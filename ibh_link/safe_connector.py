from PyQt5 import QtCore
import threading
import socket
from queue import Queue


class SafeConnector(QtCore.QObject):

    signal = QtCore.pyqtSignal(tuple)

    def __init__(self, parent=None):
        # initialise in Qt thread
        super(QtCore.QObject, self).__init__(parent)
        self._queue = Queue()
        self.rsock, self.wsock = socket.socketpair()
        self.notifier = QtCore.QSocketNotifier(
            self.rsock.fileno(), QtCore.QSocketNotifier.Read)
        self.notifier.activated.connect(self.recv)

    def recv(self):
        # runs in Qt thread after it's been woken up by QSocketNotifier
        self.rsock.recv(1)
        self.signal.emit(self._queue.get())

    def emit(self, *args):
        # runs in any thread
        self._queue.put(args)
        self.wsock.send(b'1')

if __name__ == '__main__':

    from PyQt5 import QtCore, QtWidgets
    import time


    class PythonThread(threading.Thread):
        def __init__(self, connector, *args, **kwargs):
            threading.Thread.__init__(self, *args, **kwargs)
            self.connector = connector
            self.daemon = True

        def emit_signal(self):
            # self.connector.emit(QtCore.pyqtSignal(str,name='sig'), str(time.time()))
            self.connector.emit(str(time.strftime('%H:%M:%S%')) + str(time.process_time()))

        def run(self):
            while True:
                time.sleep(1)
                self.emit_signal()


    app = QtWidgets.QApplication([])
    mainwin = QtWidgets.QMainWindow()
    label = QtWidgets.QLabel(mainwin)
    mainwin.setCentralWidget(label)

    connector = SafeConnector()
    python_thread = PythonThread(connector)
    connector.signal.connect(label.setText)
    python_thread.start()

    mainwin.show()
    app.exec()