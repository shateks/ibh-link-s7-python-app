import datetime

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, QModelIndex
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
        self._alarms_original[data] = {'val': False, 'text': text}

    @pyqtSlot(BaseData, bool)
    def alarm_state(self, data:BaseData, val:bool):
        """
        Receives boolean values and update model of alarms window.
        :param data: BaseData, boolean type data address
        :param val: bool, current boolean value of bit
        :return:
        """
        if data in self._alarms_original.keys():
            previous = self._alarms_original[data]['val']
            self._alarms_original[data]['val'] = val
            if val != previous:
                if val:
                    self._alarms_collection_[data] = datetime.datetime.now().strftime('[%d.%m.%Y %H:%M:%S] ') +\
                                                     self._alarms_original[data]['text']
                else:
                    try:
                        self._alarms_collection_.pop(data)
                    except KeyError:
                        pass
                self.modelReset.emit()

