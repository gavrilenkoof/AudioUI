from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QFileDialog
from PyQt5.QtCore import QUrl
import sys
import AudioUI
import logging

import wave, struct
from threading import Thread
import socket
import time

TCP_IP = '192.168.100.10'
TCP_PORT = 7


# class ClientTCP:

#     def __init__(self, host_address=0):
#         self.host_address = 0
#         self.connect = False



class AudioUIApp(QtWidgets.QMainWindow, AudioUI.Ui_MainWindow):
    def __init__(self, parent=None):
        super(AudioUIApp, self).__init__(parent)
        self.setupUi(self)

        # self.connection = ClientTCP()

        self.logger = logging.getLogger('Main Window')
        self.open_file = None
        self.socket = None

        self.thread_client_configurations()

        self.widjet_adjust()
        self.widjet_functional()
    
    def widjet_functional(self):
        # Button's handlers
        self.btn_load_wav_file.clicked.connect(self.load_wav_file_handler)
        self.btn_connect_to_server.clicked.connect(self.connect_server_handler)

    def widjet_adjust(self):
        pass

    def closeEvent(self, event):
        self.logger.info("Close main window")
        self.close_file()
        self.close_connection()


    def load_wav_file_handler(self):
        self.logger.info("Load wav file handler")

        # close prev file
        self.close_file()

        try:
            file_name_url, _ = QFileDialog.getOpenFileName(self)
            self.logger.debug(f"Get file name: {file_name_url}")

            file_name = QUrl.fromLocalFile(file_name_url).fileName()

            self.text_brows_wav_file_info.clear()
            self.text_brows_wav_file_info.append(file_name)

            self.parse_wav_file(file_name_url)
        except FileNotFoundError as ex:
            self.logger.error(f"File open error. {ex}")
            self.text_brows_wav_file_info.clear()
            self.text_brows_wav_file_info.append(f"File not found!")

    
    def parse_wav_file(self, file_name_url):

        self.logger.info("Parse wav file")

        try:
            self.open_file = wave.open(file_name_url, 'r')
            number_frames = self.open_file.getnframes()
            frame_rate = self.open_file.getframerate()

            self.logger.debug(f"number_frames: {number_frames}")
            self.logger.debug(f"frame_rate: {frame_rate}")

            self.text_brows_wav_file_info.append(f"frame rate: {frame_rate} Hz")
        except wave.Error as ex:
            self.logger.error(f"Parse WAV file error: {ex}")
            self.text_brows_wav_file_info.clear()
            self.text_brows_wav_file_info.append(f"File must have the format '.wav'.")



    def close_file(self):
        self.logger.info("Close file")

        if self.open_file is None:
            pass
        else:
            self.open_file.close()

    def close_connection(self):
        self.logger.info("Close connection")

        if self.socket is None:
            pass
        else:
            self.socket.close()


    def thread_client_configurations(self):

        
        
        self.thr_client_rx = Thread(target=self.rx_task, args=(), daemon=True)
        self.thr_client_tx = Thread(target=self.tx_task, args=(), daemon=True)

        self.thr_client_rx_should_work = False
        self.thr_client_tx_should_work = False



    def connect_server_handler(self):
        self.logger.info("Connect to server")
        self.logger.debug(f"Address: {TCP_IP}:{TCP_PORT}")

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(1.5)
            self.socket.connect((TCP_IP, TCP_PORT))
        except socket.timeout as ex:
            self.logger.error(f"Socket.timeout. Connection failed: {ex}")
            self.socket.close()
            self.text_brows_wav_file_info.clear()
            self.text_brows_wav_file_info.append(f"Connection failed. Address {TCP_IP}:{TCP_PORT}")



 
    def tx_task(self):

        while True:
            if self.thr_client_tx_should_work is True:
                pass
            else:
                time.sleep(1)



    def rx_task(self):
        while True:
            if self.thr_client_rx_should_work is True:
                pass
            else:
                time.sleep(1)
    

def main():
    logging.basicConfig(level=logging.DEBUG, format='%(name)s:[%(levelname)s]: %(message)s')

    app = QApplication(sys.argv)
    form = AudioUIApp()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()