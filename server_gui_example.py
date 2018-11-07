import sys
import ibh_link.ibh_const as ibh
from collections import OrderedDict
from ui_ibh_server import *
from PyQt5.QtCore import QObject, QThread, pyqtSlot, QModelIndex
from PyQt5.QtWidgets import QWidget, QApplication
from ibh_link.ibh_server_data import *
from ibh_link.ibh_server_model import Model, ChangeByteDelegate, ProxySortModel
from ibh_link.ibh_server_qt_adapter import Worker
import faulthandler
import PyQt5
from ibh_link.safe_connector import SafeConnector

f1 = open("crash_server_gui.txt",'w')
faulthandler.enable(file=f1)

PLC_STATE = OrderedDict({ibh.OP_STATUS_STOP:'STOP', ibh.OP_STATUS_START:'START', ibh.OP_STATUS_RUN:'RUN',
                         ibh.OP_STATUS_UNKNOWN:'UNKNOWN'})

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

        self.model = Model(self._collection)
        self.proxy_model = ProxySortModel()
        self.proxy_model.setSourceModel(self.model)
        self.ui.treeView.setModel(self.proxy_model)
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

        self.ui.combo_plc_state.addItems(PLC_STATE.values())
        self.ui.combo_plc_state.currentIndexChanged.connect(self.combo_plc_changed_handler)

    @pyqtSlot()
    def test_function(self):
        self.ui.treeView.repaint()
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

    @pyqtSlot(int)
    def combo_plc_changed_handler(self, index):
        self._collection.plc_state = index

    @pyqtSlot(QModelIndex,QModelIndex)
    def data_changed_proxy(self, index1, index2):
        self.model.dataChanged.emit(index1,index2)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    self = IbhLinkServerGui()
    self.show()
    app.exec()


