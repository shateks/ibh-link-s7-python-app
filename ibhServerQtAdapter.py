from PyQt5.QtCore import QObject, QThread, pyqtSlot, pyqtSignal
import IBHconst
from ibhLinkServer import IbhLinkServer


class Worker(QObject):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._server = IbhLinkServer

    @pyqtSlot()
    def start(self, ip_address: str, ip_port: int, mpi_address: int):
        self._server.__init__(ip_address, ip_port, mpi_address)
        self._server.startServer()

    @pyqtSlot()
    def stop(self):
        self._server.stopListen()


import socket
import threading

class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen(self):
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            client.settimeout(60)
            threading.Thread(target = self.listenToClient,args = (client,address)).start()

    def listenToClient(self, client, address):
        size = 1024
        while True:
            try:
                data = client.recv(size)
                if data:
                    # Set the response to echo back the recieved data
                    response = data
                    client.send(response)
                else:
                    raise error('Client disconnected')
            except:
                client.close()
                return False

if __name__ == "__main__":
    while True:
        port_num = input("Port? ")
        try:
            port_num = int(port_num)
            break
        except ValueError:
            pass

    ThreadedServer('',port_num).listen()