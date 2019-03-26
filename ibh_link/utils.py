import configparser
import ipaddress
import re
# from PyQt5.QtWidgets import QWidget
from ibh_link.data_plc import variable_range, DataType, Action, variable_full_description, DEFAULT_RANGE


def recursive_dict_fromkeys(recursive_dict: dict) -> dict:
    result = dict()
    for k,v in recursive_dict.items():
        if type(v) is dict:
            result[k] = recursive_dict_fromkeys(v)
        else:
            result[k] = None
    return result


class PlcVariableParser:
    """
    Class for parsing strings provided by 'What's this' property
    """


    def __init__(self):
        _data_area_finder_expresion = r"^([A-Z]{1,3})([\d]{1,4})"
        _bit_type_address_expresion = r"(?<=\.)[0-7]"
        _data_block_offset_expresion = r"((?<=\.)DB[BWDX])(\d{1,5})"
        _data_type_expresion = r"BOOL|BYTE|SINT|WORD|INT|DWORD|DINT|REAL"
        _bit_action_type = r"(?<![EN])[RST](?![EIO])|(?<![EN])SET|RESET|TOGGLE"
        _range_expresion = r"(RANGE)\(([\d\-\+\.]+),([\d\+\.]+)\)"
        self._data_area_re = re.compile(_data_area_finder_expresion)
        self._bit_type_address_re = re.compile(_bit_type_address_expresion)
        self._data_block_offset_re = re.compile(_data_block_offset_expresion)
        self._data_type_re = re.compile(_data_type_expresion)
        self._bit_action_re = re.compile(_bit_action_type)
        self._range_re = re.compile(_range_expresion)
        
    def find_bit_action(self, val):
        action = self._bit_action_re.search(val)
        if action is not None:
            char = action.group(0)[0]
            if char == 'S':
                return Action.SET
            elif char == 'R':
                return Action.RESET
            elif char == 'T':
                return Action.TOGGLE
        return None

    def find_wirte_action(self, val):
        if 'WRITE' in val:
            return Action.WRITE
        else:
            return None

    def cut_string(self, text, begin, end):
        _text_len = len(text)
        if _text_len < 1 or begin > end or end > _text_len - 1:
            return text
        else:
            return text[:begin] + text[end:-1]

    def convert_str_to_data_type(self, val:str) -> DataType:
        if val == 'BOOL':
            return DataType.BOOL
        elif val == 'BYTE':
            return DataType.BYTE
        elif val == 'SINT':
            return DataType.SINT
        elif val == 'WORD':
            return DataType.WORD
        elif val == 'INT':
            return DataType.INT
        elif val == 'DWORD':
            return DataType.DWORD
        elif val == 'DINT':
            return DataType.DINT
        elif val == 'REAL':
            return DataType.REAL
        return None

    def values_in_range(self, val_1, val_2, range_1, range_2):
        if range_1 > range_2:
            (range_1, range_2) = (range_2, range_1)
        if val_1 < range_1 or val_1 > range_2:
            return False
        if val_2 < range_1 or val_2 > range_2:
            return False
        return True

    def analyze_range(self, re_result, var_type: DataType):
        """
        Method is trying to find variable range description like: 'RANGE(-20,500)'
        Can raise: ValueError
        :param re_result: re.Match
        :param var_type: DataType
        :return: variable_range
        """
        result_first = None
        result_second = None
        if re_result is not None:
            if re_result.group(1) == 'RANGE':
                first = re_result.group(2)
                second = re_result.group(3)
                if var_type == DataType.REAL:
                    result_first = float(first)
                    result_second = float(second)
                elif var_type in (DataType.BYTE, DataType.SINT, DataType.WORD, DataType.INT, DataType.DWORD, DataType.DINT):
                    result_first = int(first)
                    result_second = int(second)
                if not self.values_in_range(result_first, result_second, *DEFAULT_RANGE[var_type]):
                    raise ValueError('Not valid range values: {} {}'.format(first, second))
            if result_first > result_second:
                (result_first, result_second) = (result_second, result_first)
        else:
                result_first, result_second = DEFAULT_RANGE[var_type]
        return variable_range(result_first, result_second)

    def parse(self, str_val):
        """
        Method for parsing strings, for instance: 'db100.dbx10.2' to named tuple 'variable_full_description'.
        :param str_val: str
        :raises ValueError
        :return: variable_full_description
        """
        area = None
        offset = None
        address = None
        bit_number = None
        data_type = None
        action_type = None
        var_range = None
        val = str_val.strip().upper()
        val = val.replace(" ", "")
        result_range_search = self._range_re.search(val)
        if result_range_search:
            val = self.cut_string(val, result_range_search.start(), result_range_search.end()-1)
        result_write_search = self.find_wirte_action(val)
        if result_write_search:
            val = val.replace('WRITE', '')
        val = val.replace(",", "")
        data_area_match = self._data_area_re.match(val)
        if data_area_match is None:
            raise ValueError('No valid S7 address:{}'.format(str_val))

        area = data_area_match.group(1)
        if area in ['M', 'I', 'E', 'Q', 'A']:
            address = int(data_area_match.group(2))
            action_type = self.find_bit_action(val)
            val_indirect = val[data_area_match.end(0):]
            bit_match = self._bit_type_address_re.search(val_indirect)
            if bit_match is None or result_range_search or result_write_search:
                raise ValueError('No valid S7 address:{}'.format(str_val))
            bit_number = int(bit_match.group(0))
            data_type = DataType.BOOL

        elif area in ['MB', 'MW', 'MD', 'AB', 'AW', 'AD', 'IB', 'IW', 'ID',
                           'QB', 'QW', 'QD', 'EB', 'EW', 'ED']:
            address = int(data_area_match.group(2))
            action_type = result_write_search
            val_indirect = val[data_area_match.end(0):]
            data_type_match = self._data_type_re.match(val_indirect)
            char = area[1]
            if char == 'B':
                implicit_data_type = DataType.BYTE
            elif char == 'W':
                implicit_data_type = DataType.WORD
            elif char == 'D':
                implicit_data_type = DataType.DWORD
            if data_type_match is None:
                if len(val_indirect) > 0:
                     raise ValueError('No valid S7 address:{}'.format(str_val))
                data_type = implicit_data_type
            else:
                data_type = self.convert_str_to_data_type(data_type_match.group(0))
                if data_type in [DataType.BYTE, DataType.SINT] and implicit_data_type == DataType.BYTE:
                    pass
                elif data_type in [DataType.WORD, DataType.INT] and implicit_data_type == DataType.WORD:
                    pass
                elif data_type in [DataType.DWORD, DataType.DINT, DataType.REAL] and implicit_data_type == DataType.DWORD:
                    pass
                else:
                    raise ValueError('No valid S7 address:{}'.format(str_val))
            var_range = self.analyze_range(result_range_search, data_type)
            area = area[0]

        elif area == 'DB':
            area = 'D'
            address = int(data_area_match.group(2))
            val_indirect = val[data_area_match.end(0):]
            data_block_address_match = self._data_block_offset_re.search(val_indirect)
            if data_block_address_match is None:
                raise ValueError('No valid S7 address:{}'.format(str_val))

            char = data_block_address_match.group(1)[2]

            if char == 'X':
                offset = int(data_block_address_match.group(2))
                action_type = self.find_bit_action(val)
                val_indirect = val_indirect[data_area_match.end(2):]
                bit_match = self._bit_type_address_re.search(val_indirect)
                if bit_match is None or result_range_search or result_write_search:
                    raise ValueError('No valid S7 address:{}'.format(str_val))
                bit_number = int(bit_match.group(0))
                data_type = DataType.BOOL
            else:
                offset = int(data_block_address_match.group(2))
                action_type = result_write_search
                val_indirect = val_indirect[data_block_address_match.end(0):]
                data_type_match = self._data_type_re.match(val_indirect)
                if char == 'B':
                    implicit_data_type = DataType.BYTE
                elif char == 'W':
                    implicit_data_type = DataType.WORD
                elif char == 'D':
                    implicit_data_type = DataType.DWORD

                if data_type_match is None:
                    data_type = implicit_data_type
                else:
                    data_type = self.convert_str_to_data_type(data_type_match.group(0))
                    if data_type in [DataType.BYTE, DataType.SINT] and implicit_data_type == DataType.BYTE:
                        pass
                    elif data_type in [DataType.WORD, DataType.INT] and implicit_data_type == DataType.WORD:
                        pass
                    elif data_type in [DataType.DWORD, DataType.DINT, DataType.REAL] and implicit_data_type == DataType.DWORD:
                        pass
                    else:
                        raise ValueError('No valid S7 address:{}'.format(str_val))
                var_range = self.analyze_range(result_range_search, data_type)

        else:
            raise ValueError('No valid S7 address:{}'.format(str_val))

        # Replacing German notation:
        if area == 'E':
            area = 'I'
        elif area == 'A':
            area = 'Q'

        full_var_desc = variable_full_description(area, address, offset, bit_number, data_type, action_type, var_range)
        return full_var_desc

    def parse_alarm(self, str_val):
        """
        Method for parsing alarm window, for instance: 'db100.dbx10.2 comment section' to
        named tuple 'variable_full_description' and 'comment section'
        :param str_val: str
        :raises ValueError
        :return: variable_full_description, str
        """
        val, comment = str_val.strip().split(' ', 1)
        comment = comment.strip()
        val = val.strip().upper()
        full_var_desc = self.parse(val)
        if full_var_desc.data_type != DataType.BOOL or full_var_desc.action != None:
            raise ValueError('No valid S7 address for alarm variable:{}'.format(str_val))
        return full_var_desc, comment


class ConfReader:
    """
    Class for reading configuration parameters from defined file location
    """
    def __init__(self, location:str):
        self._configuration = configparser.ConfigParser()
        # TODO: use context manager, or try block
        self._configuration.read(location)
        if len(self._configuration.sections()) == 0:
            raise FileExistsError('File in location \'{}\' not exist or is empty'.format(location))
    @property
    def screens(self):
        """
        :rtype: list of tuple(screen title, file name)
        """
        return self._configuration.items('SCREENS')

    @property
    def plc_tcp_ip_address(self):
        try:
            val = self._configuration['PLC_ADDRESS']['address']
            addr = ipaddress.ip_address(val)
            if addr.version == 4:
                return val
            else:
                raise ValueError('Address not in 4-th version :{}'.format(val))
        except ValueError as e:
            raise ValueError('Configuration file bad entry: TCP/IP address.\n{}'.format(e))
        except Exception as e:
            raise Exception('Configuration file bad entry: TCP/IP address.')

    @property
    def plc_tcp_ip_port(self):
        try:
            val = int(self._configuration['PLC_ADDRESS']['port'])
            if val >= 0 and val <= 65535:
                return val
            else:
                raise ValueError('No valid range of port {}.'.format(val))
        except Exception as e:
            raise Exception('Configuration file bad entry: TCP/IP port number.\n{}'.format(e))

    @property
    def plc_mpi_address(self):
        try:
            return int(self._configuration['PLC_ADDRESS']['mpi'])
        except Exception as e:
            raise Exception('Configuration file bad entry: MPI plc address.')

    @property
    def refresh_time(self):
        val = float(self._configuration['REFRESH']['time'])
        if val < 100:
            raise ValueError("Please give refresh time grater than 100ms, given: {}".format(val))
        return val

    @property
    def console(self):
        try:
            val = self._configuration['DEBUG']['console'].upper()
            if val in ('FALSE', 'NO', '0', 'NONE', ''):
                return False
            else:
                return True
        except Exception as e:
            raise Exception('Configuration file bad entry: [DEBUG] console.')

def enable_crash_report(file_name):
    import faulthandler
    f1 = open(file_name, 'w')
    faulthandler.enable(file=f1)

if __name__ == '__main__':
    c = ConfReader('../config.ini')
    print(c.screens)
    print(c.plc_tcp_ip_address)
    print(c.plc_tcp_ip_port)
    print(c.plc_mpi_address)
    print(c.refresh_time)
    print(c.console)