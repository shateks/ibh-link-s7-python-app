from PyQt5.QtCore import QObject, QThread, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QLabel, QPushButton
import time
import string
import threading
import ibhlinkdriver
import IBHconst
from data_plc import BaseData
from collections import namedtuple
from enum import Enum
"""
Requirements:
* Fixed refresh size for reding variables.
* Avoid of directly connecting gui push buttons to driver read/write slots. This cause problems when buttons
will be clicked many times in short time. 
* To decide: If after r/w operations disconnect or stay connected.

Connecting collection of visualization variables with gui objects:
1. During loading of "qtcreators" *.ui files, all children of graphic screen will be checked for presence
'what's this' property. One plc variable can be assigned to many gui elements

Supported graphic elements:
- Qlabel
- QPushbutton, monostable
- QPushbutton with "checkable" option, as bistable button
- Qlineedit
"""
class Status(Enum):
    ready = 1
    busy = 2

class Manager(QObject):
    """
    The managing class for Worker.
    Is responsive for:
    * invoking cyclically read of memory areas
        Details:

    * sending results of reads to subscribers
    * same operations above for writes
    """
    visu_variable_type = namedtuple('visu_variable_type',['data', 'slot'])
    def __init__(self):
        """
        example of finally result of read:
        {M:{33:0x23,34:0x34,35:0x35,300:0x21,301:0x12},
        I:{10:0x00,11:0x12},
        Q:{},
        D:{100:{0:0x02,1:0xff}, 200:{0:0xff,1:0xf0,10:0xaa}}
        """

        super().__init__()
        self.visu_variable_list = []
        self.visu_variable = dict()
        self.bytes_for_readout = {'M':{}, 'I':{}, 'Q':{}, 'D':{}}
        self.m_area_list = []
        # self._grouped_read_out_list
        pass

    @staticmethod
    def divide_lists_of_address(input_list, chunk_size):
        """
        Method divides list for bytes readout, list after processing should be optimized
        to minimize count of readout.
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

    def add_subscriber(self, data_description, q_obj_refernce):
        """
        Adding subscriber for plc data readout.
        TODO: add some code for writing variables from visualization
        :param data_description: tuple(area:string,db_number:int,address:int,bit_nr:int,data_type:string)
        :param q_obj_refernce: QObject - Reference for QObject
        :return:
        """

        if isinstance(q_obj_refernce, QLabel):
            data = BaseData(*data_description)
            slot = q_obj_refernce.setText
            self.visu_variable_list.append(self.visu_variable_type(data, slot))
            # self.visu_variable_list.append((data, slot))
            self.populate_bytes_readout(data)

        elif isinstance(q_obj_refernce, QPushButton):
            pass
        pass

    def populate_bytes_readout(self, data):
        if data.area == 'D':
            if not data.db_number in self.bytes_for_readout['D'].keys():
                self.bytes_for_readout['D'][data.db_number] = {}
            for byte_address in data.occupied_bytes:
                self.bytes_for_readout['D'][data.db_number][byte_address] = None
        else:
            for byte_address in data.occupied_bytes:
                self.bytes_for_readout[data.area][byte_address] = None

    def process_readout_list(self):
        """
        Method should be called after last adding of variables for readout.
        Details of sending:
        receiver expecting "read_bytes(self, data_type, data_number, db_number, size)"
        List of tuples is needed to be prepared.
        :return:
        """
        pass

    @pyqtSlot()
    def do_work(self):
        """
        Verification of reading process:
        Check count of
        :return:
        """
        # TODO: get readout list and initialize reading
        for key,val in self.bytes_for_readout.items():

            pass
        # TODO: consume result of reading
        for elem in self.visu_variable_list:
            elem.slot('{} {}'.format(elem.data.area , time.strftime('%H:%M:%S',time.localtime())))

    ask_worker_for_readiness = pyqtSignal()

    @pyqtSlot()
    def collect_bytes(self):
        """
        When reading process is finished ?:
        Check count of asked for reading bytes and counter of received bytes, if is equal
        emit signal to driver for its status.
        :return:
        """
        pass

    # TODO: slot for receiving errors, status signals from worker
    @pyqtSlot()
    def worker_status_receiver(self):
        pass

class Worker(QObject):
    """
    The class wrapping ibhlinkdriver in a QObject type object that can be moved to a thread and used
    from the benefits of Qt signals and slots.
    The methods have practically the same arguments.
    """
    def __init__(self, ip_address, mpi_address):
        super().__init__()
        self._driver = ibhlinkdriver.ibhlinkdriver(ip_address, IBHconst.IBHLINK_PORT, mpi_address)
        self._stay_connected = False
        self._change_driver = False

    @pyqtSlot(str, int, int)
    def change_communication_parameters(self, ip_address, ip_port, mpi_address):
        if not self._driver.connected:
            self._driver.ip_address = ip_address
            self._driver.ip_port = ip_port
            self._driver.mpi_address = mpi_address
        else:
            self.failure_signal('Communication parameters cannot be changed, driver is still connected.')

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
    def read_bytes(self, data_type, data_number, db_number, size):
        """
        :param data_type: string - M, E or I, A or Q, D
        :param data_number: int - number of data
        :param db_number: int - in case of type 'D' number of DB block
        :param size: int - number of bytes to read beginning from target 'data_number'
        """
        if not self._driver.connected:
            self._driver.connect_plc()

        if self._driver.connected:
            vals = self._driver.read_vals(data_type, data_number, db_number, size)
            self.read_bytes_signal.emit(vals)
            self._driver.disconnect_plc()
            # self.read_bytes_signal.emit([1,2,3,4,5,6,7,8])


    @pyqtSlot()
    def get_plc_status(self):
        try:
            if not self._driver.connected:
                self._driver.connect_plc()

            if self._driver.connected:
                status = self._driver.plc_get_run()
                self.get_plc_status_signal.emit(status)
                self._driver.disconnect_plc()
        except ibhlinkdriver.DriverError as e:
            self.failure_signal.emit(str(e))
    # TODO: slot for writing list<int>

    # TODO: slot for reading any bit in byte

    # TODO: slot for writing any bit in byte

    # TODO: signal with read list of bytes
    failure_signal = pyqtSignal(str)
    read_bytes_signal = pyqtSignal(list)
    get_plc_status_signal = pyqtSignal(str)
    # TODO: signal with error

