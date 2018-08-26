from collections import namedtuple

data_item = namedtuple('data_item', ['area', 'address', 'offset'])

class NotDuplicableList(list):
    def append(self, _T):
        if _T._name in [x._name for x in self]:
            pass
        else:
            super().append(_T)

class BaseItem():
    def __init__(self, name, parent=None):
        self._name = name
        self._child_list = NotDuplicableList()
        self._parent = parent
        if self._parent is not None:
            self._parent.appendChild(self)

    def appendChild(self, child):
        self._child_list.append(child)

    def parent(self):
        return self._parent

    def row(self):
        return self._parent._child_list.index(self)

    def childCount(self):
        return len(self._child_list)

    def columnCount(self):
        return 1

    def child(self, row):
        return self._child_list[row]

    def name(self):
        return self._name

    def children(self):
        return self._child_list

    def find_by_name(self, name_value):
        for x in self._child_list:
            if x.name() == name_value:
                return x
        else:
            return None

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

        # self._collection = {'M':{}, 'I':{}, 'Q':{}, 'D':{}}
        self._collection = BaseItem('root')
        # self._m_collection = BaseItem('M',self._collection)
        # self._i_collection = BaseItem('I',self._collection)
        # self._q_collection = BaseItem('Q',self._collection)
        # self._d_collection = BaseItem('D',self._collection)
        BaseItem('M', self._collection)
        BaseItem('I', self._collection)
        BaseItem('Q', self._collection)
        BaseItem('D', self._collection)

    def get_root(self):
        return self._collection
# class IbhDataCollection():
#     def __init__(self):
#         self._add_if_not_exist = False
#
#         # self._collection = {'M':{}, 'I':{}, 'Q':{}, 'D':{}}
#         self._collection = BaseItem('root')
#         # self._m_collection = BaseItem('M',self._collection)
#         # self._i_collection = BaseItem('I',self._collection)
#         # self._q_collection = BaseItem('Q',self._collection)
#         # self._d_collection = BaseItem('D',self._collection)
#         BaseItem('M', self._collection)
#         BaseItem('I', self._collection)
#         BaseItem('Q', self._collection)
#         BaseItem('D', self._collection)
#
    # @property
    # def add_if_not_exist(self):
    #     return self._add_if_not_exist
    #
    # @add_if_not_exist.setter
    # def add_if_not_exist(self, value):
    #     self._add_if_not_exist = bool(value)
    #
    # def is_in_collection(self, item):
    #     """
    #     Method check if item is in collection.
    #     :rtype: bool
    #     :type item: data_item
    #     """
    #     if item.area in ['M','I','Q']:
    #         return item.address in self._collection[item.area]
    #     elif (item.area == 'D') and (item.address in self._collection['D']):
    #         return item.offset in self._collection['D'][item.address]
    #     return False

    # def get(self, item):
    #     """
    #     Gets item from collection
    #     :param item: data_item
    #     :return: int
    #     """
    #     if self.is_in_collection(item):
    #         if item.area == 'D':
    #             return self._collection['D'][item.address][item.offset]
    #         else:
    #             return self._collection[item.area][item.address]
    #     elif self.add_if_not_exist:
    #         self.append(item, 0)
    #         return 0
    #     else:
    #         raise ValueError(format('No valid type of area, or item not in collection, item={}', item))
    #
    # def set(self, item, value):
    #     """
    #     Sets value to collection
    #     :param item: data_item
    #     :param value: int
    #     """
    #     if value > 255:
    #         raise ValueError(format("Please don't put here values larger than 0xff, given value:{}", value))
    #     if self.is_in_collection(item):
    #         if item.area == 'D':
    #             self._collection['D'][item.address][item.offset] = value
    #         else:
    #             self._collection[item.area][item.address] = value
    #     elif self.add_if_not_exist:
    #         self.append(item, value)
    #     else:
    #         raise ValueError(format('No valid type of area, or item not in collection, item={}', item))

    def append(self, item, value):
        """
        Method appending item to collection
        :type value: int
        :type item: data_item
        """
        if item.area == 'D':
            elem_area = self._collection.find_by_name(item.area)
            if elem_area:
                _db_item = elem_area.find_by_name(item.address)
                if _db_item is None:
                    _db_item = BaseItem(item.address, elem_area)
                    _db_value_item = ValueItem(item.offset, _db_item)
                    _db_value_item.value = value
                else:
                    _db_value_item = _db_item.find_by_name(item.offset)
                    if _db_value_item is None:
                        _db_value_item = ValueItem(item.offset, _db_item)
                        _db_value_item.value = value
                    else:
                        _db_value_item.value = value
            # if self._collection['D'][item.address] in self._collection['D']:
            #     self._collection['D'][item.address][item.offset] = value
            # else:
            #     self._collection['D'][item.address] = {item.offset: value}
        elif item.area in ['M','I','Q']:
            elem_area = self._collection.find_by_name(item.area)
            if elem_area:
                elem_address = elem_area.find_by_name(item.address)
                if elem_address is None:
                    _value_item = ValueItem(item.address, elem_area)
                    _value_item.value = value
                else:
                    elem_address.value = value
