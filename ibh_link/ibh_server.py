import socket
import threading
import ctypes
from ibh_link.safe_connector import SafeConnector
from ibh_link import ibh_const, data_plc
from ibh_link.ibh_server_data import IbhDataCollection, data_item
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

    def produce_respose(self, data:bytes, disconnect:threading.Event) -> bytes:
        msg_rx = ibh_const.IBHLinkMSG()
        msg_rx.receiveSome(data)
        msg_tx = ibh_const.IBHLinkMSG()
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
            return bytes(msg_tx)[:ibh_const.MSG_HEADER_SIZE + msg_tx.ln]

        if msg_rx.b == ibh_const.MPI_READ_WRITE_DB:
            area ='D'
            data_address = msg_rx.data_adr
            db_offset = (msg_rx.data_area << 8) + msg_rx.data_idx
            size = msg_rx.data_cnt
            if msg_rx.func_code == ibh_const.TASK_TFC_READ:
                return self.fill_message_with_collection_data(msg_tx,area,data_address,db_offset,size)
            elif msg_rx.func_code == ibh_const.TASK_TFC_WRITE:
                return self.fill_collection_with_message_data(msg_tx,area,data_address,db_offset,size,msg_rx.d)

        elif msg_rx.b == ibh_const.MPI_GET_OP_STATUS:
            msg_tx.ln = ibh_const.TELE_HEADER_SIZE + 2
            ctypes.memmove(ctypes.addressof(msg_tx.d), self.collection.plc_state.to_bytes(2, byteorder='little'), 2)
            return bytes(msg_tx)[:ibh_const.MSG_HEADER_SIZE + msg_tx.ln]

        elif msg_rx.b == ibh_const.MPI_READ_WRITE_M:
            area ='M'
            data_address = msg_rx.data_adr
            size = msg_rx.data_cnt
            if msg_rx.func_code == ibh_const.TASK_TFC_READ:
                return self.fill_message_with_collection_data(msg_tx, area, data_address, 0, size)
            elif msg_rx.func_code == ibh_const.TASK_TFC_WRITE:
                return self.fill_collection_with_message_data(msg_tx, area, data_address, 0, size, msg_rx.d)

        elif msg_rx.b == ibh_const.MPI_READ_WRITE_IO:
            if msg_rx.data_area == ibh_const.INPUT_AREA:
                area = 'I'
            elif msg_rx.data_area == ibh_const.OUTPUT_AREA:
                area = 'Q'
            data_address = msg_rx.data_adr
            size = msg_rx.data_cnt
            if msg_rx.func_code == ibh_const.TASK_TFC_READ:
                return self.fill_message_with_collection_data(msg_tx, area, data_address, 0, size)
            elif msg_rx.func_code == ibh_const.TASK_TFC_WRITE:
                return self.fill_collection_with_message_data(msg_tx, area, data_address, 0, size, msg_rx.d)

        elif msg_rx.b == ibh_const.MPI_READ_WRITE_CNT:
            area = 'C'
            data_address = msg_rx.data_adr
            size = msg_rx.data_cnt
            if msg_rx.func_code == ibh_const.TASK_TFC_READ:
                return self.fill_message_with_collection_data(msg_tx, area, data_address, 0, size)
            elif msg_rx.func_code == ibh_const.TASK_TFC_WRITE:
                return self.fill_collection_with_message_data(msg_tx, area, data_address, 0, size, msg_rx.d)

        elif msg_rx.b == ibh_const.MPI_READ_WRITE_TIM:
            area = 'T'
            data_address = msg_rx.data_adr
            size = msg_rx.data_cnt
            if msg_rx.func_code == ibh_const.TASK_TFC_READ:
                return self.fill_message_with_collection_data(msg_tx, area, data_address, 0, size)
            elif msg_rx.func_code == ibh_const.TASK_TFC_WRITE:
                return self.fill_collection_with_message_data(msg_tx, area, data_address, 0, size, msg_rx.d)

        elif msg_rx.b == ibh_const.MPI_DISCONNECT:
            msg_tx.ln = 8
            disconnect.set()
            return bytes(msg_tx)[:ibh_const.MSG_HEADER_SIZE + ibh_const.TELE_HEADER_SIZE]

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
            data_added_flag = False
            val = list()
            for i in range(size):
                if area == 'D':
                    _item = data_item(area, data_address, db_offset + i)
                else:
                    _item = data_item(area, data_address + i, 0)
                if not self.collection.is_in_collection(_item):
                    data_added_flag = True
                val.append(self.collection.get(_item))
            if self.connector and data_added_flag:
                self.connector.emit(EventType.added, area)
            msg.ln = ibh_const.TELE_HEADER_SIZE + msg.data_cnt
            ctypes.memmove(ctypes.addressof(msg.d), bytes(val), len(val))
        except ValueError:
            msg.ln = ibh_const.TELE_HEADER_SIZE
            msg.f = ibh_const.REJ_IV
        return bytes(msg)[:ibh_const.MSG_HEADER_SIZE + msg.ln]

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
            data_added_flag = False
            data_changed_flag = False
            val = list(array[:size])
            for i in range(size):
                if area == 'D':
                    _item = data_item(area, data_address, db_offset + i)
                else:
                    _item = data_item(area, data_address + i, 0)
                if self.collection.is_in_collection(_item):
                    data_changed_flag = True
                else:
                    data_added_flag = True
                self.collection.set(_item, val[i])
            if self.connector:
                if data_added_flag:
                    self.connector.emit(EventType.added, area)
                if data_changed_flag:
                    self.connector.emit(EventType.changed, area)
            msg.ln = ibh_const.TELE_HEADER_SIZE
        except ValueError:
            msg.ln = ibh_const.TELE_HEADER_SIZE
            msg.f = ibh_const.REJ_IV
        return bytes(msg)[:ibh_const.MSG_HEADER_SIZE + msg.ln]

    def basic_telegram_check(self, rx) -> int:
        """
        CON_IV the specified msg.data_cnt parameter invalid. Check the limit of 222 bytes (read)
        respectively 216 bytes (write) in msg.data_cnt.

        CON_NA no response of the remote station remote station check network wiring, check remote
        address, check baud rate
        """
        if rx.b in [ibh_const.MPI_READ_WRITE_DB, ibh_const.MPI_READ_WRITE_IO, ibh_const.MPI_READ_WRITE_M,
                    ibh_const.MPI_READ_WRITE_CNT, ibh_const.MPI_READ_WRITE_TIM]:
            if rx.func_code == ibh_const.TASK_TFC_READ and rx.data_cnt > ibh_const.IBHLINK_READ_MAX:
                return ibh_const.CON_IV
            if rx.func_code == ibh_const.TASK_TFC_WRITE and rx.data_cnt > ibh_const.IBHLINK_WRITE_MAX:
                return ibh_const.CON_IV

        if rx.device_adr != self.mpi_address:
            return ibh_const.CON_NA

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
