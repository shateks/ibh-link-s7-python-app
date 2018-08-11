from PyQt5.QtCore import QObject, QThread, pyqtSlot, pyqtSignal
import time
import string
import threading
import ibhlinkdriver
import IBHconst

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
- k-led (kde led)

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

    """

    def __init__(self):
        """

        """
        self._grouped_read_out_list
        pass

    def add_subscriber(self, data, type, obj_refernce):
        """
        Adding subscriber for plc data readout.

        :param data: string - data area, address. E.g. M1.2, MW10, DB10.DBX2
        :param type: string - BOOL,BYTE,WORD,INT,DWORD,DINT,REAL
        :param obj_refernce: QObject - Reference for QObject
        :return:
        """

        # TODO: parser, własny generator z "yeld" który dzieli "MB10","db10.dbb0" na listę\
        # moment przejścia między litera/cyfra kolejny punkt podziału
        data.capitalize()
        type.capitalize()
        pass

class Worker(QObject):
    """
    Klasa owijająca ibhlinkdriver w obiekt typu QObject który można przenieść do wątku i korzystać
    z dobrodziejstwa sygnałów i slotów Qt.
    Metody posiadają praktycznie te same argumenty.
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


def _parser(data):
    _str = data.strip()
    for index, char in enumerate(_str):
        if index in range() in string.ascii_letters and _str[-1] in string.digits:

    if val[0] in []
    for char in val:
        yield char


st = ' Mb90.1 '

for s in _parser(st):
    print(s)