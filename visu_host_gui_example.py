import sys, logging
from itertools import cycle

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTextEdit, QMessageBox
from PyQt5.QtGui import QPalette, QPixmap

from ibh_link.utils import ConfReader, enable_crash_report
from ui_ibh_client_visu_host import *
from ibh_link.ibh_client_qt_adapter import *
from PyQt5.QtCore import QThread, QTimer, Qt
from ibh_link import utils

enable_crash_report('crash_visu_host_gui.txt')

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

class QTextEditLoggerHandler(logging.Handler, QObject):

    def __init__(self, widget: QWidget):
        logging.Handler.__init__(self)
        QObject.__init__(self)
        self.setLevel(logging.DEBUG)
        self.add_message.connect(widget.log)

    def emit(self, record):
        msg = self.format(record)
        self.add_message.emit(msg, record.levelno)

    add_message = pyqtSignal(str, int)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self._images_no_connection = cycle((QPixmap('./img/no_conn_1.png', ), QPixmap('./img/no_conn_2.png')))
        self._images_connection_ok = cycle((QPixmap('./img/arrow1.svg'), QPixmap('./img/arrow2.svg'),
                                            QPixmap('./img/arrow3.svg'), QPixmap('./img/arrow4.svg')))
        self._images_communication_error = cycle((QPixmap('./img/err_conn_1.png'), QPixmap('./img/err_conn_2.png')))
        self._connection_animation_number = 0
        self._communication_state = CommunicationStatus.no_connection

        self._connection_status_label = QLabel()
        self._message_label = QLabel('...')
        self._plc_status_label = QLabel()

        self._run_color_palette = QPalette()
        self._run_color_palette.setColor(QPalette.Window, Qt.darkGreen)
        self._run_color_palette.setColor(QPalette.WindowText, Qt.green)

        self._stop_color_palette = QPalette()
        self._stop_color_palette.setColor(QPalette.Window, Qt.darkRed)
        self._stop_color_palette.setColor(QPalette.WindowText, Qt.red)

        self._start_up_color_palette = QPalette()
        self._start_up_color_palette.setColor(QPalette.Window, Qt.darkYellow)
        self._start_up_color_palette.setColor(QPalette.WindowText, Qt.yellow)

        self._unknown_color_palette = QPalette()
        self._unknown_color_palette.setColor(QPalette.Window, Qt.darkGray)
        self._unknown_color_palette.setColor(QPalette.WindowText, Qt.white)

        self._plc_status_label.setFixedWidth(100)
        self._plc_status_label.setAutoFillBackground(True)
        self._plc_status_label.setAlignment(Qt.AlignCenter)

        self.ui.statusbar.setMinimumHeight(40)
        self.ui.statusbar.addPermanentWidget(self._plc_status_label, 1)
        self.ui.statusbar.addPermanentWidget(self._message_label,10)
        self.ui.statusbar.addPermanentWidget(self._connection_status_label, 0)

        self._graphics_timer = QTimer()
        self._graphics_timer.timeout.connect(self.animate_connection_state)
        self._graphics_timer.start(400)

        self.mutable_tabs = []

    def add_debug_console(self):
        self.ui._console_widget = QWidget()
        self.ui._console_layout = QVBoxLayout()
        self.ui._console_text_edit = QTextEdit()
        self.ui._console_text_edit.setReadOnly(True)
        self.ui._console_text_edit.document().setMaximumBlockCount(100000)
        self.ui._console_layout.addWidget(self.ui._console_text_edit)
        self.ui._console_widget.setLayout(self.ui._console_layout)
        self.ui.tabWidget.addTab(self.ui._console_widget, 'DEBUG')

    @pyqtSlot(str, int)
    def log(self, msg:str, level:int):
        if level >= logging.WARNING:
            self.ui._console_text_edit.setTextColor(Qt.red)
        else:
            self.ui._console_text_edit.setTextColor(Qt.black)
        self.ui._console_text_edit.append(msg)

    @pyqtSlot(CommunicationStatus)
    def change_connection_visu_state(self, state):
        self._communication_state = state
        if self._communication_state == CommunicationStatus.succeed:
            for tab in self.mutable_tabs:
                tab.setEnabled(True)
                self._message_label.setText('Connected to PLC.')
        elif self._communication_state == CommunicationStatus.no_connection:
            for tab in self.mutable_tabs:
                tab.setEnabled(False)
                self._message_label.setText('System error: No connection to adapter.')
        elif self._communication_state == CommunicationStatus.communication_error:
            for tab in self.mutable_tabs:
                tab.setEnabled(False)
                self._message_label.setText('System error: Connected to adapter, but PLC communication errors occurred.')
    @pyqtSlot()
    def animate_connection_state(self):
        if self._communication_state == CommunicationStatus.succeed:
            self._connection_status_label.setPixmap(self._images_connection_ok.__next__())
        elif self._communication_state == CommunicationStatus.no_connection:
            self._connection_status_label.setPixmap(self._images_no_connection.__next__())
            self.display_plc_status('UNKNOWN')
        elif self._communication_state == CommunicationStatus.communication_error:
            self._connection_status_label.setPixmap(self._images_communication_error.__next__())

    @pyqtSlot(str)
    def display_plc_status(self, op_status):
        if op_status == 'RUN':
            self._plc_status_label.setPalette(self._run_color_palette)
        elif op_status == 'STOP':
            self._plc_status_label.setPalette(self._stop_color_palette)
        elif op_status == 'START':
            self._plc_status_label.setPalette(self._start_up_color_palette)
        else:
            self._plc_status_label.setPalette(self._unknown_color_palette)
        self._plc_status_label.setText(op_status)

    @pyqtSlot(str)
    def display_message_label(self, msg):
        self._message_label.setText(msg)

if (__name__ == '__main__' ):

    app = QApplication(sys.argv)
    try:
        configuration = ConfReader('config.ini')
        ip_address = configuration.plc_tcp_ip_address
        ip_port = configuration.plc_tcp_ip_port
        mpi_address = configuration.plc_mpi_address
        refresh_time = configuration.refresh_time
        debug_console = configuration.console
        screens_list = configuration.screens
    except FileExistsError as e:
        main_widget = QMessageBox()
        main_widget.setWindowTitle('Initialization error')
        main_widget.setInformativeText('Problems while reading configuration file.')
        main_widget.setIcon(QMessageBox.Critical)
        main_widget.setText(str(e))
    except Exception as e:
        main_widget = QMessageBox()
        main_widget.setWindowTitle('Initialization error')
        main_widget.setInformativeText('Problems while reading configuration file.')
        main_widget.setIcon(QMessageBox.Critical)
        main_widget.setText(str(e))
    else:
        main_widget = MainWindow()
        if debug_console:
            main_widget.add_debug_console()
            log_handler = QTextEditLoggerHandler(main_widget)
            root_logger.addHandler(log_handler)
            root_logger.debug('<<<<<<<<<<<<  Adding screens files to tabs, PyQt.uic.Load.Ui logger output  >>>>>>>>>>>>>')
        for screen_name, file_name in screens_list:
            try:
                wi = uic.loadUi(file_name)
                main_widget.ui.tabWidget.addTab(wi, screen_name)
                main_widget.mutable_tabs.append(wi)
            except FileNotFoundError as e:
                 root_logger.warning("\nReading screen file problem\n{}".format(e))
        else:
            root_logger.debug('<<<<<<<<<<<<  End of adding screens >>>>>>>>>>>>>')
        worker = Worker(ip_address, mpi_address)
        worker.change_communication_parameters(ip_address, ip_port, mpi_address)
        worker.stay_connected = True
        socket_thread = QThread()

        manager = Manager(worker)

        parser = utils.PlcVariableParser()
        root_logger.debug('\n<<<<<<<<<<<<  Parsing QWidget\'s \'What\'s this\' fields, connecting signals and slots >>>>>>>>>>>>>')
        for i in find_supported_widgets(main_widget):
            try:
                if i.whatsThis() == '':
                    continue
                data = parser.parse(i.whatsThis())
                root_logger.info('-----------------------\n'
                                 'In \'{}\' found: \'{}\' parsed to: \'{}\''.format(i.objectName(), i.whatsThis(), data))
                manager.add_subscriber(data, i)
            except ValueError as e:
                root_logger.warning('-----------------------\n'
                                    'In \'{}\' found: \'{}\' parsing failure'.format(i.objectName(), i.whatsThis()))
                pass
        root_logger.debug('<<<<<<<<<<<<  End of parsing >>>>>>>>>>>>>\n')
        manager.optimize_readout_list()

        # TODO: After closing mainwindow exception is sean in console:
        # Qt has caught an exception thrown from an event handler. Throwing
        # exceptions from an event handler is not supported in Qt.
        # You must not let any exception whatsoever propagate through Qt code.
        # If that is not possible, in Qt 5 you must at least reimplement
        # QCoreApplication::notify() and catch all exceptions there.
        # (python3:5091): GLib-CRITICAL **: g_source_unref_internal: assertion 'source != NULL' failed
        worker.moveToThread(socket_thread)
        manager.communication_status.connect(main_widget.change_connection_visu_state)
        manager.plc_state_signal.connect(main_widget.display_plc_status)
        socket_thread.start()
        timer = QTimer()
        timer.timeout.connect(manager.do_work)
        timer.start(refresh_time)

    main_widget.show()
    app.exec()