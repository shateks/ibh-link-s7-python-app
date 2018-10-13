import socket
import ibhlinkdriver
import IBHconst as c
from unittest import TestCase,mock
import faulthandler

f1 = open("crash.txt",'w')
faulthandler.enable(file=f1)

import logging

# create logger with 'spam_application'
logger = logging.getLogger('spam_application')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('spam.log')
fh.setLevel(logging.DEBUG)

# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)

class TestIbhlinkdriver(TestCase):

    ipAddr = '192.168.1.15'
    ipPort = 1099
    mpiAddr = 2




    def setUp(self):
        self.patcher = mock.patch('socket.socket', autospec=socket.socket)
        # self.patcher = mock.patch('socket.socket')
        self.addCleanup(self.patcher.stop)
        self._socket_class = self.patcher.start()
        self._instance_socket_class = self._socket_class.return_value
        self.driver = ibhlinkdriver.IbhLinkDriver(self.ipAddr, self.ipPort, self.mpiAddr)

    def test_plc_get_run(self):
        raw_bytes_msg_struct = bytes(c.IBHLinkMSG( rx=c.MPI_TASK, tx=c.HOST, nr=0, ln=c.MSG_HEADER_SIZE,
                                                   b=c.MPI_GET_OP_STATUS, device_adr=self.mpiAddr))
        sent_bytes = raw_bytes_msg_struct[:16]
        self._instance_socket_class.send.return_value = len(sent_bytes)
        self._instance_socket_class.recv.return_value = bytes([c.HOST, c.MPI_TASK, 10, self.driver.msg_number, 0x32, 0,
                                                               0, 0, self.driver.mpi_address, 0, 0, 0, 0, 0, 0, 0, 2, 0])
        self.driver.connect_plc()
        self.assertEqual("RUN",self.driver.plc_get_run(),"PLC state not properly returned")
        self._instance_socket_class.send.assert_called_once_with(sent_bytes)

    def test_write_vals_MB10(self):
        var = 33
        msg_struct = c.IBHLinkMSG(rx=c.MPI_TASK, tx=c.HOST, ln=c.MSG_HEADER_SIZE+1, nr=0,
                                  b=c.MPI_READ_WRITE_M, device_adr=self.mpiAddr,
                                  data_adr=10, data_cnt=1, data_type=c.TASK_TDT_UINT8,
                                  func_code=c.TASK_TFC_WRITE, d=c.dataArray(var))
        raw_bytes_msg_struct = bytes(msg_struct)
        sent_bytes = raw_bytes_msg_struct[:17]
        msg_struct.rx,msg_struct.tx = msg_struct.tx,msg_struct.rx
        msg_struct.a = msg_struct.b
        msg_struct.ln = 8
        raw_bytes_msg_struct = bytes(msg_struct)
        expected_bytes = raw_bytes_msg_struct[:16]
        self._instance_socket_class.recv.return_value = expected_bytes
        self._instance_socket_class.send.return_value = len(sent_bytes)
        self.driver.connect_plc()
        self.driver.write_vals(data_type='M', data_address=10, offset=0, size=1, vals=bytes([var]))
        self._instance_socket_class.send.assert_called_once_with(sent_bytes)



