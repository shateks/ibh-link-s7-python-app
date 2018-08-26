import socket
import ctypes
import IBHconst

class ToShortSendReceiveTelegramError(Exception):
    pass

class CorruptedTelegramError(Exception):
    pass

class FaultsInTelegramError(Exception):
    pass

class IbhLinkServer:
    def __init__(self, ip_addr, ip_port, mpi_addr):
        self.connected = False
        self.ip_address = ip_addr
        self.ip_port = ip_port
        if mpi_addr < 0 or mpi_addr > 126:
            print("mpi_addr < 0 or mpi_addr > 126")
        self.mpi_address = mpi_addr
        self.msg_number = 0
        self.max_recv_bytes = 512

    def startListen(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(self.ip_address, self.ip_port)
            s.listen(1)
            conn,addr = s.accept()
            with conn:
                print('Connected by', addr)
                while True:
                    data = conn.recv(1024)
                    # pass data to function
                    if not data: break
                    conn.sendall(data)


    def stopListen(self):
        pass


    def connect_plc(self):
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(5.0)
            self._socket.connect((self.ip_address, self.ip_port))
            self.connected = True
        except Exception as e:
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

        op_status = int.from_bytes(msg_rx.d[:2], byteorder='big')
        if op_status == 0:
            return 'STOP'
        elif op_status == 1:
            return 'START'
        elif op_status == 2:
            return 'RUN'
        else:
            return 'UNKNOWN'

    def produce_respose(self, data):
        msg_rx = IBHconst.IBHLinkMSG()
        msg_rx.receiveSome(data)

        self.received_telegram_check(msg_rx, IBHconst.TELE_HEADER_SIZE)

        msg_tx = IBHconst.IBHLinkMSG()
        msg_tx.rx = msg_rx.tx
        msg_tx.tx = msg_rx.rx
        msg_tx.ln = ?
        msg_tx.nr = msg_rx.nr
        msg_tx.a = msg_rx.b
        msg_tx.f = ?
        msg_tx.b = 0
        msg_tx.e = 0
        msg_tx.device_adr = self.mpi_address
        msg_tx.data_area =
        msg_tx.data_adr =
        msg_tx.data_idx =
        msg_tx.data_cnt =
        msg_tx.data_type = IBHconst.TASK_TDT_UINT8 | IBHconst.TASK_TDT_UINT16
        msg_tx.func_code = IBHconst.TASK_TFC_READ | IBHconst.TASK_TFC_WRITE
        msg_tx.d =

        if msg_rx.b == IBHconst.MPI_READ_WRITE_DB:
            ='D'
            db_number = msg_rx.data_adr
            db_offset = (msg_rx.data_area << 8) + msg_rx.data_idx
        elif msg_rx.b == IBHconst.MPI_GET_OP_STATUS:
            pass
        elif msg_rx.b == IBHconst.MPI_READ_WRITE_M:
            ='M'
            data_address = msg_rx.data_adr
        elif msg_rx.b == IBHconst.MPI_READ_WRITE_IO:
            pass
        elif msg_rx.b == IBHconst.MPI_READ_WRITE_CNT:
            pass
        elif msg_rx.b == IBHconst.MPI_DISCONNECT:
            pass

        self._socket.shutdown(socket.SHUT_RDWR)
        self._socket.close()
        self.connected = False


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
        bytes_count = self._socket.send(raw_bytes)
        if bytes_count != len(raw_bytes):
            raise ToShortSendReceiveTelegramError(
                'Sent telegram is too short is {}, expected {}'.format(bytes_count, len(raw_bytes))
            )
        return bytes_count

    def receiveData(self):
        raw_bytes = self._socket.recv(self.max_recv_bytes)

        if len(raw_bytes) < IBHconst.MSG_HEADER_SIZE + IBHconst.TELE_HEADER_SIZE:
            raise ToShortSendReceiveTelegramError(
                'Received telegram is too short is {}, expected {}'.format(len(raw_bytes),
                                                                           IBHconst.MSG_HEADER_SIZE + IBHconst.TELE_HEADER_SIZE)
            )

        return raw_bytes

    def received_telegram_check(self, rx, expeceted_rx_ln):
        if rx.rx != self.mpi_address:
            raise CorruptedTelegramError('Received telegram transmiter(tx), receiver(rx) not match')
        elif rx.ln != expeceted_rx_ln:
            raise CorruptedTelegramError(
                'Received telegram length message not correct {}, expected {}'.format(rx.ln, expeceted_rx_ln)
            )

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



if __name__ == "__main__":
    driver = IbhLinkServer('192.168.1.15', 1099, 2)
    # driver = ibhlinkdriver('127.0.0.1', 1099, 2)
    driver.connect_plc()
    print("connected {}".format(driver.connected))
    # print(driver.plc_get_run())
    # print(driver.read_vals('M',10,10,1))
    print(driver.read_vals('D', 0, 100, 1))
    # print(driver.plc_get_run())
    driver.disconnect_plc()
