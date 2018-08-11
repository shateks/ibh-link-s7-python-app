import configparser
import re


class PlcVariableParser:
    """
    Class for parsing strings provided by 'What's this' property
    """
    # TODO: Dodaj do wyszukiwania jeszcze reprezentację zmiennych: BYTE/SINT, WORD/INT, DWORD/DINT/REAL
    def __init__(self):
        _data_area_finder_expresion = r"^[A-Z]{1,3}[\d]{1,4}"
        _bit_type_address_expresion = r"(\.)([\d]{1,5})"
        _data_block_address_expresion = r""
        _data_representation_expresion = r""
        _regex = r"([ADEMIQ][BDW]?)([\d]{1,4})((\.)[\d])?((\.)(DB[BWDX])([\d]{1,5}((\.)([\d]))?))?"
        self._data_area_finder_re = re.compile(_data_area_finder_expresion)
        self._bit_type_address_re = re.compile(_bit_type_address_expresion)
        self._data_block_address_re = re.compile(_data_block_address_expresion)
        self._data_representation_re = re.compile(_data_representation_expresion)
        self._parser = re.compile(_regex)

        self.area = None
        self.db_nr = None
        self.address = None
        self.bit_nr = None
        self.data_type = None


    def parse(self, val):
        val = val.upper()
        _result = self._parser.search(val)
        _groups = _result.groups()
        return _groups


    def parse_simple(self, val):
        """

        :param val:
        :return: tuple(area,db_number,address,bit_nr,data_type)
        """
        val = val.strip().upper()
        val = val.replace(" ", "")
        data_match = self._data_area_finder_re.match(val)
        if data_match is None:
            return None

        self.area = data_match.group(1)
        if data_match in ['M', 'I', 'E', 'Q', 'A']:
            val = val[:data_match.end(0)]
            bit_match = self._bit_type_address_re.match(val)
            return objekt
        elif data_match in ['MB', 'MW', 'MD', 'AB', 'AW', 'AD', 'IB', 'IW', 'ID',
                           'QB', 'QW', 'QD', 'EB', 'EW', 'ED']:
            val = val[:data_match.end(0)]
        elif data_match == 'DB':
            val = val[:data_match.end(0)]
        else:
            return None
        self. = int(data_match.group(2))


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
