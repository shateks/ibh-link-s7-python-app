from PyQt5 import QtCore
from PyQt5.QtCore import QObject, pyqtSlot, QModelIndex
from ibh_link.data_plc import BaseData

class AlarmWindowModel(QtCore.QAbstractListModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._alarms_ = dict()
        self._alarms_list_ = list()


    def rowCount(self, parent=None, *args, **kwargs):
        return len(self._alarms_list_)

    def data(self, index:QModelIndex, role=None):
        if not index.isValid():
            return None
        if index.row() > self.rowCount():
            return None
        if role == QtCore.Qt.DisplayRole:
            return self._alarms_list_[index.row()]
        return None

    def define_alarm(self, data:BaseData, text:str):
        self._alarms_[data] = {'val':False, 'txt':'{}{}{}{}'.format(text,data.area,data.address,data._bit_nr)}
        self._alarms_list_.append(self._alarms_[data]['txt'])

    @pyqtSlot(BaseData, bool)
    def alarm_state(self, data:BaseData, val:bool):
        if data in self._alarms_.keys():
            pass
        self._alarms_[data]['val'] = val


