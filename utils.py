import configparser
import re
from PyQt5.QtWidgets import QWidget

SUPPORTED_WIDGETS = ['QPushButton','QLabel']
# SUPPORTED_WIDGETS = ['QRadioButton','QPushButton','QLabel','QLineEdit','QCheckBox']

"""
QLabel - only for reading
    slot: setText()
    
QPushButton - can be for writing only (checkable=false), and 
    property: checkable, check by: isCheckable()
    slot: setChecked(bool)
    signal: clicked(bool checked = false) "If the button is checkable, checked is true
                            if the button is checked, or false if the button is unchecked."
"""
def find_supported_widgets(widget):
    w_list = widget.findChildren(QWidget)
    for w in w_list:
        if w.metaObject().className() in SUPPORTED_WIDGETS:
            yield w

class PlcVariableParser:
    """
    Class for parsing strings provided by 'What's this' property
    """
    def __init__(self):
        _data_area_finder_expresion = r"^([A-Z]{1,3})([\d]{1,4})"
        _bit_type_address_expresion = r"(?<=\.)[0-7]"
        _data_block_address_expresion = r"((?<=\.)DB[BWDX])(\d{1,5})"
        _data_type_expresion = r"BOOL|BYTE|SINT|WORD|INT|DWORD|DINT|REAL"
        self._data_area_re = re.compile(_data_area_finder_expresion)
        self._bit_type_address_re = re.compile(_bit_type_address_expresion)
        self._data_block_address_re = re.compile(_data_block_address_expresion)
        self._data_type_re = re.compile(_data_type_expresion)

        self.area = None
        self.db_nr = None
        self.address = None
        self.bit_nr = None
        self.data_type = None

    def parse(self, str_val):
        """
        Method for parsing strings, for instance: 'db100.dbx10.2' to tuple ('D',100,10,2,'BOOL')
        :param val:
        :return: tuple(area,db_number,address,bit_nr,data_type)
        """
        val = str_val
        val = val.strip().upper()
        val = val.replace(" ", "")
        val = val.replace(",", "")
        data_area_match = self._data_area_re.match(val)
        if data_area_match is None:
            raise ValueError('No valid S7 address:{}'.format(str_val))

        self.area = data_area_match.group(1)

        if self.area in ['M', 'I', 'E', 'Q', 'A']:
            self.address = int(data_area_match.group(2))
            val = val[data_area_match.end(0):]
            bit_match = self._bit_type_address_re.search(val)
            if bit_match is None:
                raise ValueError('No valid S7 address:{}'.format(str_val))
            self.bit_nr = int(bit_match.group(0))
            self.data_type = 'BOOL'

        elif self.area in ['MB', 'MW', 'MD', 'AB', 'AW', 'AD', 'IB', 'IW', 'ID',
                           'QB', 'QW', 'QD', 'EB', 'EW', 'ED']:
            self.address = int(data_area_match.group(2))
            val = val[data_area_match.end(0):]
            data_type_match = self._data_type_re.match(val)

            char = self.area[1]

            if char == 'B':
                implicit_data_type = 'BYTE'
            elif char == 'W':
                implicit_data_type = 'WORD'
            elif char == 'D':
                implicit_data_type = 'DWORD'

            if data_type_match is None:
                if len(val) > 0:
                    raise ValueError('No valid S7 address:{}'.format(str_val))
                self.data_type = implicit_data_type
            else:
                self.data_type = data_type_match.group(0)
                if self.data_type in ['BYTE', 'SINT'] and implicit_data_type == 'BYTE':
                    pass
                elif self.data_type in ['WORD', 'INT'] and implicit_data_type == 'WORD':
                    pass
                elif self.data_type in ['DWORD', 'DINT', 'REAL'] and implicit_data_type == 'DWORD':
                    pass
                else:
                    raise ValueError('No valid S7 address:{}'.format(str_val))

            self.area = self.area[0]

        elif self.area == 'DB':
            self.area = 'D'
            self.db_nr = int(data_area_match.group(2))
            val = val[data_area_match.end(0):]
            data_block_address_match = self._data_block_address_re.search(val)
            if data_block_address_match is None:
                raise ValueError('No valid S7 address:{}'.format(str_val))

            char = data_block_address_match.group(1)[2]

            if char == 'X':
                self.address = int(data_block_address_match.group(2))
                val = val[data_area_match.end(2):]
                bit_match = self._bit_type_address_re.search(val)
                if bit_match is None:
                    raise ValueError('No valid S7 address:{}'.format(str_val))
                self.bit_nr = int(bit_match.group(0))
                self.data_type = 'BOOL'
            else:
                self.address = int(data_block_address_match.group(2))
                val = val[data_block_address_match.end(0):]
                data_type_match = self._data_type_re.match(val)

                if char == 'B':
                    implicit_data_type = 'BYTE'
                elif char == 'W':
                    implicit_data_type = 'WORD'
                elif char == 'D':
                    implicit_data_type = 'DWORD'

                if data_type_match is None:
                    self.data_type = implicit_data_type
                else:
                    self.data_type = data_type_match.group(0)
                    if self.data_type in ['BYTE', 'SINT'] and implicit_data_type == 'BYTE':
                        pass
                    elif self.data_type in ['WORD', 'INT'] and implicit_data_type == 'WORD':
                        pass
                    elif self.data_type in ['DWORD', 'DINT', 'REAL'] and implicit_data_type == 'DWORD':
                        pass
                    else:
                        raise ValueError('No valid S7 address:{}'.format(str_val))

        else:
            raise ValueError('No valid S7 address:{}'.format(str_val))

        # Replacing German notation:
        if self.area == 'E':
            self.area = 'I'
        elif self.area == 'A':
            self.area = 'Q'

        return (self.area, self.db_nr, self.address, self.bit_nr, self.data_type)


class ConfReader:
    """
    Class for reading configuration parameters from defined file "config.ini"
    """
    def __init__(self):
        self._configuration = configparser.ConfigParser()
        # TODO: use context manager, or try block
        self._configuration.read('config.ini')

    @property
    def screens(self):
        """
        :rtype: list of tuple(screen title, file name)
        """
        return self._configuration.items('SCREENS')

    @property
    def plc_tcp_ip_address(self):
        return self._configuration['PLC_ADDRESS']['address']

    @property
    def plc_tcp_ip_port(self):
        return self._configuration['PLC_ADDRESS']['port']

    @property
    def plc_mpi_address(self):
        return self._configuration['PLC_ADDRESS']['mpi']

    @property
    def refresh_time(self):
        return self._configuration['REFRESH']['time']


if __name__ == '__main__':
    c = ConfReader()
    print(c.screens)
    print(c.plc_tcp_ip_address)
    print(c.plc_tcp_ip_port)
    print(c.plc_mpi_address)
    print(c.refresh_time)
