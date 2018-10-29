from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, Qt, QModelIndex, QAbstractItemModel
from ibh_link.ibh_server import IbhLinkServer, IbhDataCollection, EventType
from ibh_link.ibh_server_model import Model

class ___model(QAbstractItemModel):

    pass


class Worker(QObject):

    def __init__(self,connector=None, model: Model=None, parent=None):
        super().__init__(parent)
        self._server = None
        self._connector = connector
        self._model = model
        self._server_response_lag = None

    @property
    def lag(self):
        return self._server_response_lag

    @lag.setter
    def lag(self,val_time):
        self._server_response_lag = val_time

    @pyqtSlot()
    def start(self, ip_address: str, ip_port: int, mpi_address: int, collection: IbhDataCollection):
        self._server = IbhLinkServer(ip_address, ip_port, mpi_address, collection, self._connector)
        self._server.lag = self._server_response_lag
        self._server.start()
        self.started.emit()

    @pyqtSlot()
    def stop(self):
        self._server.stop()
        self._server.join()
        self.stoped.emit()

    @pyqtSlot(tuple)
    def item_added(self, tup):
        """
        Only purpose of slot is redirect signal from QtNotifier, signal is emitted when item is added to
        collection of data (IbhDataCollection).
        :param tup: EventType, memory area D,M,I or Q
        :return:
        """

        type, area = tup
        root = QModelIndex()
        if type == EventType.added:
            count = self._model.rowCount(root)
            for row in range(count):
                index = self._model.index(row,0,root)
                if self._model.data(index, Qt.DisplayRole) == area:
                    self._model.rowsInserted.emit(index,0,0)
                    break
        elif type == EventType.changed:
            count = self._model.rowCount(root)
            for row in range(count):
                index = self._model.index(row, 0, root)
                if self._model.data(index, Qt.DisplayRole) == area:
                    index1 = self._model.index(0,2,index)
                    count2 = index.internalPointer().childCount()
                    index2 = self._model.index(count2-1,2,index)
                    self._dataChanged.emit(index1, index2)
                    break


    started = pyqtSignal()
    stoped = pyqtSignal()
    _dataChanged = pyqtSignal(QModelIndex,QModelIndex)
    collection_modified = pyqtSignal(str)
