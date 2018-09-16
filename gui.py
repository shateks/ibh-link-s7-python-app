import logging
import logging.handlers
import sys
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit
from ui_gui import *
from ibhQtAdapter import *
from PyQt5.QtCore import QThread, Qt

def killnij():
    print('killnij() {}'.format(QThread.currentThreadId()))

MEMORY_AREA_LIST = ['I - INPUT','Q - QUTPUT','M - MEMORY','DB - DATA BLOCK']

FORMAT = 'FORMAT:%(threadName)s - %(asctime)s - %(name)s - %(levelname)s - %(message)s'
formater = logging.Formatter('%(threadName)s - %(asctime)s - %(name)s - %(levelname)s - %(message)s')

console = logging.StreamHandler()
console.setLevel(logging.WARNING)

file_handler = logging.handlers.RotatingFileHandler('gui.log','a',10000,10)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formater)

logging.basicConfig(format=FORMAT,handlers=(console,file_handler))

root_logger = logging.getLogger('')
root_logger.setLevel(logging.DEBUG)

class Okno(QWidget):

    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.cb_address_area.addItems(MEMORY_AREA_LIST)
        # >>>>>>>>>>>>>>>>
        # w = Worker('192.168.1.15',2)
        self.w = Worker('127.0.0.1', 2)
        self.t = QThread()

        self.w.moveToThread(self.t)
        # t.started.connect(w.startingSlot)
        # t.finished.connect(lambda: t.deleteLater())
        # t.finished.connect(killnij)
        logHandler = QTextEdtitLoggerHandler(self)
        root_logger.addHandler(logHandler)
        # logging.basicConfig(handlers=(logHandler,file_handler),)

        self.ui.le_ip_address.setText('127.0.0.1')
        self.ui.le_ip_port.setText('1099')
        self.ui.le_mpi_address.setText('2')
        self.ui.le_variable_address.setText('100')
        self.ui.le_variable_offset.setText('0')
        self.ui.cb_address_area.setCurrentIndex(3)

        self.w.change_communication_parameters(*self.collect_communication_parameter())


        self.t.start()

        self.ui.btn_read.clicked.connect(self.read_bytes)
        # widget.ui.btn_start.clicked.connect(lambda: w.read_bytes('D',0,100,4))
        self.w.read_bytes_signal.connect(lambda l: self.ui.te_log.append(str(l)))

        self.ui.btn_write.clicked.connect(self.write_bytes)

        self.ui.btn_get_plc_status.clicked.connect(lambda: self.w.get_plc_status())
        self.w.get_plc_status_signal.connect(lambda l: self.ui.te_log.append('PLC is in {} state.'.format(l)))

        self.w.failure_signal.connect(lambda s: self.ui.te_log.append(s))

        self.ui.le_ip_address.editingFinished.connect(
            lambda: self.w.change_communication_parameters(*self.collect_communication_parameter()))
        self.ui.le_ip_port.editingFinished.connect(
            lambda: self.w.change_communication_parameters(*self.collect_communication_parameter()))
        self.ui.le_mpi_address.editingFinished.connect(
            lambda: self.w.change_communication_parameters(*self.collect_communication_parameter()))

        self.ui.btn_clear.clicked.connect(self.ui.te_log.clear)
        print('Main thread {}'.format(QThread.currentThreadId()))

    #     <<<<<<<<<<<<<<<<<<<<<<

    # @pyqtSlot()
    # def read_operation(self):
    #     self.ip_address, self.ip_port, self.mpi_address = self.collect_communication_parameter()
    #
    #     self.ui.te_log.setText(self.ip_address)

    # @pyqtSlot()
    # def get_plc_state(self):
    #     pass

    def collect_communication_parameter(self):
        return (self.ui.le_ip_address.text(), int(self.ui.le_ip_port.text()), int(self.ui.le_mpi_address.text()))

    def collect_variable_parameter(self):
        index = self.ui.cb_address_area.currentIndex()
        if index == 0:
            area = 'I'
        elif index == 1:
            area = 'Q'
        elif index == 2:
            area = 'M'
        elif index == 3:
            area = 'D'

        if area in ['I','Q','M']:
            data_numb = int(self.ui.le_variable_address.text())
            db_numb = 0
            size = int(self.ui.sb_variable_bytes_count.text())
        elif area == 'D':
            db_numb = int(self.ui.le_variable_address.text())
            data_numb = int(self.ui.le_variable_offset.text())
            size = int(self.ui.sb_variable_bytes_count.text())

        return (area, data_numb, db_numb, size)

    def read_bytes(self):
        try:
            (area, data_numb, db_numb, size) = self.collect_variable_parameter()
            self.w.read_bytes(area, data_numb, db_numb, size)
        except ValueError as e:
            self.log_error(str(e))

    def write_bytes(self):
        try:
            (area, data_numb, db_numb, size) = self.collect_variable_parameter()
            val = int(self.ui.le_variable_value.text())
            self.w.write_bytes(area, data_numb, db_numb, size, val)
        except ValueError as e:
            self.log_error(str(e))

    @pyqtSlot(str)
    def log_error(self, msg):
        self.ui.te_log.setTextColor(Qt.red)
        self.ui.te_log.append(msg)
        self.ui.te_log.setTextColor(Qt.black)


class QTextEdtitLoggerHandler(logging.Handler):

    def __init__(self, widget: Okno):
        super().__init__()
        self.setLevel(logging.INFO)
        self.widget = widget

    def emit(self, record):
        msg = self.format(record)
        self.widget.log_error(msg)


if (__name__ == '__main__' ):


    app = QApplication(sys.argv)
    widget = Okno()
    widget.show()

    app.exec()