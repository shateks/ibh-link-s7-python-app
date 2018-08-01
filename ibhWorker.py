from PyQt5.QtCore import QObject, QThread, pyqtSlot, pyqtSignal
import time
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
"""
"""
Klasa owijająca ibhlinkdriver w obiekt typu QObject który można przenieść do wątku i korzystać
z dobrodziejstwa sygnałów i slotów Qt.
Metody posiadają praktycznie te same argumenty.
"""

class Worker(QObject):
    def __init__(self, ip_address, mpi_address):
        super().__init__()
        self.driver = ibhlinkdriver.ibhlinkdriver(ip_address, IBHconst.IBHLINK_PORT, mpi_address)

    # slot do odczytu list<int> dowolnej długości
    # parametry:
    @pyqtSlot(str, int, int, int)
    def read_bytes(self, data_type, data_number, db_number, size):
        """
        :param data_type: string - M, E or I, A or Q, D
        :param data_number: int - number of data
        :param db_number: int - in case of type 'D' number of DB block
        :param size: int - number of bytes to read beginning from target 'data_number'
        ???????????:rtype: list of int - as list of bytes

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
