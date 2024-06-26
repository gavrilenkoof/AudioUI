# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AudioUI.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from functional.toggle import AnimatedToggle


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(510, 503)
        MainWindow.setMinimumSize(QtCore.QSize(510, 450))
        MainWindow.setMaximumSize(QtCore.QSize(1000, 1000))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout()
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.line_7 = QtWidgets.QFrame(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line_7.sizePolicy().hasHeightForWidth())
        self.line_7.setSizePolicy(sizePolicy)
        self.line_7.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_7.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_7.setObjectName("line_7")
        self.horizontalLayout_2.addWidget(self.line_7)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.line_8 = QtWidgets.QFrame(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line_8.sizePolicy().hasHeightForWidth())
        self.line_8.setSizePolicy(sizePolicy)
        self.line_8.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_8.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_8.setObjectName("line_8")
        self.horizontalLayout_2.addWidget(self.line_8)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btn_reboot_server = QtWidgets.QToolButton(self.centralwidget)
        self.btn_reboot_server.setMinimumSize(QtCore.QSize(65, 31))
        self.btn_reboot_server.setMaximumSize(QtCore.QSize(65, 31))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.btn_reboot_server.setFont(font)
        self.btn_reboot_server.setObjectName("btn_reboot_server")
        self.horizontalLayout.addWidget(self.btn_reboot_server)
        self.btn_connect_to_server = QtWidgets.QToolButton(self.centralwidget)
        self.btn_connect_to_server.setMinimumSize(QtCore.QSize(175, 31))
        self.btn_connect_to_server.setMaximumSize(QtCore.QSize(65, 31))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.btn_connect_to_server.setFont(font)
        self.btn_connect_to_server.setObjectName("btn_connect_to_server")
        self.horizontalLayout.addWidget(self.btn_connect_to_server)
        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.edit_ip_address = QtWidgets.QLineEdit(self.centralwidget)
        self.edit_ip_address.setMinimumSize(QtCore.QSize(150, 31))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.edit_ip_address.setFont(font)
        self.edit_ip_address.setObjectName("edit_ip_address")
        self.horizontalLayout.addWidget(self.edit_ip_address)


        self.label_telem = QtWidgets.QLabel(self.centralwidget)
        self.label_telem.setObjectName("label_telem")
        self.horizontalLayout.addWidget(self.label_telem)
        self.label_telem.setText("0 %")
        


        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.line_11 = QtWidgets.QFrame(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line_11.sizePolicy().hasHeightForWidth())
        self.line_11.setSizePolicy(sizePolicy)
        self.line_11.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_11.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_11.setObjectName("line_11")
        self.horizontalLayout_11.addWidget(self.line_11)
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_11.addWidget(self.label_6)
        self.line_12 = QtWidgets.QFrame(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line_12.sizePolicy().hasHeightForWidth())
        self.line_12.setSizePolicy(sizePolicy)
        self.line_12.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_12.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_12.setObjectName("line_12")
        self.horizontalLayout_11.addWidget(self.line_12)
        self.verticalLayout_2.addLayout(self.horizontalLayout_11)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")


        # self.btn_mode_choice = QtWidgets.QToolButton(self.centralwidget)
        # self.btn_mode_choice.setMinimumSize(QtCore.QSize(65, 31))
        # self.btn_mode_choice.setMaximumSize(QtCore.QSize(65, 31))
        # font = QtGui.QFont()
        # font.setPointSize(9)
        # self.btn_mode_choice.setFont(font)
        # self.btn_mode_choice.setObjectName("btn_mode_choice")
        # self.horizontalLayout_10.addWidget(self.btn_mode_choice)

        spacerItem5 = QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem5)

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label.setFont(font)
        
        self.horizontalLayout_10.addWidget(self.label)

        self.btn_mode_choice = AnimatedToggle(
            checked_color="#308CC6",
            pulse_checked_color="#44308CC6"
        )
        self.btn_mode_choice.setMinimumSize(QtCore.QSize(60, 37))
        self.btn_mode_choice.setMaximumSize(QtCore.QSize(60, 37))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.btn_mode_choice.setFont(font)
        self.btn_mode_choice.setObjectName("btn_mode_choice")
        self.horizontalLayout_10.addWidget(self.btn_mode_choice)

        spacerItem_mode = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem_mode)



        
        self.verticalLayout_2.addLayout(self.horizontalLayout_10)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.line = QtWidgets.QFrame(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line.sizePolicy().hasHeightForWidth())
        self.line.setSizePolicy(sizePolicy)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout_4.addWidget(self.line)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_4.addWidget(self.label_3)
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line_2.sizePolicy().hasHeightForWidth())
        self.line_2.setSizePolicy(sizePolicy)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.horizontalLayout_4.addWidget(self.line_2)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.btn_load_wav_file = QtWidgets.QToolButton(self.centralwidget)
        self.btn_load_wav_file.setMinimumSize(QtCore.QSize(65, 31))
        self.btn_load_wav_file.setMaximumSize(QtCore.QSize(65, 31))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.btn_load_wav_file.setFont(font)
        self.btn_load_wav_file.setObjectName("btn_load_wav_file")
        self.horizontalLayout_5.addWidget(self.btn_load_wav_file)
        self.btn_play_wav_file = QtWidgets.QToolButton(self.centralwidget)
        self.btn_play_wav_file.setMinimumSize(QtCore.QSize(65, 31))
        self.btn_play_wav_file.setMaximumSize(QtCore.QSize(65, 31))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.btn_play_wav_file.setFont(font)
        self.btn_play_wav_file.setObjectName("btn_play_wav_file")
        self.horizontalLayout_5.addWidget(self.btn_play_wav_file)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem2)
        self.verticalLayout_3.addLayout(self.horizontalLayout_5)
        self.verticalLayout_4.addLayout(self.verticalLayout_3)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.line_4 = QtWidgets.QFrame(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line_4.sizePolicy().hasHeightForWidth())
        self.line_4.setSizePolicy(sizePolicy)
        self.line_4.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.horizontalLayout_6.addWidget(self.line_4)
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_6.addWidget(self.label_4)
        self.line_3 = QtWidgets.QFrame(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line_3.sizePolicy().hasHeightForWidth())
        self.line_3.setSizePolicy(sizePolicy)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.horizontalLayout_6.addWidget(self.line_3)
        self.verticalLayout_4.addLayout(self.horizontalLayout_6)
        self.verticalLayout_5.addLayout(self.verticalLayout_4)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.btn_play_mic = QtWidgets.QToolButton(self.centralwidget)
        self.btn_play_mic.setMinimumSize(QtCore.QSize(65, 31))
        self.btn_play_mic.setMaximumSize(QtCore.QSize(65, 31))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.btn_play_mic.setFont(font)
        self.btn_play_mic.setObjectName("btn_play_mic")
        self.horizontalLayout_3.addWidget(self.btn_play_mic)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem3)
        self.verticalLayout_5.addLayout(self.horizontalLayout_3)
        self.verticalLayout_7.addLayout(self.verticalLayout_5)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout()
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.line_5 = QtWidgets.QFrame(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line_5.sizePolicy().hasHeightForWidth())
        self.line_5.setSizePolicy(sizePolicy)
        self.line_5.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_5.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_5.setObjectName("line_5")
        self.horizontalLayout_7.addWidget(self.line_5)
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_7.addWidget(self.label_5)
        self.line_6 = QtWidgets.QFrame(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line_6.sizePolicy().hasHeightForWidth())
        self.line_6.setSizePolicy(sizePolicy)
        self.line_6.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_6.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_6.setObjectName("line_6")
        self.horizontalLayout_7.addWidget(self.line_6)
        self.verticalLayout_8.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.slider_volume = QtWidgets.QSlider(self.centralwidget)
        self.slider_volume.setMaximum(100)
        self.slider_volume.setProperty("value", 1)
        self.slider_volume.setOrientation(QtCore.Qt.Horizontal)
        self.slider_volume.setObjectName("slider_volume")
        self.horizontalLayout_8.addWidget(self.slider_volume)
        self.label_volume = QtWidgets.QLabel(self.centralwidget)
        self.label_volume.setMinimumSize(QtCore.QSize(40, 0))
        self.label_volume.setObjectName("label_volume")
        self.horizontalLayout_8.addWidget(self.label_volume)
        self.verticalLayout_8.addLayout(self.horizontalLayout_8)
        self.verticalLayout_6.addLayout(self.verticalLayout_8)
        spacerItem4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_6.addItem(spacerItem4)
        self.text_brows_info = QtWidgets.QTextBrowser(self.centralwidget)
        self.text_brows_info.setMinimumSize(QtCore.QSize(150, 50))
        self.text_brows_info.setMaximumSize(QtCore.QSize(15000, 150))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.text_brows_info.setFont(font)
        self.text_brows_info.setObjectName("text_brows_info")
        self.verticalLayout_6.addWidget(self.text_brows_info)
        self.verticalLayout_7.addLayout(self.verticalLayout_6)
        self.verticalLayout_9.addLayout(self.verticalLayout_7)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 510, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Audio"))
        self.label_2.setText(_translate("MainWindow", "Server configuration"))
        self.btn_reboot_server.setText(_translate("MainWindow", "Reboot"))
        self.btn_connect_to_server.setText(_translate("MainWindow", "Connect to server"))
        self.label_6.setText(_translate("MainWindow", "Mode"))
        self.btn_mode_choice.setText(_translate("MainWindow", "File"))
        self.label.setText(_translate("MainWindow", "Mode"))
        self.label_3.setText(_translate("MainWindow", "File configuration"))
        self.btn_load_wav_file.setText(_translate("MainWindow", "Load"))
        self.btn_play_wav_file.setText(_translate("MainWindow", "Play file"))
        self.label_4.setText(_translate("MainWindow", "Microphone configuration"))
        self.btn_play_mic.setText(_translate("MainWindow", "Record"))
        self.label_5.setText(_translate("MainWindow", "Volume"))
        self.label_volume.setText(_translate("MainWindow", "Mode"))
