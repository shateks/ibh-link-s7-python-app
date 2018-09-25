from typing import Iterable

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, Qt, QModelIndex, QAbstractItemModel
from PyQt5.Qt import QVariant
from ibhLinkServer import IbhLinkServer, IbhDataCollection, EventType
from IbhLinkServerModel import Model

class ___model(QAbstractItemModel):

    pass


class Worker(QObject):

    def __init__(self,connector=None, model: Model=None, parent=None):
        super().__init__(parent)
        self._server = None
        self._connector = connector
        self._model = model

    @pyqtSlot()
    def start(self, ip_address: str, ip_port: int, mpi_address: int, collection: IbhDataCollection):
        self._server = IbhLinkServer(ip_address, ip_port, mpi_address, collection, self._connector)
        self._server.start()
        self.started.emit()

    @pyqtSlot()
    def stop(self):
        self._server.stop()
        self._server.join()
        self.stoped.emit()

    @pyqtSlot(tuple)
    def item_added(self, tup):
    # def item_added(self, type: EventType, area: str):
        """
        Only purpose of slot is redirect signal from QtNotifier, signal is emitted when item is added to
        collection of data (IbhDataCollection).
        :param type: type of event added or changed
        :param area: memory area D,M,I or Q
        :return:
        """

        type, area = tup
        root = QModelIndex()
        if type == EventType.added:
            count = self._model.rowCount(QModelIndex())
            for row in range(count):
                index = self._model.index(row,0,root)
                if self._model.data(index, Qt.DisplayRole) == area:
                    self._model.rowsInserted.emit(index,0,0)
                    break
        elif type == EventType.changed:
            count = self._model.rowCount(QModelIndex())
            for row in range(count):
                index = self._model.index(row, 0, root)
                if self._model.data(index, Qt.DisplayRole) == area:
                    count2 = index.internalPointer().childCount()
                    index2 = self._model.index(count2-1,2,index)
                    self._dataChanged.emit(index2, index2)



    started = pyqtSignal()
    stoped = pyqtSignal()
    _dataChanged = pyqtSignal(QModelIndex,QModelIndex)
    collection_modified = pyqtSignal(str)
