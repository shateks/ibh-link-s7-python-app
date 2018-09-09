import logging
import socket
import ctypes
import IBHconst


logger = logging.getLogger('gui logger')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('gui.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(relativeCreated)6d %(threadName)s: %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

logger.debug("Hallo")

class DriverError(Exception):
    pass

class ToShortSendReceiveTelegramError(DriverError):
    pass

class CorruptedTelegramError(DriverError):
    pass

class FaultsInTelegramError(DriverError):
    pass

class ibhlinkdriver:
    def __init__(self, ip_addr, ip_port, mpi_addr):
        self.connected = False
        self.ip_address = ip_addr
        self.ip_port = ip_port
        if mpi_addr < 0 or mpi_addr > 126:
            print("mpi_addr < 0 or mpi_addr > 126")
        self.mpi_address = mpi_addr
        self.msg_number = 0
        self.max_recv_bytes = 512

    def connect_plc(self):
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # self._socket.settimeout(5.0)
            self._socket.connect((self.ip_address, self.ip_port))
            logger.debug("Connected to:{}".format(self.ip_address))
            self.connected = True
        except ConnectionRefusedError as e:
            print("Unhandled exception {}".format(e))
            self.connected = False

    def disconnect_plc(self):
        if not self.connected:
            return

        msg_tx = IBHconst.IBHLinkMSG(rx=IBHconst.MPI_TASK, tx=IBHconst.HOST, nr=self.msg_number,
                                     ln=IBHconst.MSG_HEADER_SIZE, b=IBHconst.MPI_DISCONNECT,
                                     device_adr=self.mpi_address)
        self.msg_number += 1

        msg_length = IBHconst.MSG_HEADER_SIZE + IBHconst.TELE_HEADER_SIZE

        self.sendData(bytes(msg_tx)[:msg_length])

        raw_bytes = self.receiveData()

        msg_rx = IBHconst.IBHLinkMSG()
        msg_rx.receiveSome(raw_bytes)

        self.received_telegram_check(msg_tx, msg_rx, IBHconst.TELE_HEADER_SIZE)

        self._socket.shutdown(socket.SHUT_RDWR)
        self._socket.close()
        logger.debug("Disconnected:{}".format(self.ip_address))
        self.connected = False

    def plc_get_run(self):
        msg_tx = IBHconst.IBHLinkMSG(rx=IBHconst.MPI_TASK, tx=IBHconst.HOST, nr=self.msg_number,
                                     ln=IBHconst.MSG_HEADER_SIZE, b=IBHconst.MPI_GET_OP_STATUS,
                                     device_adr=self.mpi_address)
        self.msg_number += 1

        self.sendData(bytes(msg_tx)[:IBHconst.MSG_HEADER_SIZE + IBHconst.TELE_HEADER_SIZE])

        raw_bytes = self.receiveData()

        msg_rx = IBHconst.IBHLinkMSG()
        msg_rx.receiveSome(raw_bytes)

        self.received_telegram_check(msg_tx, msg_rx, IBHconst.TELE_HEADER_SIZE + 2)

        op_status = int.from_bytes(msg_rx.d[:2], byteorder='little')
        if op_status == 0:
            return 'STOP'
        elif op_status == 1:
            return 'START'
        elif op_status == 2:
            return 'RUN'
        else:
            return 'UNKNOWN'

    def read_vals(self, data_type, data_number, db_number, size):

        if size > IBHconst.IBHLINK_READ_MAX or size <= 0:
            print("if size > IBHconst.IBHLINK_READ_MAX or size <= 0:")
            return None
        elif data_type == 'E' or data_type == 'I':
            msg_tx = IBHconst.IBHLinkMSG(b=IBHconst.MPI_READ_WRITE_IO, data_area=IBHconst.INPUT_AREA, data_adr=data_number,
                                         data_cnt=size, data_type=IBHconst.TASK_TDT_UINT8)
        elif data_type == 'A' or data_type == 'O':
            msg_tx = IBHconst.IBHLinkMSG(b=IBHconst.MPI_READ_WRITE_IO, data_area=IBHconst.OUTPUT_AREA,
                                         data_adr=data_number, data_cnt=size, data_type=IBHconst.TASK_TDT_UINT8)
        elif data_type == 'M':
            msg_tx = IBHconst.IBHLinkMSG(b=IBHconst.MPI_READ_WRITE_M, data_area=IBHconst.INPUT_AREA, data_adr=data_number,
                                         data_cnt=size, data_type=IBHconst.TASK_TDT_UINT8)
        elif data_type == 'D':
            msg_tx = IBHconst.IBHLinkMSG(b=IBHconst.MPI_READ_WRITE_DB, data_area=data_number >> 8, data_idx=data_number,
                                         data_adr=db_number, data_cnt=size, data_type=IBHconst.TASK_TDT_UINT8)
        elif size > IBHconst.IBHLINK_READ_MAX / 2:
            print("size > IBHconst.IBHLINK_READ_MAX/2")
            return None
        elif data_type == 'T':
            # TODO: implementation read 'T'
            pass
        elif data_type == 'Z' or data_type == 'C':
            # TODO: implementation read 'C'
            pass
        else:
            print("No valid data type")
            return None

        msg_tx.rx = IBHconst.MPI_TASK
        msg_tx.tx = IBHconst.HOST
        msg_tx.ln = IBHconst.TELE_HEADER_SIZE
        msg_tx.nr = self.msg_number
        msg_tx.device_adr = self.mpi_address
        msg_tx.func_code = IBHconst.TASK_TFC_READ

        self.msg_number += 1
        msg_length = IBHconst.MSG_HEADER_SIZE + IBHconst.TELE_HEADER_SIZE
        self.sendData(bytes(msg_tx)[:msg_length])

        raw_bytes = self.receiveData()

        msg_rx = IBHconst.IBHLinkMSG()
        msg_rx.receiveSome(raw_bytes)

        self.received_telegram_check(msg_tx, msg_rx, IBHconst.TELE_HEADER_SIZE + size)

        if msg_rx.a in [IBHconst.MPI_READ_WRITE_DB, IBHconst.MPI_READ_WRITE_IO, IBHconst.MPI_READ_WRITE_M]:
            list_of_bytes = msg_rx.d[:msg_rx.data_cnt]  # type: list
            return list_of_bytes
        elif msg_rx.a in [IBHconst.MPI_READ_WRITE_CNT, IBHconst.MPI_READ_WRITE_TIM]:
            list_of_bytes = msg_rx.d[:2 * msg_rx.data_cnt]  # type: list
            return list_of_bytes
        else:
            return None

    def write_vals(self, data_type, data_number, db_number, size, vals):
        # TODO: implementacja write
        if not type(vals) is bytes:
            raise TypeError("Given 'vals' of type {}, use bytes object".format(type(vals)))
        if size > IBHconst.IBHLINK_WRITE_MAX or size <= 0:
            print("if size > IBHconst.IBHLINK_WRITE_MAX or size <= 0:")
            return None
        elif data_type == 'E' or data_type == 'I':
            msg_tx = IBHconst.IBHLinkMSG(ln=IBHconst.TELE_HEADER_SIZE + size, b=IBHconst.MPI_READ_WRITE_IO,
                                         data_area=IBHconst.INPUT_AREA, data_adr=data_number,
                                         data_cnt=size, data_type=IBHconst.TASK_TDT_UINT8)
            ctypes.memmove(ctypes.addressof(msg_tx.d), vals, size)
        elif data_type == 'A' or data_type == 'O':
            msg_tx = IBHconst.IBHLinkMSG(ln=IBHconst.TELE_HEADER_SIZE + size, b=IBHconst.MPI_READ_WRITE_IO,
                                         data_area=IBHconst.OUTPUT_AREA, data_adr=data_number,
                                         data_cnt=size, data_type=IBHconst.TASK_TDT_UINT8)
            ctypes.memmove(ctypes.addressof(msg_tx.d), vals, size)
        elif data_type == 'M':
            msg_tx = IBHconst.IBHLinkMSG(ln=IBHconst.TELE_HEADER_SIZE + size, b=IBHconst.MPI_READ_WRITE_M,
                                         data_adr=data_number,
                                         data_cnt=size, data_type=IBHconst.TASK_TDT_UINT8)
            ctypes.memmove(ctypes.addressof(msg_tx.d), vals, size)
        elif data_type == 'D':
            msg_tx = IBHconst.IBHLinkMSG(ln=IBHconst.TELE_HEADER_SIZE + size, b=IBHconst.MPI_READ_WRITE_DB,
                                         data_area=data_number >> 8, data_idx=data_number,
                                         data_adr=db_number, data_cnt=size, data_type=IBHconst.TASK_TDT_UINT8)
            ctypes.memmove(ctypes.addressof(msg_tx.d), vals, size)
        elif size > IBHconst.IBHLINK_WRITE_MAX / 2:
            print("size > IBHconst.IBHLINK_WRITE_MAX/2")
            return None
        elif data_type == 'T':
            # TODO: implementacja read 'T'
            pass
        elif data_type == 'Z' or data_type == 'C':
            # TODO: implementacja read 'C'
            pass
        else:
            print("No valid data type")
            return None

        msg_tx.rx = IBHconst.MPI_TASK
        msg_tx.tx = IBHconst.HOST
        msg_tx.nr = self.msg_number
        msg_tx.device_adr = self.mpi_address
        msg_tx.func_code = IBHconst.TASK_TFC_WRITE

        self.msg_number += 1

        msg_length = IBHconst.MSG_HEADER_SIZE + IBHconst.TELE_HEADER_SIZE + size
        self.sendData(bytes(msg_tx)[:msg_length])

        raw_bytes = self.receiveData()

        msg_rx = IBHconst.IBHLinkMSG()
        msg_rx.receiveSome(raw_bytes)

        self.received_telegram_check(msg_tx, msg_rx, IBHconst.TELE_HEADER_SIZE)

        return True

    def sendData(self, raw_bytes):
        logger.debug("Sending:{}".format(raw_bytes))
        bytes_count = self._socket.send(raw_bytes)
        if bytes_count != len(raw_bytes):
            raise ToShortSendReceiveTelegramError(
                'Sent telegram is too short is {}, expected {}'.format(bytes_count, len(raw_bytes))
            )
        return bytes_count

    def receiveData(self):
        raw_bytes = self._socket.recv(self.max_recv_bytes)
        logger.debug("Receiving:{}".format(raw_bytes))

        if len(raw_bytes) < IBHconst.MSG_HEADER_SIZE + IBHconst.TELE_HEADER_SIZE:
            raise ToShortSendReceiveTelegramError(
                'Received telegram is too short is {}, expected {}'.format(len(raw_bytes),
                 IBHconst.MSG_HEADER_SIZE + IBHconst.TELE_HEADER_SIZE)
            )

        return raw_bytes

    def received_telegram_check(self, tx, rx, expeceted_rx_ln):
        if rx.f != IBHconst.CON_OK:
            raise FaultsInTelegramError('Received telegram error code non zero value, error code(f)={}'.format(rx.f))
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

    def GetMB(self, Nr):
        val = self.read_vals('M', Nr, 0, 1)
        return val[0]

    def GetMW(self, Nr):
        val = self.read_vals('M', Nr, 0, 2)
        return int.from_bytes(val, byteorder='big')

    def GetMD(self, Nr):
        val = self.read_vals('M', Nr, 0, 4)
        return int.from_bytes(val, byteorder='big')

    def GetM(self, Nr, BitNr):
        val = self.read_vals('M', Nr, 0, 1)
        mask = 1 << BitNr
        return val & mask != 0

    def SetMB(self, Nr, val):
        self.write_vals('M', Nr, 0, 1, val)

    # TODO: Sprawdź metody czy nie trzeba ustawić byteorder
    def SetMW(self, Nr, val):
        self.write_vals('M', Nr, 0, 2, val)

    def SetMD(self, Nr, val):
        self.write_vals('M', Nr, 0, 4, val)

    def SetM(self, Nr, BitNr, val):
        if BitNr > 7:
            raise ValueError("Given 'BitNr' greater than 7".format(type(BitNr)))
        old_val = self.read_vals('M', Nr, 0, 1)
        mask = 1 << BitNr

        if val:
            new_val = old_val | mask
        else:
            new_val = old_val & (0xff - mask)

        self.write_vals('M', Nr, 0, 1, new_val)


    def GetEB(self, Nr, val):
        pass

    def GetEW(self, Nr, val):
        pass

    def GetED(self, Nr, val):
        pass

    def GetE(self, Nr, BitNr, val):
        pass

    def SetEB(self, Nr, val):
        pass

    def SetEW(self, Nr, val):
        pass

    def SetED(self, Nr, val):
        pass

    def SetE(self, Nr, BitNr, val):
        pass

    def GetAB(self, Nr, val):
        pass

    def GetAW(self, Nr, val):
        pass

    def GetAD(self, Nr, val):
        pass

    def GetA(self, Nr, BitNr, val):
        pass

    def SetAB(self, Nr, val):
        pass

    def SetAW(self, Nr, val):
        pass

    def SetAD(self, Nr, val):
        pass

    def SetA(self, Nr, BitNr, val):
        pass

    def GetDBB(self, Nr, DBNr, val):
        pass

    def GetDBW(self, Nr, DBNr, val):
        pass

    def GetDBD(self, Nr, DBNr, val):
        pass

    def GetDBX(self, Nr, DBNr, BitNr, val):
        pass

    def SetDBB(self, Nr, DBNr, val):
        pass

    def SetDBW(self, Nr, DBNr, val):
        pass

    def SetDBD(self, Nr, DBNr, val):
        pass

    def SetDBX(self, Nr, DBNr, BitNr, val):
        pass


if __name__ == "__main__":
    driver = ibhlinkdriver('192.168.1.15', 1099, 2)
    # driver = ibhlinkdriver('127.0.0.1', 1099, 2)
    driver.connect_plc()
    print("connected {}".format(driver.connected))
    # print(driver.plc_get_run())
    # print(driver.read_vals('M',10,10,1))
    print(driver.read_vals('D', 0, 100, 1))
    # print(driver.plc_get_run())
    driver.disconnect_plc()
