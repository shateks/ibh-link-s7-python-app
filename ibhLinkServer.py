import socket
import threading
import ctypes
import data_plc
from safe_connector import SafeConnector
import IBHconst
from IbhServerData import IbhDataCollection, data_item
from enum import Enum
import time

class EventType(Enum):
    added = 1
    changed = 2

class ToShortSendReceiveTelegramError(Exception):
    pass


class CorruptedTelegramError(Exception):
    pass


class FaultsInTelegramError(Exception):
    pass


class IbhLinkServer(threading.Thread):
    def __init__(self, ip_addr, ip_port, mpi_addr, collection: IbhDataCollection, connector: SafeConnector = None):
        super().__init__(daemon=True)
        self.connected = False
        self.ip_address = ip_addr
        self.ip_port = ip_port
        self.collection = collection
        self.connector = connector
        if mpi_addr < 0 or mpi_addr > 126:
            raise ValueError("mpi_addr < 0 or mpi_addr > 126")
        self.plc_status = IBHconst.OP_STATUS_STOP
        self.mpi_address = mpi_addr
        self.msg_number = 0
        self.max_recv_bytes = 512
        self.abort = threading.Event()
        self._lag = None

    def start(self):
        self.abort.clear()
        super().start()

    def stop(self):
        self.abort.set()

    @property
    def lag(self):
        return self._lag

    @lag.setter
    def lag(self, val_time):
        self._lag = val_time

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.ip_address, self.ip_port))
            s.settimeout(1.0)
            s.listen(1)
            while not self.abort.is_set():
                try:
                    conn, addr = s.accept()
                    print('Connected by', addr)
                    threading.Thread(target=self.clientHandler, args=(conn, addr, self.abort)).start()
                except socket.timeout:
                    pass

    def clientHandler(self, conn: socket.socket, address, stop_event: threading.Event):
        print("clientHandler")
        disconnect = threading.Event()
        while not stop_event.is_set() and not disconnect.is_set():
            try:
                data = conn.recv(self.max_recv_bytes)
                if data:
                    if self.lag is not None:
                        time.sleep(self.lag)
                    response = self.produce_respose(data, disconnect)
                    conn.send(response)
                else:
                    raise Exception('Client disconnected')
            except Exception as e:
                disconnect.set()
                conn.shutdown(socket.SHUT_RDWR)
                conn.close()
        conn.close()

    # def disconnect_plc(self):
    #     if not self.connected:
    #         return
    #
    #     msg_tx = IBHconst.IBHLinkMSG(rx=IBHconst.MPI_TASK, tx=IBHconst.HOST, nr=self.msg_number,
    #                                  ln=IBHconst.MSG_HEADER_SIZE, b=IBHconst.MPI_DISCONNECT,
    #                                  device_adr=self.mpi_address)
    #     self.msg_number += 1
    #
    #     msg_length = IBHconst.MSG_HEADER_SIZE + IBHconst.TELE_HEADER_SIZE
    #
    #     self.sendData(bytes(msg_tx)[:msg_length])
    #
    #     raw_bytes = self.receiveData()
    #
    #     msg_rx = IBHconst.IBHLinkMSG()
    #     msg_rx.receiveSome(raw_bytes)
    #
    #     self.basic_telegram_check(msg_tx, msg_rx, IBHconst.TELE_HEADER_SIZE)
    #
    #     self._socket.shutdown(socket.SHUT_RDWR)
    #     self._socket.close()
    #     self.connected = False
    #
    # @property
    # def str_plc_status(self) -> str:
    #     if self.plc_status == 0:
    #         return 'STOP'
    #     elif self.plc_status == 1:
    #         return 'START'
    #     elif self.plc_status == 2:
    #         return 'RUN'
    #     else:
    #         return 'UNKNOWN'
    #
    # def set_plc_status(self, val):
    #     self.plc_status = val


    def produce_respose(self, data:bytes, disconnect:threading.Event) -> bytes:
        msg_rx = IBHconst.IBHLinkMSG()
        msg_rx.receiveSome(data)
        msg_tx = IBHconst.IBHLinkMSG()
        msg_tx.rx = msg_rx.tx
        msg_tx.tx = msg_rx.rx
        # msg_tx.ln = ?
        msg_tx.nr = msg_rx.nr
        msg_tx.a = msg_rx.b
        msg_tx.f = 0
        msg_tx.b = 0
        msg_tx.e = 0
        msg_tx.device_adr = msg_rx.device_adr
        msg_tx.data_area = msg_rx.data_area
        msg_tx.data_adr = msg_rx.data_adr
        msg_tx.data_idx = msg_rx.data_idx
        msg_tx.data_cnt = msg_rx.data_cnt
        msg_tx.data_type = msg_rx.data_type
        msg_tx.func_code = msg_rx.func_code
        # msg_tx.data_type = IBHconst.TASK_TDT_UINT8 | IBHconst.TASK_TDT_UINT16
        # msg_tx.func_code = IBHconst.TASK_TFC_READ | IBHconst.TASK_TFC_WRITE
        # msg_tx.d = ?

        error = self.basic_telegram_check(msg_rx)
        if error:
            msg_tx.ln = 8
            msg_tx.f = error
            return bytes(msg_tx)[:IBHconst.MSG_HEADER_SIZE + msg_tx.ln]

        if msg_rx.b == IBHconst.MPI_READ_WRITE_DB:
            area ='D'
            data_address = msg_rx.data_adr
            db_offset = (msg_rx.data_area << 8) + msg_rx.data_idx
            size = msg_rx.data_cnt
            if msg_rx.func_code == IBHconst.TASK_TFC_READ:
                return self.fill_message_with_collection_data(msg_tx,area,data_address,db_offset,size)
            elif msg_rx.func_code == IBHconst.TASK_TFC_WRITE:
                return self.fill_collection_with_message_data(msg_tx,area,data_address,db_offset,size,msg_rx.d)

        elif msg_rx.b == IBHconst.MPI_GET_OP_STATUS:
            msg_tx.ln = IBHconst.TELE_HEADER_SIZE + 2
            ctypes.memmove(ctypes.addressof(msg_tx.d), data_plc._to_plc_word_(self.plc_status), 2)
            return bytes(msg_tx)[:IBHconst.MSG_HEADER_SIZE + msg_tx.ln]

        elif msg_rx.b == IBHconst.MPI_READ_WRITE_M:
            area ='M'
            data_address = msg_rx.data_adr
            size = msg_rx.data_cnt
            if msg_rx.func_code == IBHconst.TASK_TFC_READ:
                return self.fill_message_with_collection_data(msg_tx, area, data_address, 0, size)
            elif msg_rx.func_code == IBHconst.TASK_TFC_WRITE:
                return self.fill_collection_with_message_data(msg_tx, area, data_address, 0, size, msg_rx.d)

        elif msg_rx.b == IBHconst.MPI_READ_WRITE_IO:
            if msg_rx.data_area == IBHconst.INPUT_AREA:
                area = 'I'
            elif msg_rx.data_area == IBHconst.OUTPUT_AREA:
                area = 'Q'
            data_address = msg_rx.data_adr
            size = msg_rx.data_cnt
            if msg_rx.func_code == IBHconst.TASK_TFC_READ:
                return self.fill_message_with_collection_data(msg_tx, area, data_address, 0, size)
            elif msg_rx.func_code == IBHconst.TASK_TFC_WRITE:
                return self.fill_collection_with_message_data(msg_tx, area, data_address, 0, size, msg_rx.d)

        elif msg_rx.b == IBHconst.MPI_READ_WRITE_CNT:
            area = 'C'
            data_address = msg_rx.data_adr
            size = msg_rx.data_cnt
            if msg_rx.func_code == IBHconst.TASK_TFC_READ:
                return self.fill_message_with_collection_data(msg_tx, area, data_address, 0, size)
            elif msg_rx.func_code == IBHconst.TASK_TFC_WRITE:
                return self.fill_collection_with_message_data(msg_tx, area, data_address, 0, size, msg_rx.d)

        elif msg_rx.b == IBHconst.MPI_READ_WRITE_TIM:
            area = 'T'
            data_address = msg_rx.data_adr
            size = msg_rx.data_cnt
            if msg_rx.func_code == IBHconst.TASK_TFC_READ:
                return self.fill_message_with_collection_data(msg_tx, area, data_address, 0, size)
            elif msg_rx.func_code == IBHconst.TASK_TFC_WRITE:
                return self.fill_collection_with_message_data(msg_tx, area, data_address, 0, size, msg_rx.d)

        elif msg_rx.b == IBHconst.MPI_DISCONNECT:
            msg_tx.ln = 8
            disconnect.set()
            return bytes(msg_tx)[:IBHconst.MSG_HEADER_SIZE + IBHconst.TELE_HEADER_SIZE]

    def fill_message_with_collection_data(self, msg, area, data_address, db_offset, size):
        """
        Fills "msg" some fields with collection data, pointed by "area","data_address","db_offser","size".
        In case of positive or negative result, function return ready for sending bytes.
        :param msg: IBHconst.IBHLinkMSG - prepared message
        :param area: str - 'D','M','I','Q'
        :param data_address:
        :param db_offset:
        :param size:
        :return: bytes
        """
        try:
            val = list()
            if area == 'D':
                for i in range(size):
                    _item = data_item(area, data_address, db_offset + i)
                    _exist = self.collection.is_in_collection(_item)
                    val.append(self.collection.get(_item))
            else:
                for i in range(size):
                    _item = data_item(area, data_address + i, 0)
                    _exist = self.collection.is_in_collection(_item)
                    val.append(self.collection.get(_item))

            if self.connector and not _exist:
                self.connector.emit(EventType.added, area)
            # elif self.connector and _exist:
            #     self.connector.emit(EventType.changed, area)

            msg.ln = IBHconst.TELE_HEADER_SIZE + msg.data_cnt
            ctypes.memmove(ctypes.addressof(msg.d), bytes(val), len(val))
        except ValueError:
            msg.ln = IBHconst.TELE_HEADER_SIZE
            msg.f = IBHconst.REJ_IV
        return bytes(msg)[:IBHconst.MSG_HEADER_SIZE + msg.ln]

    def fill_collection_with_message_data(self, msg, area, data_address, db_offset, size, array):
        """
        Fills "msg" some fields with answer of operation, collection data, pointed by "area","data_address",
        "db_offser","size","array".
        In case of positive or negative result, function return ready for sending bytes.
        :param msg: IBHconst.IBHLinkMSG
        :param area: str - 'D','M','I','Q'
        :param data_address: int
        :param db_offset: int
        :param size: int
        :param array: IBHconst.dataArray
        :return: bytes
        """
        try:
            val = list(array[:size])
            if area == 'D':
                for i in range(size):
                    _item = data_item(area, data_address, db_offset + i)
                    _exist = self.collection.is_in_collection(_item)
                    self.collection.set(_item, val[i])
            else:
                for i in range(size):
                    _item = data_item(area, data_address + i, 0)
                    _exist = self.collection.is_in_collection(_item)
                    self.collection.set(data_item(area, data_address + i, 0), val[i])

            if self.connector and not _exist:
                self.connector.emit(EventType.added, area)
            elif self.connector and _exist:
                self.connector.emit(EventType.changed, area)

            msg.ln = IBHconst.TELE_HEADER_SIZE
        except ValueError:
            msg.ln = IBHconst.TELE_HEADER_SIZE
            msg.f = IBHconst.REJ_IV
        return bytes(msg)[:IBHconst.MSG_HEADER_SIZE + msg.ln]

    def basic_telegram_check(self, rx) -> int:
        """
        CON_IV the specified msg.data_cnt parameter invalid. Check the limit of 222 bytes (read)
        respectively 216 bytes (write) in msg.data_cnt.

        CON_NA no response of the remote station remote station check network wiring, check remote
        address, check baud rate
        """
        if rx.b in [IBHconst.MPI_READ_WRITE_DB, IBHconst.MPI_READ_WRITE_IO, IBHconst.MPI_READ_WRITE_M,
                    IBHconst.MPI_READ_WRITE_CNT, IBHconst.MPI_READ_WRITE_TIM]:
            if rx.func_code == IBHconst.TASK_TFC_READ and rx.data_cnt > IBHconst.IBHLINK_READ_MAX:
                return IBHconst.CON_IV
            if rx.func_code == IBHconst.TASK_TFC_WRITE and rx.data_cnt > IBHconst.IBHLINK_WRITE_MAX:
                return IBHconst.CON_IV

        if rx.device_adr != self.mpi_address:
            return IBHconst.CON_NA

        return 0


"""
REJ_IV specified offset address out of limits or not known in the remote station.
 Please check msg.data_adr if present or offset parameter in request message.
"""

"""
REJ_OP specified length to write or to read results in an access outside the limits.
Please check msg.data_cnt length in request message.
"""

"""
REJ_HW specified address not defined in the remote station. Please check msg.data_adr in the
request message.
"""


if __name__ == "__main__":
    # driver = IbhLinkServer('192.168.1.15', 1099, 2)
    collection = IbhDataCollection()
    collection.add_if_not_exist(1)
    collection.append(data_item('D',100,0),13)
    server = IbhLinkServer('127.0.0.1', 1099, 2, collection)
    server.start()
    # print("connected {}".format(server.connected))
    # print(driver.plc_get_run())
    # print(driver.read_vals('M',10,10,1))
    # print(server.read_vals('D', 0, 100, 1))
    # print(driver.plc_get_run())
    # server.disconnect_plc()
    # time.sleep(100)
    # server.stop()
    server.join()
    print('END')
