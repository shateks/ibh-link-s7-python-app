import logging
import sys
from PyQt5.QtWidgets import QApplication, QWidget
from ui_gui import *
from ibhQtAdapter import *
from PyQt5.QtCore import QThread

def killnij():
    print('killnij() {}'.format(QThread.currentThreadId()))

class Okno(QWidget):

    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

w = Worker('192.168.1.15',2)
# w = Worker('127.0.0.1',2)
t = QThread()

w.moveToThread(t)
# t.started.connect(w.startingSlot)
# t.finished.connect(lambda: t.deleteLater())
# t.finished.connect(killnij)

app = QApplication(sys.argv)
widget = Okno()
widget.show()
t.start()
widget.ui.btn_start.clicked.connect(lambda: w.read_bytes('M',0,100,4))
# widget.ui.btn_start.clicked.connect(lambda: w.read_bytes('D',0,100,4))
w.read_bytes_signal.connect(lambda l: widget.ui.textEdit.append(str(l)))

widget.ui.btn_get_plc_status.clicked.connect(lambda: w.get_plc_status())
w.get_plc_status_signal.connect(lambda l: widget.ui.textEdit.append(l))

print('Main thread {}'.format(QThread.currentThreadId()))
app.exec()