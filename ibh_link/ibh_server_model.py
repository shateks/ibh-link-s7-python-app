from PyQt5 import QtCore
from PyQt5.QtGui import QIntValidator

from ibh_link.ibh_server_data import IbhDataCollection, BaseItem, ValueItem
from PyQt5.QtCore import QModelIndex, QAbstractItemModel, QSortFilterProxyModel
from PyQt5.QtWidgets import QItemDelegate, QLineEdit


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

    def flags(self, index):
        logic_sum = QtCore.Qt.ItemIsEnabled
        if index.column() == 2:
            logic_sum |= QtCore.Qt.ItemIsEditable
        return logic_sum

    def index(self, row, col, parent=QModelIndex(), *args, **kwargs):
        if not parent.isValid():
            parent_ref = self._root
        else:
            parent_ref = parent.internalPointer()

        child_item = parent_ref.child(row)
        if child_item:
            return self.createIndex(row, col, child_item)
        else:
            return QtCore.QModelIndex()

    def hasChildren(self, parent=None, *args, **kwargs):
        if parent.isValid():
            return 0 < self.rowCount(parent)
        else:
            return super().hasChildren(parent)

    def rowCount(self, parent=None, *args, **kwargs):
        """

        :param QModelIndex parent:
        """
        if not parent.isValid():
            parent_item = self._root
        else:
            parent_item = parent.internalPointer()
        return parent_item.childCount()

    def columnCount(self, parent=None, *args, **kwargs):
        return 3

    def data(self, index, role=None):
        """

        :type index: QModelIndex
        """
        if not index.isValid():
            return None

        item = index.internalPointer()

        if role == QtCore.Qt.DisplayRole:

            if type(item) is BaseItem:
                if index.column() == 0:
                    return item.name()
                else:
                    return None
            if type(item) is ValueItem:
                if index.column() == 1:
                    return item.name()
                elif index.column() == 2:
                    return item.value
        if role == QtCore.Qt.EditRole:
            if index.column() == 0:
                return item.name()

    def headerData(self, section, Qt_Orientation, role=None):
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return 'Memory area'
            elif section == 1:
                return 'Address/Offset'
            elif section == 2:
                return 'Value'

    def setData(self, index, value, role=None):
        if index.isValid():

            item = index.internalPointer()

            if role == QtCore.Qt.EditRole and type(item) is ValueItem:
                item.value = value
                self.dataChanged.emit(index, index)
                return True

        return False

class ChangeByteDelegate(QItemDelegate):

    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        line_edit = QLineEdit(parent)
        value_validator = QIntValidator(0,255)
        line_edit.setValidator(value_validator)
        return line_edit

    def setEditorData(self, editor, index):
        # value = index.internalPointer().value
        value = index.data()
        editor.setText(str(value))

    def setModelData(self, editor: QLineEdit, model: QAbstractItemModel, index: QModelIndex):
        value = int(editor.text())
        model.setData(index, value, QtCore.Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

class ProxySortModel(QSortFilterProxyModel):

    def __init__(self, parent=None):
        super().__init__(parent)

    def lessThan(self, left_index: QModelIndex, right_index: QModelIndex):
        try:
            left_item = left_index.internalPointer()
            right_item = right_index.internalPointer()
            if left_item.childCount() == 0:

                if left_item.name() < right_item.name():
                    return True
                else:
                    return False
            else:
                return False
        except AttributeError:
            return False

    def sort(self, column, order=None):
        if column == 1:
            super().sort(column, order)

