import struct


def _from_plc_bit_(list_of_bytes, bit_nr):
    val = list_of_bytes[0]
    mask = 1 << bit_nr
    return val & mask != 0

def _from_plc_byte_(list_of_bytes):
    return list_of_bytes[0]

def _from_plc_sint_(list_of_bytes):
    return int.from_bytes(list_of_bytes[0], byteorder='big', signed=True)

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
    return struct.unpack('>f',list_of_bytes[:4])[0]

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
    return new_val

def _to_plc_byte_(list_of_bytes):
    return list_of_bytes[0]

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

class BaseData:
    def __init__(self, area, db_number, address, bit_nr, data_type):
        self._area=area
        self._db_number=db_number
        self._address=address
        self._bit_nr=bit_nr
        self._data_type=data_type

        if self._data_type == 'BOOL':
            self._size = 1
            self._plc_to_visu_conv = lambda list_of_bytes:_from_plc_bit_(list_of_bytes, self._bit_nr)
            self._visu_to_plc_conv = lambda list_of_bytes, val: _to_plc_bit_(list_of_bytes, self._bit_nr, val)
        elif self._data_type == 'BYTE':
            self._size = 1
            self._plc_to_visu_conv = _from_plc_byte_
            self._visu_to_plc_conv = _to_plc_byte_
        elif self._data_type == 'SINT':
            self._size = 1
            self._plc_to_visu_conv = _from_plc_sint_
            self._visu_to_plc_conv = _to_plc_sint_
        elif self._data_type == 'WORD':
            self._size = 2
            self._plc_to_visu_conv = _from_plc_word_
            self._visu_to_plc_conv = _to_plc_word_
        elif self._data_type == 'INT':
            self._size = 2
            self._plc_to_visu_conv = _from_plc_int_
            self._visu_to_plc_conv = _to_plc_int_
        elif self._data_type == 'DWORD':
            self._size = 4
            self._plc_to_visu_conv = _from_plc_dword_
            self._visu_to_plc_conv = _to_plc_dword_
        elif self._data_type == 'DINT':
            self._size = 4
            self._plc_to_visu_conv = _from_plc_dint_
            self._visu_to_plc_conv = _to_plc_dint_
        elif self._data_type == 'REAL':
            self._size = 4
            self._plc_to_visu_conv = _from_plc_real_
            self._visu_to_plc_conv = _to_plc_real_

        self._occupied_bytes = [x for x in range(self._address, self._address + self._size)]

    @property
    def occupied_bytes(self):
        return self._occupied_bytes

    def bytes_list_to_variable(self, list_of_bytes):
        return self._plc_to_visu_conv(list_of_bytes)

    def variable_to_bytes_list(self, *args):
        return self._visu_to_plc_conv(*args)

