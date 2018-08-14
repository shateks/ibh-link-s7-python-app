from PyQt5.QtCore import QObject, QThread, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QLabel, QPushButton
import time
import string
import threading
import ibhlinkdriver
import IBHconst
from data_plc import BaseData

"""
Wymagania:
* należy ustalić stały interwał odświeżania
* nie łączyć bezpośrednio sygnał/slot przycisków gui z funkcjami zapisującymi/odczytującymi driver-a.
    Chcę uniknąć zasypywania wątku sygnałami dotyczących tej samej zmiennej z jednego przycisku
    po kilkukrotnym naciśnięciu.
* slot qt do odbierania żądań odczytu i zapisu zmiennych????
* sygnał qt do przesyłania zmiennych
* odczyt/zapis możliwość cykliczności, lub cykliczność przenieść poziom wyżej. Trzeba przenieść!
* Czy po zakończeniu cyklu odczytu i zapisu zrywać połączenie???

Powiązanie odczytywania zestawu zmiennych bitowych z obiektami graficznymi?
1. W momencie ładowania pliku z ui rejestrowane są obiekty 'lista_X' gui
    które trzeba odświeżać, adres zmiennej w właściwości 'what's this'
2. lista_X - jedna zmienna może być wyświetlana/uaktualniania w wielu obiektach
3. będą dwie listy: odczyt i zapis. Zapis gdy będzie interakcja z gui w stylu naciśnięty przycisk

Obiekty graficzne objęte rejestrowaniem:
- label
- button, działanie jak mono-stabilny
- button z opcją checkable, działanie jak bi-stabilny
- line edit

Proces ładowania plików ui:
Przeszukuje wszystkie obiekty graficzne, w celu odnalezienia zawartości pola What's this.
Jeżeli w what's this, mamy: 
* 'M10.1' - oznacza 1-szy bit markera 10.
* 'MW20,WORD' - oznacza słowo, adres 20.
* 'MD20,DINT' - oznacza podwójny integer(4bajty), adres 20
* 'MD20,REAL' - oznacza liczbę zmiennoprzecinkową (4bajty), adres 20
Znalezione pola wpisujemy do listy/słownika/zbioru
"""


class Manager(QObject):
    """
    The managing class for Worker.
    Is responsive for:
    * invoking cyclically read of memory areas
    * sending results of reads to subscribers
    * same operations above for writes
    """

    def __init__(self):
        """

        """
        self.visu_variable_list = []
        self.visu_variable = dict()
        self.bytes_for_readout = dict()

        # self._grouped_read_out_list
        pass

    @staticmethod
    def divide_lists_of_address(input_list, chunk_size):
        """
        Method divides list for bytes readout, list after processing should be optimized
        to minimize count of readout.
        :param input_list: list - with no duplicates unsorted or sorted
        :param chunk_size: int - size of byte block
        :return: list of lists - divided list
        """
        _list = sorted(input_list)
        _result = []
        _partial_result = []

        _div_point = _list[0] + chunk_size - 1
        _prev_element = _list[0]
        _div_begin = _list[0]

        for element in _list:
            if element > _div_point:
                _partial_result = [x for x in range(_div_begin, _prev_element + 1)]
                _div_point = element + chunk_size
                _result.append(_partial_result)
                _div_begin = element
            _prev_element = element

        _partial_result = [x for x in range(_div_begin, _prev_element + 1)]
        _result.append(_partial_result)

        return _result

    def add_subscriber(self, data_description, q_obj_refernce):
        """
        Adding subscriber for plc data readout.

        :param data_description: tuple(area:string,db_number:int,address:int,bit_nr:int,data_type:string)
        :param q_obj_refernce: QObject - Reference for QObject
        :return:
        """

        if isinstance(q_obj_refernce, QLabel):
            data = BaseData(*data_description)

            slot = q_obj_refernce.setText

        elif isinstance(q_obj_refernce, QPushButton):
            pass
        pass

class Worker(QObject):
    """
    The class wrapping ibhlinkdriver in a QObject type object that can be moved to a thread and used
    from the benefits of Qt signals and slots.
    The methods have practically the same arguments.
    """
    def __init__(self, ip_address, mpi_address):
        super().__init__()
        self.driver = ibhlinkdriver.ibhlinkdriver(ip_address, IBHconst.IBHLINK_PORT, mpi_address)


    @pyqtSlot(str, int, int, int)
    def read_bytes(self, data_type, data_number, db_number, size):
        """
        :param data_type: string - M, E or I, A or Q, D
        :param data_number: int - number of data
        :param db_number: int - in case of type 'D' number of DB block
        :param size: int - number of bytes to read beginning from target 'data_number'
        """
        if not self.driver.connected:
            self.driver.connect_plc()

        vals = self.driver.read_vals(data_type, data_number, db_number, size)
        self.read_bytes_signal.emit(vals)
        self.driver.disconnect_plc()
        # self.read_bytes_signal.emit([1,2,3,4,5,6,7,8])


    # TODO: slot do zapisu list<int> dowolnej długości

    # TODO: slot do odczytu dowolnego bitu

    # TODO: slot do zapisu dowolnego bitu

    # TODO: sygnał odczytu list of int
    read_bytes_signal = pyqtSignal(list)
    # TODO: sygnał błędu operacji
    endSlot = pyqtSignal()
