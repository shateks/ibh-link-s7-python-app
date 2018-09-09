from collections import namedtuple

data_item = namedtuple('data_item', ['area', 'address', 'offset'])


class BaseItem():
    def __init__(self, name, parent=None):
        self._name = name
        self._child_dict = dict()
        self._parent = parent
        if self._parent is not None:
            self._parent.appendChild(self)

    def appendChild(self, child):
        self._child_dict[child.name()]=child

    def parent(self):
        return self._parent

    def row(self):
        return list(self._parent._child_dict.keys()).index(self.name())

    def childCount(self):
        return len(self._child_dict)

    def columnCount(self):
        return 1

    def child(self, row):
        return list(self._child_dict.values())[row]

    def name(self):
        return self._name

    def children(self):
        return self._child_dict

    def __getitem__(self, key):
        return self.children()[key]


class ValueItem(BaseItem):

    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self._value = 0

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self,_new_val):
        self._value = _new_val


class IbhDataCollection():

    def __init__(self):
        self._add_if_not_exist = False

        self._collection = BaseItem('root')
        BaseItem('M', self._collection)
        BaseItem('I', self._collection)
        BaseItem('Q', self._collection)
        BaseItem('D', self._collection)

    def get_root(self):
        return self._collection

    def add_if_not_exist(self, value):
        self._add_if_not_exist = bool(value)

    def is_in_collection(self, item):
        """
        Method check if item is in collection.
        :rtype: bool
        :type item: data_item
        """
        if item.area in ['M','I','Q']:
            return item.address in self._collection[item.area].children()
        elif (item.area == 'D') and (item.address in self._collection['D'].children()):
            return item.offset in self._collection['D'][item.address].children()
        return False

    def get(self, item):
        """
        Gets item from collection
        :param item: data_item
        :return: int
        """
        if self.is_in_collection(item):
            if item.area == 'D':
                return self._collection['D'][item.address][item.offset].value
            else:
                return self._collection[item.area][item.address].value
        elif self._add_if_not_exist:
            self.append(item, 0)
            return 0
        else:
            raise ValueError('No valid type of area, or item not in collection, item={}'.format(item))

    def set(self, item, value):
        """
        Sets value to collection
        :param item: data_item
        :param value: int
        """
        if value > 255:
            raise ValueError("Please don't put here values larger than 0xff, given value:{}".format(value))
        if self.is_in_collection(item):
            if item.area == 'D':
                self._collection['D'][item.address][item.offset].value = value
            else:
                self._collection[item.area][item.address].value = value
        elif self.add_if_not_exist:
            self.append(item, value)
        else:
            raise ValueError('No valid type of area, or item not in collection, item={}'.format(item))

    def append(self, item, value):
        """
        Method appending item to collection
        :type value: int
        :type item: data_item
        """
        if item.area == 'D':
            elem_area = self._collection._child_dict[item.area]
            if elem_area:
                if item.address in elem_area.children():
                    _db_item = elem_area.children()[item.address]
                    if item.offset in _db_item.children():
                        _db_value_item = _db_item.children()[item.offset]
                        _db_value_item.value = value
                    else:
                        _db_value_item = ValueItem(item.offset, _db_item)
                        _db_value_item.value = value
                else:
                    _db_item = BaseItem(item.address, elem_area)
                    _db_value_item = ValueItem(item.offset, _db_item)
                    _db_value_item.value = value

        elif item.area in ['M','I','Q']:
            elem_area = self._collection._child_dict[item.area]
            if elem_area:
                if item.address in elem_area.children():
                    _value_item = elem_area.children()[item.address]
                    _value_item.value = value
                else:
                    _value_item = ValueItem(item.address, elem_area)
                    _value_item.value = value
