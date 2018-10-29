import logging
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QLocale
from PyQt5.QtGui import QDoubleValidator, QValidator
from PyQt5.QtWidgets import QLabel, QPushButton, QSlider, QDial, QProgressBar, QLineEdit, QWidget
import time
from ibh_link import ibh_const, ibh_client
from ibh_link.data_plc import BaseData, WritableBitData, WritableNumericData, Action, DataType
from collections import namedtuple, deque
from enum import Enum
from ibh_link.utils import variable_full_description

logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)

class Status(Enum):
    ready = 1
    busy = 2
    no_connection = 3
    succeed = 4


read_deque = deque()
"""
Prepared tuples ready for consuming by driver,
collection of elements "memory_chunk_type"
"""

result_read_deque = deque()
"""
Returning list of ints writen by driver,
collection of elements "memory_chunk_type, list(int)"
"""

write_request_deque = deque()
"""
Not yet prepared for driver write operations,
collection of elements "visu_variable, bool|int|float"
"""

write_deque = deque()
"""
Prepared tuples for write for consuming by driver.
Every tuple is single variable: one, two or four byte long.
"""

memory_chunk_type = namedtuple('memory_chunk_type',['area', 'address', 'offset', 'size'])

SUPPORTED_WIDGETS = ['QPushButton', 'QLabel', 'QSlider', 'QDial', 'QProgressBar', 'QLineEdit']

def find_supported_widgets(widget):
    w_list = widget.findChildren(QWidget)
    for w in w_list:
        if w.metaObject().className() in SUPPORTED_WIDGETS:
            yield w

class DoubleWordValidator(QValidator):

    def __init__(self, bottom:int, top:int, parent=None):
        super().__init__(parent)
        self._bottom = int(bottom)
        self._top = int(top)

    def validate(self, p_str, p_int):
        try:
            _val = int(p_str)
            if _val > self._top or _val < self._bottom:
                return (QValidator.Invalid, p_str, p_int)
            else:
                return (QValidator.Acceptable, p_str, p_int)
        except:
            return (QValidator.Invalid, p_str, p_int)


class Manager(QObject):
    """
    The managing class for Worker.
    Is responsive for:
    * invoking cyclically read of memory areas
        Details:

    * sending results of reads to subscribers
    * same operations above for writes
    """
    visu_object = namedtuple('visu_object', ['data', 'slot'])
    def __init__(self, worker: "Worker"):

        super().__init__()
        self._visu_variable_list = []
        self._visu_variable = dict()
        self._templet_bytes_for_readout = {'M':{}, 'I':{}, 'Q':{}, 'D':{}}
        self._processed_readout_list = []
        self._socket_error_flag = False

        worker.queued_read_out_finished.connect(self.collect_bytes_and_send_values)
        self.start_packet_communication.connect(worker.queued_operations)
        self.ask_for_plc_state.connect(worker.get_plc_status)
        worker.plc_state_signal.connect(self.plc_state_receiver)
        worker.status_signal.connect(self.socket_connection_error)

        self._time_memory = time.time()

    @staticmethod
    def divide_lists_of_address(input_list, chunk_size):
        """
        Method divides list for bytes readout, list after processing should be optimized
        to minimize count of readout. Total length of lists can be greater then input_list.
        :param input_list: list - with no duplicates unsorted or sorted
        :param chunk_size: int - size of byte block
        :return: list of lists - divided list
        """
        _list = sorted(input_list)
        _result = []
        _partial_result = []

        _div_point = _list[0] + chunk_size - 1
        _prev_element = _list[0]
        _div_begin = _list[0]
        for element in _list:
            if element > _div_point:
                _partial_result = [x for x in range(_div_begin, _prev_element + 1)]
                _div_point = element + chunk_size
                _result.append(_partial_result)
                _div_begin = element
            _prev_element = element
        _partial_result = [x for x in range(_div_begin, _prev_element + 1)]
        _result.append(_partial_result)
        return _result

    def add_subscriber(self, full_description: variable_full_description, q_obj_ref):
        """
        Adding subscriber for plc data readout.
        :param full_description: variable_full_description
        :param q_obj_ref: QObject - Reference for QObject
        :return:
        """
        read_subscriber_added_flag = False
        write_trigger_added_flag = False
        if isinstance(q_obj_ref, QLabel):
            data = BaseData(full_description)
            if q_obj_ref.pixmap() is not None:
                slot = lambda val: q_obj_ref.setEnabled(bool(val))
            else:
                slot = lambda val: q_obj_ref.setText(str(val))
            self.populate_bytes_readout(data)
            self._visu_variable_list.append(self.visu_object(data, slot))
            read_subscriber_added_flag = True
        elif isinstance(q_obj_ref, QPushButton):
            if full_description.action in (Action.TOGGLE, Action.RESET, Action.SET):
                data = WritableBitData(full_description)
                q_obj_ref.clicked.connect(lambda: self.populate_write_request_by_bit_variable(data))
                write_trigger_added_flag = True
            else:
                data = BaseData(full_description)
            if q_obj_ref.isCheckable():
                slot = lambda val: self.slot_handling_qpushbutton(q_obj_ref, data, val)
                self.populate_bytes_readout(data)
                self._visu_variable_list.append(self.visu_object(data, slot))
                read_subscriber_added_flag = True
        elif isinstance(q_obj_ref, QSlider) or isinstance(q_obj_ref, QDial):
            data = WritableNumericData(full_description)
            if full_description.action == Action.WRITE:
                q_obj_ref.setTracking(False)
                q_obj_ref.valueChanged.connect(lambda val: self.populate_write_request_by_int_variable(data, val))
                write_trigger_added_flag = True
            slot = lambda val: self.slot_handling_qslider(q_obj_ref, data, val)
            self.populate_bytes_readout(data)
            self._visu_variable_list.append(self.visu_object(data, slot))
            read_subscriber_added_flag = True
        elif isinstance(q_obj_ref, QProgressBar):
            slot = lambda val: q_obj_ref.setValue(int(val))
            data = BaseData(full_description)
            self.populate_bytes_readout(data)
            self._visu_variable_list.append(self.visu_object(data, slot))
            read_subscriber_added_flag = True
        elif isinstance(q_obj_ref, QLineEdit):
            if full_description.action == Action.WRITE:
                data = WritableNumericData(full_description)
                if data.data_type == DataType.REAL:
                    validator = QDoubleValidator(*data.value_range, 24)
                    locale = QLocale(QLocale.C)
                    locale.setNumberOptions(QLocale.RejectGroupSeparator)
                    validator.setLocale(locale)
                    q_obj_ref.editingFinished.connect(lambda: self.populate_write_request_by_int_variable(data, float(q_obj_ref.text())))
                else:
                    validator = DoubleWordValidator(*data.value_range)
                    q_obj_ref.editingFinished.connect(lambda: self.populate_write_request_by_int_variable(data, int(q_obj_ref.text())))
                q_obj_ref.setValidator(validator)
                write_trigger_added_flag = True
            else:
                data = BaseData(full_description)
                q_obj_ref.setReadOnly(True)
            slot = lambda val: self.slot_handling_qlineedit(q_obj_ref, data, val)
            self.populate_bytes_readout(data)
            self._visu_variable_list.append(self.visu_object(data, slot))
            read_subscriber_added_flag = True        
        if not(read_subscriber_added_flag or write_trigger_added_flag):
            logger.warning('No supported widget, or operation for: ' + q_obj_ref.objectName())
        else:
            if read_subscriber_added_flag:
                logger.debug('Subscriber added for reading: ' + q_obj_ref.objectName())
            if write_trigger_added_flag:
                logger.debug('Added trigger for write operation: ' + q_obj_ref.objectName())

        
    def slot_handling_qpushbutton(self, ref:QPushButton, data, val):
        if ref.isDown():
            return
        else:
            if isinstance(data, WritableBitData) and data.request_sent:
                return
            ref.setChecked(bool(val))

    def slot_handling_qslider(self, ref:QSlider, data, val):
        if ref.isSliderDown():
            return
        else:
            if not data.request_sent:
                ref.blockSignals(True)
                ref.setValue(int(val))
                ref.blockSignals(False)

    def slot_handling_qlineedit(self, ref:QLineEdit, data, val):
        if isinstance(data, WritableNumericData):
            if ref.hasFocus():
                return
            else:
                if not data.request_sent:
                    ref.setText(str(val))
        else:
            ref.setText(str(val))

    def populate_bytes_readout(self, data: BaseData):
        if data.area == 'D':
            if not data.address in self._templet_bytes_for_readout['D'].keys():
                self._templet_bytes_for_readout['D'][data.address] = {}
            for byte_address in data.occupied_bytes:
                self._templet_bytes_for_readout['D'][data.address][byte_address] = None
        else:
            for byte_address in data.occupied_bytes:
                self._templet_bytes_for_readout[data.area][byte_address] = None

    @pyqtSlot(BaseData)
    def populate_write_request_by_bit_variable(self, data):
        """
        Used for bit like actions: SET, RESET, TOGGLE
        :param data: BaseData
        :return:
        """
        for m, d, v in write_request_deque:
            if data == d:
                return
        memory_chunk = None
        data.request_sent = True
        if data.area == 'D':
            memory_chunk = memory_chunk_type('D', data.address, data.offset, 1)
        elif data.area in ['M','I','Q']:
            memory_chunk = memory_chunk_type(data.area, data.address, 0, 1)
        write_request_deque.append((memory_chunk, data, None))


    @pyqtSlot(WritableNumericData, int)
    def populate_write_request_by_int_variable(self, data: WritableNumericData, val: int):
        temp_index = None
        for i, (m, d, v) in enumerate(write_request_deque):
            if data == d:
                temp_index = i
                break
        if temp_index:
            del(write_request_deque[temp_index])
        memory_chunk = None
        data.request_sent = True
        if data.area == 'D':
            memory_chunk = memory_chunk_type('D', data.address, data.offset, data.size)
        elif data.area in ['M', 'I', 'Q']:
            memory_chunk = memory_chunk_type(data.area, data.address, 0, data.size)
        write_request_deque.append((memory_chunk, data, val))

    def optimize_readout_list(self):
        """
        The main role of method is to minimize count of readings, through group single
        readings in memory block readings.
        Method should be called after last adding of variables for readout.
        Details of sending:
        driver expecting "read_bytes(self, data_type, data_address, offset, size)"
        List of tuples is needed to be prepared.
        :return:
        """
        _m_list = list(self._templet_bytes_for_readout['M'].keys())
        _i_list = list(self._templet_bytes_for_readout['I'].keys())
        _q_list = list(self._templet_bytes_for_readout['Q'].keys())
        _d_list = dict()
        for k,v in self._templet_bytes_for_readout['D'].items():
            _d_list[k] = list(v.keys())

        if len(_m_list):
            for l in self.divide_lists_of_address(_m_list, ibh_const.IBHLINK_READ_MAX):
                self._processed_readout_list.append(memory_chunk_type('M', l[0], 0, len(l)))

        if len(_i_list):
            for l in self.divide_lists_of_address(_i_list, ibh_const.IBHLINK_READ_MAX):
                self._processed_readout_list.append(memory_chunk_type('I', l[0], 0, len(l)))

        if len(_q_list):
            for l in self.divide_lists_of_address(_q_list, ibh_const.IBHLINK_READ_MAX):
                self._processed_readout_list.append(memory_chunk_type('Q', l[0], 0, len(l)))

        for k,v in _d_list.items():
            if len(v):
                for l in self.divide_lists_of_address(v, ibh_const.IBHLINK_READ_MAX):
                    self._processed_readout_list.append(memory_chunk_type('D', k, l[0], len(l)))

    @pyqtSlot()
    def do_work(self):
        """
        """
        if self._socket_error_flag:
            self.communication_status.emit(Status.no_connection)
            read_deque.clear()
            self._socket_error_flag = False
        if len(read_deque) == 0:
            for item in self._processed_readout_list:
                read_deque.append(item)
            self.ask_for_plc_state.emit()
            self.start_packet_communication.emit()

    @pyqtSlot()
    def collect_bytes_and_send_values(self):
        """
        When reading process is finished ?:
        Check count of asked for reading bytes and counter of received bytes, if is equal
        emit signal to driver for its status.
        :return:
        """
        _bytes_for_readout_ = self._templet_bytes_for_readout.copy()
        while True:
            try:
                (chunk, vals) = result_read_deque.popleft()
                for i,v in enumerate(vals):
                    try:
                        if chunk.area == 'D':
                            _bytes_for_readout_[chunk.area][chunk.address][chunk.offset + i] = vals[i]
                        else:
                            _bytes_for_readout_[chunk.area][chunk.address + i] = vals[i]
                    except KeyError:
                        pass
            except IndexError:
                break

        for item in self._visu_variable_list:
            temp_list = []
            if item.data.area == 'D':
                for byte_number in item.data.occupied_bytes:
                    temp_byte = _bytes_for_readout_[item.data.area][item.data.address][byte_number]
                    if temp_byte is not None:
                        temp_list.append(temp_byte)
                    else:
                        item.slot(False)
                        break
                else:
                    var_interpretation = item.data._plc_to_visu_conv(temp_list)
                    item.slot(str(var_interpretation))
            else:
                for byte_number in item.data.occupied_bytes:
                    temp_byte = _bytes_for_readout_[item.data.area][byte_number]
                    if temp_byte is not None:
                        temp_list.append(temp_byte)
                    else:
                        item.slot(False)
                        break
                else:
                    var_interpretation = item.data._plc_to_visu_conv(temp_list)
                    item.slot(var_interpretation)
        print(time.time() - self._time_memory)
        self._time_memory = time.time()

        self.communication_status.emit(Status.succeed)

    # TODO: slot for receiving errors, status signals from worker
    @pyqtSlot(Status)
    def worker_status_receiver(self,status):
        pass

    @pyqtSlot(str)
    def plc_state_receiver(self, state):
        self.plc_state_signal.emit(state)

    @pyqtSlot()
    def socket_connection_error(self):
        self._socket_error_flag = True

    start_packet_communication = pyqtSignal()
    ask_for_plc_state = pyqtSignal()
    plc_state_signal = pyqtSignal(str)
    communication_status = pyqtSignal(Status)
    variable_registred = pyqtSignal(variable_full_description,)


class Worker(QObject):
    """
    The class wrapping ibhlinkdriver in a QObject type object that can be moved to a thread and used
    from the benefits of Qt signals and slots.
    The methods have practically the same arguments.
    """
    def __init__(self, ip_address, mpi_address):
        super().__init__()
        self._driver = ibh_client.IbhLinkDriver(ip_address, ibh_const.IBHLINK_PORT, mpi_address)
        self._driver.timeout = 0
        self._stay_connected = False
        self._change_driver = False

    @pyqtSlot(str, int, int)
    def change_communication_parameters(self, ip_address, ip_port, mpi_address):
        if not self._driver.connected:
            self._driver.ip_address = ip_address
            self._driver.ip_port = ip_port
            self._driver.mpi_address = mpi_address
        else:
            self.failure_signal.emit('Communication parameters cannot be changed, driver is still connected.')

    @property
    def stay_connected(self):
        """
        Return setting: if driver should disconnect after every read/wirte operation?
        :return: Bool
        """
        return self._stay_connected

    @stay_connected.setter
    def stay_connected(self, val):
        """
        Sets mode of driver: True - driver stays connected after every read/wirte operation
        False - driver disconnects after every read/wirte operation
        :param val: Bool
        """
        self._stay_connected = bool(val)

    @pyqtSlot(str, int, int, int)
    def read_bytes(self, data_type, data_address, offset, size) -> list:
        """
        :param data_type: string - M, E or I, A or Q, D
        :param data_address: int - number of data
        :param offset: int - in case of type 'D' number of DB block
        :param size: int - number of bytes to read beginning from target 'data_number'
        :return: list - list of bytes TODO: check return type
        """
        vals = []
        try:
            if not self._driver.connected:
                self._driver.connect_plc()
            if self._driver.connected:
                vals = self._driver.read_vals(data_type, data_address, offset, size)
                if vals:
                    self.read_bytes_signal.emit(vals)
        except (ConnectionError, ibh_client.SocketUnexpectedDisconnected) as e:
            logger.error(str(e))
            self._driver.drop_connection()
            raise e
        except ibh_client.DriverError as e:
            logger.error(str(e))
            raise e
        if not self.stay_connected:
            self._driver.disconnect_plc()
        return vals

    @pyqtSlot(str, int, int, int, bytes)
    def write_bytes(self, data_type, data_address, offset, size, val):
        """
        :param data_type: string - M, E or I, A or Q, D
        :param data_address: int - number of data
        :param offset: int - in case of type 'D' number of DB block
        :param size: int - number of bytes to read beginning from target 'data_number'
        :param val: bytes - bytes to be writen
        """
        try:
            if not self._driver.connected:
                self._driver.connect_plc()
            if self._driver.connected:
                self._driver.write_vals(data_type, data_address, offset, size, val)
                self.write_bytes_signal.emit()
        except (ConnectionError, ibh_client.SocketUnexpectedDisconnected) as e:
            logger.error(str(e))
            self._driver.drop_connection()
            raise e
        except ibh_client.DriverError as e:
            logger.error(str(e))
            raise e
        finally:
            if not self.stay_connected:
                self._driver.disconnect_plc()

    @pyqtSlot()
    def get_plc_status(self):
        try:
            if not self._driver.connected:
                self._driver.connect_plc()
            if self._driver.connected:
                status = self._driver.plc_get_run()
                self.plc_state_signal.emit(status)
            else:
                self.status_signal.emit(Status.no_connection)
        except (ConnectionError, ibh_client.SocketUnexpectedDisconnected) as e:
            logger.error(str(e))
            self._driver.drop_connection()
            # raise e
        except ibh_client.DriverError as e:
            logger.error(str(e))
            # raise e
        finally:
            if not self.stay_connected:
                self._driver.disconnect_plc()

    @pyqtSlot()
    def queued_operations(self):
        if len(write_request_deque):
            self.queued_write_in()
        if len(read_deque):
            self.queued_read_out()

    def queued_read_out(self):
        try:
            while True:
                try:
                    chunk = read_deque.popleft()
                    vals = self.read_bytes(chunk.area, chunk.address, chunk.offset, chunk.size)
                    result_read_deque.append((chunk, vals))
                except IndexError:
                    break
            self.queued_read_out_finished.emit()
        except (ConnectionError, ibh_client.DriverError):
            self.status_signal.emit(Status.no_connection)

    def queued_write_in(self):
        try:
            while True:
                try:
                    chunk, data, val = write_request_deque.popleft()
                    value_list = self.read_bytes(chunk.area, chunk.address, chunk.offset, chunk.size)
                    if type(data) is WritableBitData:
                        if data.action == Action.TOGGLE:
                            logic_val = data.bytes_list_to_variable(value_list)
                            if logic_val == True:
                                result_list = data.variable_to_bytes(value_list, False)
                            else:
                                result_list = data.variable_to_bytes(value_list, True)
                        elif data.action == Action.SET:
                            result_list = data.variable_to_bytes(value_list, True)
                        elif data.action == Action.RESET:
                            result_list = data.variable_to_bytes(value_list, False)
                        self.write_bytes(chunk.area, chunk.address, chunk.offset, chunk.size, result_list)
                    elif type(data) is WritableNumericData:
                        result_list = data.variable_to_bytes(val)
                        self.write_bytes(chunk.area, chunk.address, chunk.offset, chunk.size, result_list)
                except IndexError:
                    break
            self.queued_write_in_finished.emit()
        except (ConnectionError, ibh_client.DriverError):
            self.status_signal.emit(Status.no_connection)

    failure_signal = pyqtSignal(str)
    status_signal = pyqtSignal(Status)
    read_bytes_signal = pyqtSignal(list)
    write_bytes_signal = pyqtSignal()
    plc_state_signal = pyqtSignal(str)
    queued_read_out_finished = pyqtSignal()
    queued_write_in_finished = pyqtSignal()
