import random
import sys

from ibhServerGui import *
from PyQt5.QtCore import QObject, QThread, pyqtSlot, pyqtSignal, Qt, QModelIndex
from PyQt5.QtWidgets import QWidget, QApplication
from IbhServerData import *
from IbhLinkServerModel import Model, ChangeByteDelegate, ProxySortModel
from ibhServerQtAdapter import Worker
import faulthandler
import PyQt5
from safe_connector import SafeConnector

f1 = open("crash.txt",'w')
faulthandler.enable(file=f1)


class IbhLinkServerGui(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.ui.leIpAddress.setText('127.0.0.1')
        self.ui.lePort.setText('1099')
        self.ui.leMpiAddress.setText('2')

        self.connector = SafeConnector()
        self._collection = IbhDataCollection()

        # populate_example_collection(self._collection)

        self.model = Model(self._collection)
        self.proxy_model = ProxySortModel()
        self.proxy_model.setSourceModel(self.model)
        self.ui.treeView.setModel(self.proxy_model)
        # self.ui.treeView.setModel(self.model)
        self.edit_delegate = ChangeByteDelegate(self.ui.treeView)
        self.ui.treeView.setItemDelegateForColumn(2, self.edit_delegate)
        self.ui.treeView.setSortingEnabled(True)
        self.ui.ckbAddWhenMissing.stateChanged.connect(self.cb_add_when_missing_handler)
        self.ui.ckbAddWhenMissing.setChecked(True)

        self.thread = QThread()
        self.worker = Worker(self.connector, self.model)
        self.worker.lag = 0.01
        self.worker.moveToThread(self.thread)

        self.connector.signal.connect(self.worker.item_added)

        self.ui.btnStart.clicked.connect(self.start_btn_handler)
        self.ui.btnStop.clicked.connect(self.stop_btn_handler)
        self.worker.started.connect(self.started_handler)
        self.worker.stoped.connect(self.stoped_handler)
        self.thread.start()
        self.stoped_handler()

        self.worker._dataChanged.connect(self.data_changed_proxy)

    @pyqtSlot()
    def test_function(self):
        self.ui.treeView.repaint()
        # self.ui.treeView.header().headerDataChanged(Qt.Vertical, 0, 3)
        self.ui.treeView.update(QtCore.QModelIndex())

    @pyqtSlot()
    def start_btn_handler(self):
        ip_address = self.ui.leIpAddress.text()
        ip_port = int(self.ui.lePort.text())
        mpi_address = int(self.ui.leMpiAddress.text())

        self.worker.start(ip_address, ip_port, mpi_address, self._collection)

    @pyqtSlot()
    def stop_btn_handler(self):
        self.worker.stop()

    @pyqtSlot()
    def started_handler(self):
        self.ui.btnStart.setDisabled(True)
        self.ui.btnStop.setEnabled(True)
    @pyqtSlot()
    def stoped_handler(self):
        self.ui.btnStart.setEnabled(True)
        self.ui.btnStop.setDisabled(True)

    @pyqtSlot(int)
    def cb_add_when_missing_handler(self, state):
        if state == PyQt5.QtCore.Qt.Checked:
            self._collection.add_if_not_exist(True)
        else:
            self._collection.add_if_not_exist(False)

    @pyqtSlot(QModelIndex,QModelIndex)
    def data_changed_proxy(self, index1, index2):
        self.model.dataChanged.emit(index1,index2)

def populate_example_collection(collection:IbhDataCollection):
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    self = IbhLinkServerGui()


    self.show()
    app.exec()


