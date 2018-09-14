import logging
import sys
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit
from ui_gui import *
from ibhQtAdapter import *
from PyQt5.QtCore import QThread, Qt

def killnij():
    print('killnij() {}'.format(QThread.currentThreadId()))

MEMORY_AREA_LIST = ['I - INPUT','Q - QUTPUT','M - MEMORY','DB - DATA BLOCK']



class Okno(QWidget):

    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.cb_address_area.addItems(MEMORY_AREA_LIST)

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
            db_numb = int(self.ui.le_variable_address)
            data_numb = int(self.ui.le_variable_offset)
            size = int(self.ui.sb_variable_bytes_count)

        return (area, data_numb, db_numb, size)

class QTextEdtitLoggerHandler(logging.Handler):

    def __init__(self, widget: QTextEdit):
        super().__init__()
        self.widget = widget

    def emit(self, record):
        msg = self.format(record)
        self.widget.setTextColor(Qt.red)
        self.widget.append(msg)
        self.widget.setTextColor(Qt.black)


if (__name__ == '__main__' ):
    # w = Worker('192.168.1.15',2)
    w = Worker('127.0.0.1',2)
    t = QThread()

    w.moveToThread(t)
    # t.started.connect(w.startingSlot)
    # t.finished.connect(lambda: t.deleteLater())
    # t.finished.connect(killnij)

    app = QApplication(sys.argv)
    widget = Okno()

    logHandler = QTextEdtitLoggerHandler(widget.ui.te_log)
    logging.basicConfig(handlers=(logHandler,))

    widget.ui.le_ip_address.setText('127.0.0.1')
    widget.ui.le_ip_port.setText('1099')
    widget.ui.le_mpi_address.setText('2')

    w.change_communication_parameters(*widget.collect_communication_parameter())

    widget.show()
    t.start()

    widget.ui.btn_read.clicked.connect(lambda : w.read_bytes(widget.collect_variable_parameter()))
    # widget.ui.btn_start.clicked.connect(lambda: w.read_bytes('D',0,100,4))
    w.read_bytes_signal.connect(lambda l: widget.ui.te_log.append(str(l)))

    widget.ui.btn_get_plc_status.clicked.connect(lambda: w.get_plc_status())
    w.get_plc_status_signal.connect(lambda l: widget.ui.te_log.append('PLC is in {} state.'.format(l)))

    w.failure_signal.connect(lambda s: widget.ui.te_log.append(s))

    widget.ui.le_ip_address.editingFinished.connect(lambda : w.change_communication_parameters(*widget.collect_communication_parameter()))

    widget.ui.btn_clear.clicked.connect(widget.ui.te_log.clear)
    print('Main thread {}'.format(QThread.currentThreadId()))
    app.exec()