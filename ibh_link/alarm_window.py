from PyQt5 import QtCore
from PyQt5.QtCore import QObject, pyqtSlot, QModelIndex
from ibh_link.data_plc import BaseData
from collections import OrderedDict

class AlarmWindowModel(QtCore.QAbstractListModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._alarms_original = dict()
        self._alarms_collection_ = OrderedDict()


    def rowCount(self, parent=None, *args, **kwargs):
        return len(self._alarms_collection_)

    def data(self, index:QModelIndex, role=None):
        if not index.isValid():
            return None
        if index.row() > self.rowCount():
            return None
        if role == QtCore.Qt.DisplayRole:
            return tuple(self._alarms_collection_.values())[index.row()]
        return None

    def define_alarm(self, data:BaseData, text:str):
        """
        Defines possible alarms to be display.
        :param data: BaseData, boolean data type only.
        :param text: str, Description to be display.
        :rtype:
        """
        # TODO: BUG definig new dictionary with "'val': False" key:
        self._alarms_original[data] = {'val': False, 'text': '{}{}{}{}'.format(text, data.area, data.address, data._bit_nr)}
        # self._alarms_collection_[data] = (self._alarms_original[data]['text'])
        # self.rowsInserted.emit(QModelIndex(), self.rowCount()-1, self.rowCount())
        # self.dataChanged.emit(QModelIndex())

    def child(self, row):
        """
        Returns element from collection
        :param row:
        :return:
        """
        try:
            return list(self._alarms_collection_.values())[row]
        except IndexError:
            return None

    def index(self, row, col=0, parent=QModelIndex(), *args, **kwargs):
        try:
            if not parent.isValid():
                parent_ref = self._alarms_collection_
            else:
                parent_ref = parent.internalPointer()
            child_item = list(parent_ref.values())[row]
            # child_item = self.child(row)
            if child_item:
                return self.createIndex(row, col, child_item)
            else:
                return QtCore.QModelIndex()
        except IndexError:
            return QtCore.QModelIndex()

    @pyqtSlot(BaseData, bool)
    def alarm_state(self, data:BaseData, val:bool):
        if data in self._alarms_original.keys():
            # val = bool(val)
            previous = self._alarms_original[data]['val']
            self._alarms_original[data]['val'] = val
            if val != previous:
                if val:
                    self._alarms_collection_[data] = (self._alarms_original[data]['text'])
                    self.rowsInserted.emit(QModelIndex(), self.rowCount(), self.rowCount())
                else:
                    try:
                        row_number = list(self._alarms_collection_.keys()).index(data)
                        ref = self._alarms_collection_[data]
                        self._alarms_collection_.pop(data)
                        # self.rowsRemoved.emit(self.createIndex(row_number, 0, ref), row_number, row_number+1)
                        self.modelReset.emit()
                    except KeyError:
                        pass

