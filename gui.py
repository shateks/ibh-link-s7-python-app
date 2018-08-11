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
t = QThread()

w.moveToThread(t)
# t.started.connect(w.startingSlot)
# t.finished.connect(lambda: t.deleteLater())
# t.finished.connect(killnij)

app = QApplication(sys.argv)
widget = Okno()
widget.show()
t.start()
widget.ui.btn_start.clicked.connect(lambda: w.read_bytes('D',0,100,1))
w.read_bytes_signal.connect(lambda l: widget.ui.textEdit.append(str(l)))
print('Main thread {}'.format(QThread.currentThreadId()))
app.exec()