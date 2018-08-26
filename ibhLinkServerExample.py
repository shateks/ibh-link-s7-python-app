import sys

from ibhServerGui import *
from PyQt5.QtCore import QObject, QThread, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QWidget, QApplication
from IbhServerData import *
from IbhLinkServerModel import Model



class IbhLinkServerGui(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

app = QApplication(sys.argv)
widget = IbhLinkServerGui()
collection = IbhDataCollection()
collection.append(data_item('M',10,0),0xff)
collection.append(data_item('M',10,0),0xff)
collection.append(data_item('D',10,0),0xff)
collection.append(data_item('D',10,0),0x2)
collection.append(data_item('D',10,1),0x1f)
collection.append(data_item('D',100,0),0x1)
collection.append(data_item('D',100,0),0xee)
collection.append(data_item('D',100,1),0x1f)
collection.append(data_item('M',10,0),0x0)
collection.append(data_item('M',10,2),0x2)
collection.append(data_item('M',10,4),0x4)
collection.append(data_item('M',10,6),0x6)
collection.append(data_item('M',1,0),0x10)
collection.append(data_item('M',2,0),0xff)
collection.append(data_item('I',1,0),0xf1)
collection.append(data_item('I',0,0),0x11)

model = Model(collection)
widget.ui.treeView.setModel(model)

widget.show()
app.exec()


