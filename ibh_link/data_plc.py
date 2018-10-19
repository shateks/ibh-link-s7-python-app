import struct
from collections import namedtuple
from enum import Enum

BYTE_MIN = 0
BYTE_MAX = 0xff
SINT_MIN = -128
SINT_MAX = 127
WORD_MIN = 0
WORD_MAX = 0xffff
INT_MIN = -32768
INT_MAX = 32767
DWORD_MIN = 0
DWORD_MAX = 0xffffffff
DINT_MIN = -2147483648
DINT_MAX = 2147483647
REAL_MIN = -3.402823e+38
REAL_MAX = 3.402823e+38

class Action(Enum):
    RESET = 1
    SET = 2
    TOGGLE = 3
    WRITE = 4

class DataType(Enum):
    BOOL = 1
    BYTE = 2
    SINT = 3
    WORD = 4
    INT = 5
    DWORD = 6
    DINT = 7
    REAL = 8

DEFAULT_RANGE = {DataType.BYTE:(BYTE_MIN,BYTE_MAX), DataType.SINT:(SINT_MIN,SINT_MAX), DataType.WORD:(WORD_MIN,WORD_MAX),
                 DataType.INT:(INT_MIN,INT_MAX), DataType.DWORD:(DWORD_MIN,DWORD_MAX), DataType.DINT:(DINT_MIN,DINT_MAX),
                 DataType.REAL:(REAL_MIN,REAL_MAX)}

def _from_plc_bit_(list_of_bytes, bit_nr):
    val = list_of_bytes[0]
    mask = 1 << bit_nr
    return val & mask != 0

def _from_plc_byte_(list_of_bytes):
    return list_of_bytes[0]

def _from_plc_sint_(list_of_bytes):
    return int.from_bytes([list_of_bytes[0]], byteorder='big', signed=True)

def _from_plc_word_(list_of_bytes):
    return int.from_bytes(list_of_bytes[:2], byteorder='big')

def _from_plc_int_(list_of_bytes):
    return int.from_bytes(list_of_bytes[:2], byteorder='big', signed=True)

def _from_plc_dword_(list_of_bytes):
    return int.from_bytes(list_of_bytes[:4], byteorder='big')

def _from_plc_dint_(list_of_bytes):
    return int.from_bytes(list_of_bytes[:4], byteorder='big', signed=True)

def _from_plc_real_(list_of_bytes):
    """
    Function converting 32bit big-endian float to float
    :param list_of_bytes:
    :return:
    """
    return struct.unpack('>f',bytes(list_of_bytes[:4]))[0]

def _to_plc_bit_(list_of_bytes, bit_nr, bool_val):
    """
    Unfortunately API not support read/write single bit, we have to read/write whole bytes.
    Function prepare byte to write, basing on previously read byte. On provided byte is performed
    bitwise logic operation, then byte is returned for write operation.
    :param list_of_bytes: list of bytes - read just before
    :param bit_nr:
    :param bool_val:
    :return:byte
    """
    mask = 1 << bit_nr
    if bool_val:
        new_val = list_of_bytes[0] | mask
    else:
        new_val = list_of_bytes[0] & (0xff - mask)
    return new_val.to_bytes(1, byteorder='big')

def _to_plc_byte_(val):
    return val.to_bytes(1, byteorder='big')

def _to_plc_sint_(val):
    return val.to_bytes(1, byteorder='big', signed=True)

def _to_plc_word_(val):
    return val.to_bytes(2, byteorder='big')

def _to_plc_int_(val):
    return val.to_bytes(2, byteorder='big', signed=True)

def _to_plc_dword_(val):
    return val.to_bytes(4, byteorder='big')

def _to_plc_dint_(val):
    return val.to_bytes(4, byteorder='big', signed=True)

def _to_plc_real_(val):
    """
    Function converting float to 32bit big-endian float
    :param val: float
    :return: bytes
    """
    return struct.pack(">f", val)

variable_range = namedtuple('variable_range',['minimum', 'maximum'])
variable_address = namedtuple('variable_address', ['area', 'address', 'offset', 'bit_number'])
visu_variable = namedtuple('visu_variable', ['area', 'address', 'offset', 'bit_nr', 'data_type'])
variable_full_description = namedtuple('variable_full_description', ['area', 'address', 'offset', 'bit_nr',
                                                                     'data_type', 'action', 'val_range'])

class BaseData:
    """
    Helper class for converting variables between PLC and PC, byteorder and data types.

    """
    def __init__(self, visu: visu_variable):
        self._area=visu.area
        self._offset=visu.offset
        self._address=visu.address
        self._bit_nr=visu.bit_nr
        self._data_type=visu.data_type

        if self._data_type == DataType.BOOL:
            self._size = 1
            self._plc_to_visu_conv = lambda list_of_bytes:_from_plc_bit_(list_of_bytes, self._bit_nr)
            self._visu_to_plc_conv = lambda list_of_bytes, val: _to_plc_bit_(list_of_bytes, self._bit_nr, val)
        elif self._data_type == DataType.BYTE:
            self._size = 1
            self._plc_to_visu_conv = _from_plc_byte_
            self._visu_to_plc_conv = _to_plc_byte_
        elif self._data_type == DataType.SINT:
            self._size = 1
            self._plc_to_visu_conv = _from_plc_sint_
            self._visu_to_plc_conv = _to_plc_sint_
        elif self._data_type == DataType.WORD:
            self._size = 2
            self._plc_to_visu_conv = _from_plc_word_
            self._visu_to_plc_conv = _to_plc_word_
        elif self._data_type == DataType.INT:
            self._size = 2
            self._plc_to_visu_conv = _from_plc_int_
            self._visu_to_plc_conv = _to_plc_int_
        elif self._data_type == DataType.DWORD:
            self._size = 4
            self._plc_to_visu_conv = _from_plc_dword_
            self._visu_to_plc_conv = _to_plc_dword_
        elif self._data_type == DataType.DINT:
            self._size = 4
            self._plc_to_visu_conv = _from_plc_dint_
            self._visu_to_plc_conv = _to_plc_dint_
        elif self._data_type == DataType.REAL:
            self._size = 4
            self._plc_to_visu_conv = _from_plc_real_
            self._visu_to_plc_conv = _to_plc_real_

        if self._area == 'D':
            self._occupied_bytes = [x for x in range(self._offset, self._offset + self._size)]
        else:
            self._occupied_bytes = [x for x in range(self._address, self._address + self._size)]

    @property
    def area(self):
        return self._area

    @property
    def address(self):
        return self._address

    @property
    def occupied_bytes(self):
        return self._occupied_bytes

    @property
    def offset(self):
        return self._offset

    @property
    def size(self):
        return self._size

    @property
    def data_type(self)->DataType:
        return self._data_type

    def bytes_list_to_variable(self, list_of_bytes):
        return self._plc_to_visu_conv(list_of_bytes)

    def variable_to_bytes(self, *args):
        return self._visu_to_plc_conv(*args)

class WritableData(BaseData):
    def __init__(self, visu: variable_full_description):
        super().__init__(visu)
        self._request_sent = False

    @property
    def request_sent(self):
        """
        Checks if was sent write request, after that value is cleared
        :return: bool
        """
        if self._request_sent:
            self._request_sent = False
            return True
        return False

    @request_sent.setter
    def request_sent(self, val):
        self._request_sent = bool(val)

class WritableBitData(WritableData):
    def __init__(self, visu: variable_full_description):
        super().__init__(visu)
        self._action = visu.action

    @property
    def action(self):
        return self._action

class WritableNumericData(WritableData):
    def __init__(self, visu: variable_full_description):
        super().__init__(visu)
        self._range = visu.val_range

    @property
    def value_range(self):
        return self._range