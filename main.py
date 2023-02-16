from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QFileDialog
from PyQt5.QtCore import QUrl
import sys
import AudioUI
import logging

import wave, struct
from threading import Thread, Event
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
        self.audio_file = None
        
        self.socket = None

        self.is_file_open = False
        self.play_wav_file = False

        self.thread_client_configurations()

        self.widjet_adjust()
        self.widjet_functional()
    
    def widjet_functional(self):
        # Button's handlers
        self.btn_load_wav_file.clicked.connect(self.load_wav_file_handler)
        self.btn_connect_to_server.clicked.connect(self.connect_server_handler)

        self.btn_play_wav_file.clicked.connect(self.play_wav_file_handler)

    def widjet_adjust(self):

        self.btn_play_wav_file.setText("Play")

        self.edit_ip_address.setText("192.168.100.10:7")

    def closeEvent(self, event):
        self.logger.info("Close main window")
        self.close_connection()
        self.play_wav_file = False
        self.close_file()
        

    def load_wav_file_handler(self):
        self.logger.info("Load wav file handler")

        # close prev file
        self.close_file()

        try:
            file_name_url, _ = QFileDialog.getOpenFileName(self)
            self.logger.debug(f"Get file name: {file_name_url}")

            file_name = QUrl.fromLocalFile(file_name_url).fileName()

            self.text_brows_info.clear()
            self.text_brows_info.append(f"File name: {file_name}")

            self.is_file_open = True

            self.parse_wav_file(file_name_url)
        except FileNotFoundError as ex:
            self.logger.error(f"File open error. {ex}")
            self.text_brows_info.clear()
            self.text_brows_info.append(f"File not found!")
            self.is_file_open = False

    
    def parse_wav_file(self, file_name_url):

        self.logger.info("Parse wav file")

        try:
            self.audio_file = wave.open(file_name_url, 'r')
            number_frames = self.audio_file.getnframes()
            frame_rate = self.audio_file.getframerate()
            # stat = self.audio_file.getparams()
            self.logger.debug(f"number_frames: {number_frames}")
            self.logger.debug(f"frame_rate: {frame_rate}")

            # self.text_brows_info.append(f"frame rate: {frame_rate} Hz")
        except wave.Error as ex:
            self.logger.error(f"Parse WAV file error: {ex}")
            self.text_brows_info.clear()
            self.text_brows_info.append(f"File must have the format '.wav'.")
            self.is_file_open = False



    def close_file(self):
        self.logger.info("Close file")

        if self.audio_file is None:
            pass
        else:
            self.audio_file.close()

    def close_connection(self):
        self.logger.info("Close connection")

        self.thr_client_tx_should_work = False
        self.thr_client_rx_should_work = False


        if self.socket is None:
            pass
        else:
            self.socket.close()




    def thread_client_configurations(self):

        self.thr_client_rx = Thread(target=self.rx_task, args=(), daemon=True)
        self.thr_client_tx = Thread(target=self.tx_task, args=(), daemon=True)

        self.thr_client_rx_should_work = False
        self.thr_client_tx_should_work = False

        self.thr_client_rx.start()
        self.thr_client_tx.start()



    def connect_server_handler(self):
        self.logger.info("Connecting to the server")

        try:

            tcp_ip, tcp_port = self.get_ip_address()

            self.text_brows_info.clear()
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(1.5)
            self.socket.connect((tcp_ip, tcp_port))
            self.thr_client_tx_should_work = True
            self.thr_client_rx_should_work = True
            self.text_brows_info.append(f"Connection to {tcp_ip}:{tcp_port} successfully")
            self.logger.debug(f"Connection to {tcp_ip}:{tcp_port} successfully")
        except socket.timeout as ex:
            self.logger.error(f"Socket.timeout. Connection failed: {ex}")
            self.close_connection()
            self.text_brows_info.clear()
            self.text_brows_info.append(f"Connection failed. Address {tcp_ip}:{tcp_port}")
        except IndexError as ex:
            self.logger.error(f"IndexError. {ex}")
            self.text_brows_info.clear()
            self.text_brows_info.append(f"Bad address format!")


    def play_wav_file_handler(self):
        self.logger.info("Play WAV file handler")

        self.play_wav_file = not self.play_wav_file

        if self.play_wav_file:
            self.logger.debug("Play file")
            self.btn_play_wav_file.setText("Stop")
            self.text_brows_info.append("Playing")
        else:
            self.btn_play_wav_file.setText("Play")
            self.logger.debug("Stop file")
            self.text_brows_info.append("Stop")

        
    def get_ip_address(self):

        text_server_address = self.edit_ip_address.text()
        list_address = text_server_address.split(":")
        return list_address[0], int(list_address[1])
 
    def tx_task(self):

        while True:
            if self.thr_client_tx_should_work is True and self.play_wav_file is True and self.is_file_open is True:
                
                wave_bytes = self.audio_file.readframes(128)

                message = ""
                for i in range(0, len(wave_bytes)):
                    message += hex(wave_bytes[i])[2:]

                self.socket.send(message.encode("utf-8"))

                # time.sleep(0.014)
                Event().wait(0.0225)
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