# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_ibh_client.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(776, 883)
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.groupBox = QtWidgets.QGroupBox(Form)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.groupBox.setFont(font)
        self.groupBox.setFlat(False)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.le_ip_address = QtWidgets.QLineEdit(self.groupBox)
        self.le_ip_address.setReadOnly(False)
        self.le_ip_address.setObjectName("le_ip_address")
        self.verticalLayout.addWidget(self.le_ip_address)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_3.addWidget(self.label_3)
        self.le_ip_port = QtWidgets.QLineEdit(self.groupBox)
        self.le_ip_port.setReadOnly(False)
        self.le_ip_port.setObjectName("le_ip_port")
        self.verticalLayout_3.addWidget(self.le_ip_port)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.le_mpi_address = QtWidgets.QLineEdit(self.groupBox)
        self.le_mpi_address.setReadOnly(False)
        self.le_mpi_address.setObjectName("le_mpi_address")
        self.verticalLayout_2.addWidget(self.le_mpi_address)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.horizontalLayout.setStretch(0, 6)
        self.horizontalLayout.setStretch(1, 2)
        self.horizontalLayout.setStretch(2, 2)
        self.verticalLayout_7.addWidget(self.groupBox)
        self.groupBox_3 = QtWidgets.QGroupBox(Form)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.groupBox_3.setFont(font)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.groupBox_4 = QtWidgets.QGroupBox(self.groupBox_3)
        self.groupBox_4.setEnabled(True)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.groupBox_4.setFont(font)
        self.groupBox_4.setFlat(False)
        self.groupBox_4.setObjectName("groupBox_4")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox_4)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.cb_address_area = QtWidgets.QComboBox(self.groupBox_4)
        self.cb_address_area.setObjectName("cb_address_area")
        self.gridLayout_3.addWidget(self.cb_address_area, 0, 0, 1, 1)
        self.horizontalLayout_2.addWidget(self.groupBox_4)
        self.groupBox_5 = QtWidgets.QGroupBox(self.groupBox_3)
        self.groupBox_5.setEnabled(True)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.groupBox_5.setFont(font)
        self.groupBox_5.setFlat(False)
        self.groupBox_5.setObjectName("groupBox_5")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.groupBox_5)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.le_variable_address = QtWidgets.QLineEdit(self.groupBox_5)
        self.le_variable_address.setText("")
        self.le_variable_address.setFrame(True)
        self.le_variable_address.setEchoMode(QtWidgets.QLineEdit.Normal)
        self.le_variable_address.setCursorPosition(0)
        self.le_variable_address.setObjectName("le_variable_address")
        self.gridLayout_4.addWidget(self.le_variable_address, 0, 0, 1, 1)
        self.horizontalLayout_2.addWidget(self.groupBox_5)
        self.groupBox_6 = QtWidgets.QGroupBox(self.groupBox_3)
        self.groupBox_6.setEnabled(True)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.groupBox_6.setFont(font)
        self.groupBox_6.setFlat(False)
        self.groupBox_6.setObjectName("groupBox_6")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.groupBox_6)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.le_variable_offset = QtWidgets.QLineEdit(self.groupBox_6)
        self.le_variable_offset.setObjectName("le_variable_offset")
        self.gridLayout_5.addWidget(self.le_variable_offset, 0, 0, 1, 1)
        self.horizontalLayout_2.addWidget(self.groupBox_6)
        self.groupBox_9 = QtWidgets.QGroupBox(self.groupBox_3)
        self.groupBox_9.setEnabled(True)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.groupBox_9.setFont(font)
        self.groupBox_9.setFlat(False)
        self.groupBox_9.setObjectName("groupBox_9")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.groupBox_9)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.sb_variable_bytes_count = QtWidgets.QSpinBox(self.groupBox_9)
        self.sb_variable_bytes_count.setMinimum(1)
        self.sb_variable_bytes_count.setMaximum(8)
        self.sb_variable_bytes_count.setObjectName("sb_variable_bytes_count")
        self.gridLayout_8.addWidget(self.sb_variable_bytes_count, 0, 0, 1, 1)
        self.horizontalLayout_2.addWidget(self.groupBox_9)
        self.verticalLayout_6.addLayout(self.horizontalLayout_2)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.groupBox_8 = QtWidgets.QGroupBox(self.groupBox_3)
        self.groupBox_8.setEnabled(True)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.groupBox_8.setFont(font)
        self.groupBox_8.setFlat(False)
        self.groupBox_8.setObjectName("groupBox_8")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.groupBox_8)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.le_variable_value = QtWidgets.QLineEdit(self.groupBox_8)
        self.le_variable_value.setMaxLength(32)
        self.le_variable_value.setCursorPosition(0)
        self.le_variable_value.setObjectName("le_variable_value")
        self.verticalLayout_4.addWidget(self.le_variable_value)
        self.verticalLayout_5.addWidget(self.groupBox_8)
        self.groupBox_10 = QtWidgets.QGroupBox(self.groupBox_3)
        self.groupBox_10.setEnabled(True)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.groupBox_10.setFont(font)
        self.groupBox_10.setFlat(False)
        self.groupBox_10.setObjectName("groupBox_10")
        self.gridLayout_9 = QtWidgets.QGridLayout(self.groupBox_10)
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.btn_write = QtWidgets.QPushButton(self.groupBox_10)
        self.btn_write.setEnabled(True)
        self.btn_write.setCheckable(False)
        self.btn_write.setAutoRepeat(False)
        self.btn_write.setAutoExclusive(False)
        self.btn_write.setObjectName("btn_write")
        self.gridLayout_9.addWidget(self.btn_write, 0, 1, 1, 1)
        self.btn_read = QtWidgets.QPushButton(self.groupBox_10)
        self.btn_read.setEnabled(True)
        self.btn_read.setCheckable(False)
        self.btn_read.setAutoRepeat(False)
        self.btn_read.setAutoExclusive(False)
        self.btn_read.setObjectName("btn_read")
        self.gridLayout_9.addWidget(self.btn_read, 0, 0, 1, 1)
        self.btn_get_plc_status = QtWidgets.QPushButton(self.groupBox_10)
        self.btn_get_plc_status.setEnabled(True)
        self.btn_get_plc_status.setCheckable(False)
        self.btn_get_plc_status.setAutoRepeat(False)
        self.btn_get_plc_status.setAutoExclusive(False)
        self.btn_get_plc_status.setObjectName("btn_get_plc_status")
        self.gridLayout_9.addWidget(self.btn_get_plc_status, 0, 2, 1, 1)
        self.verticalLayout_5.addWidget(self.groupBox_10)
        self.verticalLayout_6.addLayout(self.verticalLayout_5)
        self.verticalLayout_7.addWidget(self.groupBox_3)
        self.groupBox_2 = QtWidgets.QGroupBox(Form)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.groupBox_2.setFont(font)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName("gridLayout")
        self.logging_window = QtWidgets.QTextEdit(self.groupBox_2)
        self.logging_window.setReadOnly(True)
        self.logging_window.setObjectName("logging_window")
        self.gridLayout.addWidget(self.logging_window, 0, 0, 1, 1)
        self.btn_clear = QtWidgets.QPushButton(self.groupBox_2)
        self.btn_clear.setObjectName("btn_clear")
        self.gridLayout.addWidget(self.btn_clear, 1, 0, 1, 1)
        self.verticalLayout_7.addWidget(self.groupBox_2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.groupBox.setTitle(_translate("Form", "Connection parameters"))
        self.label.setText(_translate("Form", "Ip address"))
        self.le_ip_address.setWhatsThis(_translate("Form", "MW9, WORD"))
        self.le_ip_address.setInputMask(_translate("Form", "000.000.000.000; "))
        self.label_3.setText(_translate("Form", "Ip port"))
        self.le_ip_port.setWhatsThis(_translate("Form", "MW9, WORD"))
        self.le_ip_port.setInputMask(_translate("Form", "00000; "))
        self.label_2.setText(_translate("Form", "MPI address"))
        self.le_mpi_address.setWhatsThis(_translate("Form", "MW9, WORD"))
        self.le_mpi_address.setInputMask(_translate("Form", "000; "))
        self.groupBox_3.setTitle(_translate("Form", "Reading/Writing"))
        self.groupBox_4.setTitle(_translate("Form", "Area"))
        self.groupBox_5.setTitle(_translate("Form", "Address"))
        self.le_variable_address.setInputMask(_translate("Form", "00000; "))
        self.groupBox_6.setTitle(_translate("Form", "Offset"))
        self.le_variable_offset.setInputMask(_translate("Form", "0000; "))
        self.groupBox_9.setTitle(_translate("Form", "Bytes count"))
        self.groupBox_8.setTitle(_translate("Form", "Value"))
        self.le_variable_value.setInputMask(_translate("Form", "00000000000000000000000000000000; "))
        self.groupBox_10.setTitle(_translate("Form", "Operation"))
        self.btn_write.setWhatsThis(_translate("Form", "m9.2"))
        self.btn_write.setText(_translate("Form", "WRITE"))
        self.btn_read.setWhatsThis(_translate("Form", "m9.2"))
        self.btn_read.setText(_translate("Form", "READ"))
        self.btn_get_plc_status.setWhatsThis(_translate("Form", "m9.2"))
        self.btn_get_plc_status.setText(_translate("Form", "Get PLC status"))
        self.groupBox_2.setTitle(_translate("Form", "Log window"))
        self.btn_clear.setText(_translate("Form", "Clear"))

