import ctypes
from ctypes import Structure, c_uint8, c_uint16

MAX_PATH = 260

NOT_CONN = 1
CONN_FAILED = 2
RW_FAILED = 3

IBHLINK_PORT = 1099
IBHLINK_READ_MAX = 222
IBHLINK_WRITE_MAX = 212

MPI_TASK = 3
HOST = 255
MSG_HEADER_SIZE = 8
TELE_HEADER_SIZE = 8

INPUT_AREA = 0
OUTPUT_AREA = 1

MPI_READ_WRITE_DB = 0x31
MPI_GET_OP_STATUS = 0x32
MPI_READ_WRITE_M = 0x33
MPI_READ_WRITE_IO = 0x34
MPI_READ_WRITE_CNT = 0x35
MPI_READ_WRITE_TIM = 0x36
MPI_DISCONNECT = 0x3F

TASK_TDT_UINT8 = 5
TASK_TDT_UINT16 = 6
TASK_TFC_READ = 1
TASK_TFC_WRITE = 2

CON_OK = 0  # service could be executed without an error
CON_UE = 1  # timeout from remote station remote station remote station has not responded within 1 sec.timeout
CON_RR = 2  # resource unavailable remote station remote station has no left buffer space for the requested service
CON_RS = 3  # requested function of master is not activated within the remote station. remote station the connection
# seems to be closed in the remote station.try to send command again.
CON_NA = 17  # no response of the remote station remote station check network wiring, check remote address, check
# baud rate
CON_DS = 18  # master not into the logical token ring network in general check master DP-Address or
# highest-station-Addres s of other masters. Examine bus wiring to bus short circuits.
CON_LR = 20  # Resource of the local FDL controller not available or not sifficient. HOST too many messages.
# no more segments in DEVICE free
CON_IV = 21  # the specified msg.data_cnt parameter invalid HOST check the limit of 222 bytes (read)
# respectively 212 bytes (write) in msg.data_cnt
CON_TO = 48  # timeout, the request message was accepted but no indication is sent back by the remote station
# remote station MPI protocol error, or station not presentor
CON_SE = 57  # Sequence fault, internal state machine error. Remote station does not react like awaited
# or a reconnection was retried while connection is already open or device has no SAPs left to open connection channel
REJ_IV = 0x85  # specified offset address out of limits or not known in the remote station HOST please check
# msg.data_adr if present or offset parameter in request message
REJ_PDU = 0x86  # wrong PDU coding in the MPI response of the remote station DEVICE contact hotline
REJ_OP = 0x87  # specified length to write or to read results in an access outside the limits HOST please check
# msg.data_cnt length in request message

dataArray = c_uint8 * 240

class IBHLinkMSG(Structure):

    _pack_ = 1
    _fields_ = [
        ('rx', c_uint8),  # Receiver Code
        ('tx', c_uint8),  # Transmitter Code
        ('ln', c_uint8),  # Data length of the Message
        ('nr', c_uint8),  # Identification Code
        ('a', c_uint8),  # Response Code
        ('f', c_uint8),  # Error Code
        ('b', c_uint8),  # Command Code
        ('e', c_uint8),  # Extention Code
        ('device_adr', c_uint8),  # Remote partner address
        ('data_area', c_uint8),  # Data area
        ('data_adr', c_uint16),  # Data address
        ('data_idx', c_uint8),  # Data index
        ('data_cnt', c_uint8),  # Data quantity
        ('data_type', c_uint8),  # Data type
        ('func_code', c_uint8),  # Function code
        ('d', dataArray)  # User specific data
    ]

    def receiveSome(self, bytes_array):
        fit = min(len(bytes_array), ctypes.sizeof(self))
        ctypes.memmove(ctypes.addressof(self), bytes_array, fit)
    def cleanUp(self):
        ctypes.memset(ctypes.addressof(self), 0, ctypes.sizeof(self))
if __name__ == "__main__":
    struct = IBHLinkMSG(1,2,3,4,5,6,7,8,1,2,3,4,5,6,7,dataArray(2,3,4,3,1,5,6,2))
    struct.ln = 4
    for i,x in enumerate(struct.d):
        print(x)
        if i >= struct.ln - 1:
            break