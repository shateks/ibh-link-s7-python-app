from PyQt5 import QtCore
from IbhServerData import data_item, IbhDataCollection, BaseItem, ValueItem
import PyQt5.Qt
from PyQt5.QtCore import QModelIndex

class Model(QtCore.QAbstractItemModel):

    def __init__(self, collection, parent=None):
        """

        :param IbhDataCollection collection:
        """
        super().__init__(parent)
        self._collection = collection
        self._root = self._collection.get_root()

    def parent(self, index=None):
        """

        :param QModelIndex index:
        """
        if not index.isValid():
            return QModelIndex()

        child_item = index.internalPointer()
        parent_item = child_item.parent()

        if parent_item == self._root:
            return QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def flags(self, QModelIndex):
        return QtCore.Qt.ItemIsEnabled

    def index(self, row, col, parent=None, *args, **kwargs):
        if not self.hasIndex(row,col,parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parent_ref = self._root
        else:
            parent_ref = parent.internalPointer()

        child_item = parent_ref.child(row)
        if child_item:
            return self.createIndex(row, col, child_item)
        else:
            return QtCore.QModelIndex()

    def rowCount(self, parent=None, *args, **kwargs):
        """

        :param QModelIndex parent:
        :rtype: QModelIndex
        """
        if not parent.isValid():
            parent_item = self._root
        else:
            parent_item = parent.internalPointer()
        return parent_item.childCount()

    def columnCount(self, parent=None, *args, **kwargs):
        # if type(parent.internalPointer().) is ValueItem:
        #     return 2
        return 2

    def data(self, index, role=None):
        """

        :type index: QModelIndex
        """
        if not index.isValid():
            return None

        item = index.internalPointer()

        if role == QtCore.Qt.DisplayRole:
            # return index.column()
            if type(item) is BaseItem:
                if index.column() == 0:
                    return item.name()
                else:
                    return None
            if type(item) is ValueItem:
                if index.column() == 0:
                    return item.name()
                else:
                    return item.value