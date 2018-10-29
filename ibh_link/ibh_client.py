import logging
import socket
import ctypes
from ibh_link import ibh_const

logger = logging.getLogger(__name__)
# TODO: logging from this class in visu_host_gui_example causing crush
logger.setLevel(100)

class DriverError(Exception):
    pass

class ToShortSendReceiveTelegramError(DriverError):
    pass

class CorruptedTelegramError(DriverError):
    pass

class FaultsInTelegramError(DriverError):
    pass

class SocketUnexpectedDisconnected(DriverError):
    pass


class IbhLinkDriver:
    def __init__(self, ip_addr: str, ip_port: int, mpi_addr: int) -> None:
        """

        :raises ValueError
        """
        self.connected = False
        self._socket = None
        self.ip_address = ip_addr
        self.ip_port = ip_port
        if mpi_addr < 0 or mpi_addr > 126:
            raise ValueError("MPI Address is not in range (0,126)")
        self.mpi_address = mpi_addr
        self.msg_number = 0
        self.max_recv_bytes = 512
        self._time_out = None

    @property
    def timeout(self):
        return self._time_out

    @timeout.setter
    def timeout(self, val):
        """
        Setting timeout on driver, values lower than 0.1 will be treated as wait forever.
        :param: int,float val: timeout value
        :return:
        """
        if val < 0.1:
            self._time_out = None
        else:
            self._time_out = val

    def connect_plc(self):
        """
        :raises: OSError, ConnectionError
        """
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(self._time_out)
        self._socket.connect((self.ip_address, self.ip_port))
        logger.debug("Connected to:{}".format(self.ip_address))
        self.connected = True

    def disconnect_plc(self):
        """
        :raises: DriverError, ConnectionError
        """
        if not self.connected:
            return
        msg_tx = ibh_const.IBHLinkMSG(rx=ibh_const.MPI_TASK, tx=ibh_const.HOST, nr=self.msg_number,
                                      ln=ibh_const.MSG_HEADER_SIZE, b=ibh_const.MPI_DISCONNECT,
                                      device_adr=self.mpi_address)
        self.msg_number += 1
        msg_length = ibh_const.MSG_HEADER_SIZE + ibh_const.TELE_HEADER_SIZE
        self.sendData(bytes(msg_tx)[:msg_length])
        raw_bytes = self.receiveData()
        msg_rx = ibh_const.IBHLinkMSG()
        msg_rx.receiveSome(raw_bytes)
        self.received_telegram_check(msg_tx, msg_rx, ibh_const.TELE_HEADER_SIZE)
        self.connected = False
        logger.debug("Disconnected:{}".format(self.ip_address))

    def drop_connection(self):

        if self._socket is not None:
            if not self._socket._closed and self._socket is not None:
                # self._socket.shutdown(socket.SHUT_RDWR)
                self._socket.close()
            self._socket = None
        self.connected = False

    def plc_get_run(self) -> str:
        """
        :return: 'STOP', 'START', 'RUN' or 'UNKNOWN'
        :raises: DriverError, ConnectionError
        """
        msg_tx = ibh_const.IBHLinkMSG(rx=ibh_const.MPI_TASK, tx=ibh_const.HOST, nr=self.msg_number,
                                      ln=ibh_const.MSG_HEADER_SIZE, b=ibh_const.MPI_GET_OP_STATUS,
                                      device_adr=self.mpi_address)
        self.msg_number += 1
        self.sendData(bytes(msg_tx)[:ibh_const.MSG_HEADER_SIZE + ibh_const.TELE_HEADER_SIZE])
        raw_bytes = self.receiveData()
        msg_rx = ibh_const.IBHLinkMSG()
        msg_rx.receiveSome(raw_bytes)
        self.received_telegram_check(msg_tx, msg_rx, ibh_const.TELE_HEADER_SIZE + 2)
        op_status = int.from_bytes(msg_rx.d[:2], byteorder='little')
        if op_status == 0:
            return 'STOP'
        elif op_status == 1:
            return 'START'
        elif op_status == 2:
            return 'RUN'
        else:
            return 'UNKNOWN'

    def read_vals(self, data_type: str, data_address: int, offset: int, size: int) -> [int]:
        """
        :raises: ValueError, DriverError, ConnectionError
        """
        logger.debug('Reading vals:{}, address {}, offset {}, size {}'.format(data_type, data_address, offset, size))
        if size > ibh_const.IBHLINK_READ_MAX or size <= 0:
            raise ValueError("size > IBHconst.IBHLINK_READ_MAX or size <= 0:")
        elif data_type == 'E' or data_type == 'I':
            msg_tx = ibh_const.IBHLinkMSG(b=ibh_const.MPI_READ_WRITE_IO, data_area=ibh_const.INPUT_AREA, data_adr=data_address,
                                          data_cnt=size, data_type=ibh_const.TASK_TDT_UINT8)
        elif data_type == 'A' or data_type == 'O' or data_type == 'Q':
            msg_tx = ibh_const.IBHLinkMSG(b=ibh_const.MPI_READ_WRITE_IO, data_area=ibh_const.OUTPUT_AREA,
                                          data_adr=data_address, data_cnt=size, data_type=ibh_const.TASK_TDT_UINT8)
        elif data_type == 'M':
            msg_tx = ibh_const.IBHLinkMSG(b=ibh_const.MPI_READ_WRITE_M, data_adr=data_address,
                                          data_cnt=size, data_type=ibh_const.TASK_TDT_UINT8)
        elif data_type == 'D':
            msg_tx = ibh_const.IBHLinkMSG(b=ibh_const.MPI_READ_WRITE_DB, data_area=offset >> 8, data_idx=offset,
                                          data_adr=data_address, data_cnt=size, data_type=ibh_const.TASK_TDT_UINT8)
        elif size > ibh_const.IBHLINK_READ_MAX / 2:
            raise ValueError("size > IBHconst.IBHLINK_READ_MAX/2")
        elif data_type == 'T':
            # TODO: implementation read 'T'
            return None
        elif data_type == 'Z' or data_type == 'C':
            # TODO: implementation read 'C'
            return None
        else:
            raise ValueError("No valid data type")

        msg_tx.rx = ibh_const.MPI_TASK
        msg_tx.tx = ibh_const.HOST
        msg_tx.ln = ibh_const.TELE_HEADER_SIZE
        msg_tx.nr = self.msg_number
        msg_tx.device_adr = self.mpi_address
        msg_tx.func_code = ibh_const.TASK_TFC_READ

        self.msg_number += 1
        msg_length = ibh_const.MSG_HEADER_SIZE + ibh_const.TELE_HEADER_SIZE

        self.sendData(bytes(msg_tx)[:msg_length])
        raw_bytes = self.receiveData()

        msg_rx = ibh_const.IBHLinkMSG()
        msg_rx.receiveSome(raw_bytes)

        self.received_telegram_check(msg_tx, msg_rx, ibh_const.TELE_HEADER_SIZE + size)

        if msg_rx.a in [ibh_const.MPI_READ_WRITE_DB, ibh_const.MPI_READ_WRITE_IO, ibh_const.MPI_READ_WRITE_M]:
            list_of_bytes = msg_rx.d[:msg_rx.data_cnt]  # type: list
            return list_of_bytes
        elif msg_rx.a in [ibh_const.MPI_READ_WRITE_CNT, ibh_const.MPI_READ_WRITE_TIM]:
            list_of_bytes = msg_rx.d[:2 * msg_rx.data_cnt]  # type: list
            return list_of_bytes
        else:
            return None

    def write_vals(self, data_type: str, data_address: int, offset: int, size: int, vals: bytes) -> bool:
        """
        :returns: Succeed of operation.
        :raises: TypeError, ValueError, DriverError, ConnectionError
        """
        if not type(vals) is bytes:
            raise TypeError("Given 'vals' of type {}, use bytes object".format(type(vals)))
        if len(vals) != size:
            raise ValueError("Length of byte array({}) is not equal to size of write{}".format(len(vals),size))
        if size > ibh_const.IBHLINK_WRITE_MAX or size <= 0:
            raise ValueError("size > IBHconst.IBHLINK_WRITE_MAX or size <= 0. Given:".format(size))
        elif data_type == 'E' or data_type == 'I':
            msg_tx = ibh_const.IBHLinkMSG(ln=ibh_const.TELE_HEADER_SIZE + size, b=ibh_const.MPI_READ_WRITE_IO,
                                          data_area=ibh_const.INPUT_AREA, data_adr=data_address,
                                          data_cnt=size, data_type=ibh_const.TASK_TDT_UINT8)
            ctypes.memmove(ctypes.addressof(msg_tx.d), vals, size)
        elif data_type == 'A' or data_type == 'O' or data_type == 'Q':
            msg_tx = ibh_const.IBHLinkMSG(ln=ibh_const.TELE_HEADER_SIZE + size, b=ibh_const.MPI_READ_WRITE_IO,
                                          data_area=ibh_const.OUTPUT_AREA, data_adr=data_address,
                                          data_cnt=size, data_type=ibh_const.TASK_TDT_UINT8)
            ctypes.memmove(ctypes.addressof(msg_tx.d), vals, size)
        elif data_type == 'M':
            msg_tx = ibh_const.IBHLinkMSG(ln=ibh_const.TELE_HEADER_SIZE + size, b=ibh_const.MPI_READ_WRITE_M,
                                          data_adr=data_address,
                                          data_cnt=size, data_type=ibh_const.TASK_TDT_UINT8)
            ctypes.memmove(ctypes.addressof(msg_tx.d), vals, size)
        elif data_type == 'D':
            msg_tx = ibh_const.IBHLinkMSG(ln=ibh_const.TELE_HEADER_SIZE + size, b=ibh_const.MPI_READ_WRITE_DB,
                                          data_area=offset >> 8, data_idx=offset,
                                          data_adr=data_address, data_cnt=size, data_type=ibh_const.TASK_TDT_UINT8)
            ctypes.memmove(ctypes.addressof(msg_tx.d), vals, size)
        elif size > ibh_const.IBHLINK_WRITE_MAX / 2:
            logger.warning("size > IBHconst.IBHLINK_WRITE_MAX/2")
            return False
        elif data_type == 'T':
            # TODO: implementation 'T'
            return False
        elif data_type == 'Z' or data_type == 'C':
            # TODO: implementation 'C'
            return False
        else:
            logger.warning("No valid data type")
            raise ValueError("No valid data type, given:{}".format(data_type))

        msg_tx.rx = ibh_const.MPI_TASK
        msg_tx.tx = ibh_const.HOST
        msg_tx.nr = self.msg_number
        msg_tx.device_adr = self.mpi_address
        msg_tx.func_code = ibh_const.TASK_TFC_WRITE

        self.msg_number += 1

        msg_length = ibh_const.MSG_HEADER_SIZE + ibh_const.TELE_HEADER_SIZE + size
        self.sendData(bytes(msg_tx)[:msg_length])

        raw_bytes = self.receiveData()

        msg_rx = ibh_const.IBHLinkMSG()
        msg_rx.receiveSome(raw_bytes)

        self.received_telegram_check(msg_tx, msg_rx, ibh_const.TELE_HEADER_SIZE)

        return True

    def sendData(self, raw_bytes: bytes) -> int:
        """
        :returns: Count of sent bytes.
        :raises: DriverError, ConnectionError
        """
        logger.debug("Sending:{}".format(raw_bytes))
        bytes_count = self._socket.send(raw_bytes)
        if bytes_count != len(raw_bytes):
            raise ToShortSendReceiveTelegramError(
                'Sent telegram is too short is {}, expected {}'.format(bytes_count, len(raw_bytes))
            )
        return bytes_count

    def receiveData(self) -> bytes:
        """
        :raises: DriverError, ConnectionError
        """
        raw_bytes = self._socket.recv(self.max_recv_bytes)
        logger.debug("Receiving:{}".format(raw_bytes))
        if len(raw_bytes) < ibh_const.MSG_HEADER_SIZE + ibh_const.TELE_HEADER_SIZE:
            if len(raw_bytes) == 0:
                self.drop_connection()
                raise SocketUnexpectedDisconnected('Zero length data received, closing socket')
            else:
                raise ToShortSendReceiveTelegramError(
                    'Received telegram is too short is {}, expected {}'.format(len(raw_bytes),
                                                                               ibh_const.MSG_HEADER_SIZE + ibh_const.TELE_HEADER_SIZE)
                )
        return raw_bytes

    def received_telegram_check(self, tx: ibh_const.IBHLinkMSG, rx: ibh_const.IBHLinkMSG, expeceted_rx_ln: int) -> None:
        """
        :raises: DriverError
        """
        if rx.f != ibh_const.CON_OK:
            raise FaultsInTelegramError('Received telegram error code non zero value, error code(f)={0:#x}'.format(rx.f))
        elif rx.tx != tx.rx or rx.rx != tx.tx:
            raise CorruptedTelegramError('Received telegram transmiter(tx), receiver(rx) not match')
        elif rx.ln != expeceted_rx_ln:
            raise CorruptedTelegramError(
                'Received telegram length message not correct {}, expected {}'.format(rx.ln, expeceted_rx_ln)
            )
        elif rx.nr != tx.nr:
            raise CorruptedTelegramError('Sent and received telegram message number(nr) not match')
        elif rx.a != tx.b:
            raise CorruptedTelegramError('Sent and received telegram command code(b), response code(a) not match')
        elif rx.device_adr != tx.device_adr:
            raise CorruptedTelegramError('Sent and received telegram device address(device_adr) not match')
        elif rx.data_area != tx.data_area:
            raise CorruptedTelegramError('Sent and received telegram data area not match');
        elif rx.data_adr != tx.data_adr:
            raise CorruptedTelegramError('Sent and received telegram data address not match');
        elif rx.data_idx != tx.data_idx:
            raise CorruptedTelegramError('Sent and received telegram data index not match');
        elif rx.data_cnt != tx.data_cnt:
            raise CorruptedTelegramError('Sent and received telegram data count not match');
        elif rx.data_type != tx.data_type:
            raise CorruptedTelegramError('Sent and received telegram data type not match');
        elif rx.func_code != tx.func_code:
            raise CorruptedTelegramError('Sent and received telegram function code not match');


if __name__ == "__main__":
    driver = IbhLinkDriver('192.168.1.15', 1099, 2)
    driver.timeout = 5
    driver.connect_plc()
    print("connected {}".format(driver.connected))

    print(driver.read_vals('D', 100, 0, 1))

    driver.disconnect_plc()
