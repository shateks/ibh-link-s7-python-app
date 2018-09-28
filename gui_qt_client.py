import logging.handlers
import sys, os
from PyQt5.QtWidgets import QApplication, QWidget
from ui_gui_client import *
from ibhQtAdapter import *
from PyQt5.QtCore import QThread, Qt

MEMORY_AREA_LIST = ['I - INPUT','Q - QUTPUT','M - MEMORY','DB - DATA BLOCK']

FORMAT = 'FORMAT:%(threadName)s - %(asctime)s - %(name)s - %(levelname)s - %(message)s'
formater = logging.Formatter('%(threadName)s - %(asctime)s - %(name)s - %(levelname)s - %(message)s')

console = logging.StreamHandler()
console.setLevel(logging.WARNING)
os.makedirs(name=os.path.abspath('logs'), exist_ok=True)
file_handler = logging.handlers.RotatingFileHandler('logs/gui.log','a',100000,10)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formater)

logging.basicConfig(format=FORMAT,handlers=(console,file_handler))

root_logger = logging.getLogger('')
root_logger.setLevel(logging.DEBUG)

class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.cb_address_area.addItems(MEMORY_AREA_LIST)

        self._worker = Worker('127.0.0.1', 2)
        self._thread = QThread()
        self._worker.moveToThread(self._thread)

        log_handler = QTextEdtitLoggerHandler(self)
        root_logger.addHandler(log_handler)

        self.ui.le_ip_address.setText('127.0.0.1')
        self.ui.le_ip_port.setText('1099')
        self.ui.le_mpi_address.setText('2')
        self.ui.le_variable_address.setText('100')
        self.ui.le_variable_offset.setText('0')
        self.ui.cb_address_area.setCurrentIndex(3)

        self._worker.change_communication_parameters(*self.collect_communication_parameter())

        self._thread.start()

        self.ui.btn_read.clicked.connect(self.read_bytes)
        self._worker.read_bytes_signal.connect(lambda l: self.ui.te_log.append(str(l)))

        self.ui.btn_write.clicked.connect(self.write_bytes)

        self.ui.btn_get_plc_status.clicked.connect(lambda: self._worker.get_plc_status())
        self._worker.get_plc_status_signal.connect(lambda l: self.ui.te_log.append('PLC is in {} state.'.format(l)))

        self._worker.failure_signal.connect(lambda s: self.ui.te_log.append(s))

        self.ui.le_ip_address.editingFinished.connect(
            lambda: self._worker.change_communication_parameters(*self.collect_communication_parameter()))
        self.ui.le_ip_port.editingFinished.connect(
            lambda: self._worker.change_communication_parameters(*self.collect_communication_parameter()))
        self.ui.le_mpi_address.editingFinished.connect(
            lambda: self._worker.change_communication_parameters(*self.collect_communication_parameter()))

        self.ui.btn_clear.clicked.connect(self.ui.te_log.clear)


    def collect_communication_parameter(self):
        return (self.ui.le_ip_address.text(), int(self.ui.le_ip_port.text()), int(self.ui.le_mpi_address.text()))

    def collect_variable_parameter(self):
        index = self.ui.cb_address_area.currentIndex()
        area = MEMORY_AREA_LIST[index][0]

        if area in ['I','Q','M']:
            address = int(self.ui.le_variable_address.text())
            offset = 0
            size = int(self.ui.sb_variable_bytes_count.text())
        elif area == 'D':
            address = int(self.ui.le_variable_address.text())
            offset = int(self.ui.le_variable_offset.text())
            size = int(self.ui.sb_variable_bytes_count.text())

        return (area, address, offset, size)

    def read_bytes(self):
        try:
            (area, address, offset, size) = self.collect_variable_parameter()
            self._worker.read_bytes(area, address, offset, size)
        except ValueError as e:
            self.log_error(str(e))

    def write_bytes(self):
        try:
            (area, address, offset, size) = self.collect_variable_parameter()
            val = int(self.ui.le_variable_value.text())
            self._worker.write_bytes(area, address, offset, size, val)
        except ValueError as e:
            self.log_error(str(e))

    @pyqtSlot(str)
    def log_error(self, msg):
        self.ui.te_log.setTextColor(Qt.red)
        self.ui.te_log.append(msg)
        self.ui.te_log.setTextColor(Qt.black)


class QTextEdtitLoggerHandler(logging.Handler):

    def __init__(self, widget: MainWindow):
        super().__init__()
        self.setLevel(logging.INFO)
        self.widget = widget

    def emit(self, record):
        msg = self.format(record)
        self.widget.log_error(msg)


if (__name__ == '__main__' ):


    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()

    app.exec()