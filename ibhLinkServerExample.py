import random
import sys

from ibhServerGui import *
from PyQt5.QtCore import QObject, QThread, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QWidget, QApplication
from IbhServerData import *
from IbhLinkServerModel import Model, ChangeByteDelegate, ProxySortModel
from ibhServerQtAdapter import Worker
import faulthandler

f1 = open("crash.txt",'w')
faulthandler.enable(file=f1)


class IbhLinkServerGui(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

app = QApplication(sys.argv)
widget = IbhLinkServerGui()
collection = IbhDataCollection()
collection.append(data_item('M',10,0),0xff)
collection.append(data_item('M',10,0),0x10)
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

collection.add_if_not_exist(1)
collection.get(data_item('M',10,0))
collection.get(data_item('D',11,0))
collection.set(data_item('M',10,0),77)
collection.set(data_item('M',11,0),17)
collection.set(data_item('M',12,0),27)
collection.set(data_item('M',13,0),37)
collection.set(data_item('D',10,0),17)
collection.set(data_item('D',13,0),33)

for i in range(0,100):
    collection.set(data_item('D', 100, random.choice(range(200))), random.choice(range(255)))

model = Model(collection)
proxy_model = ProxySortModel()
proxy_model.setSourceModel(model)
widget.ui.treeView.setModel(proxy_model)
edit_delegate = ChangeByteDelegate(widget.ui.treeView)
widget.ui.treeView.setItemDelegateForColumn(2,edit_delegate)
widget.ui.treeView.setSortingEnabled(True)
widget.ui.ckbAddWhenMissing.stateChanged.connect(lambda val: collection.add_if_not_exist(val))

thread = QThread()
worker = Worker()
worker.moveToThread(thread)
widget.ui.btnStart.clicked.connect(worker.start)
widget.ui.btnStop.clicked.connect(worker.stop)
thread.start()

widget.show()
app.exec()


