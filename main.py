from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QFileDialog
from PyQt5.QtCore import QUrl

import sys
import os
import AudioUI

from log import get_logger


from threading import Thread, Event
import socket
import pyaudio

import numpy as np

from functional.microphone import Microphone
from functional.file_audio import FileAudio
from functional.converter import Converter
from communication.client_tcp import ClientTCP

import time




TCP_IP = '192.168.0.107'
TCP_PORT = 7


logger = get_logger(__name__.replace('__', ''))
# logger.info("Spawned main")



def find_data_file(filename):
    if getattr(sys, "frozen", False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        datadir = os.path.dirname(__file__)
    return os.path.join(datadir, filename)


if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class AudioUIApp(QtWidgets.QMainWindow, AudioUI.Ui_MainWindow):

    DEFAULT_TIMEOUT_MSG = 0.030
    DEFAULT_TIMEOUT_MSG_DELTA = 0.006
    DEFAULT_MIC_TIMEOUT_MSG = 0.003

    MSG_LEN_BYTES = 512 # 1024 for 16sign

    CURRENT_MODE_FILE = 1
    CURRENT_MODE_MIC = 2 
    PLAY_WAV_FILE_PLAYING = 3 
    PLAY_WAV_FILE_STOP = 4
    PLAY_MIC_PLAYING = 5
    PLAY_MIC_STOP = 6


    def __init__(self, parent=None):
        super(AudioUIApp, self).__init__(parent)
        self.setupUi(self)

        self.setWindowTitle('Audio')
        self.setWindowIcon(QtGui.QIcon(find_data_file("icons\\mic.png")))

        self._converter = Converter(True, 16000)
        self._file_audio = FileAudio()
        self._microphone = Microphone(1, pyaudio.paInt16)
        self._connection = ClientTCP(address_family=socket.AF_INET, socket_kind=socket.SOCK_STREAM, 
                                    timeout=0.5)

        self.current_mode = AudioUIApp.CURRENT_MODE_FILE
        self.play_wav_file = AudioUIApp.PLAY_WAV_FILE_STOP
        self.play_audio_mic = AudioUIApp.PLAY_MIC_STOP
        self.period = AudioUIApp.DEFAULT_TIMEOUT_MSG 
        
        self.thread_client_configurations()
        self.widget_adjust()
        self.widget_functional()
    
    def widget_functional(self):

        self.btn_load_wav_file.clicked.connect(self.load_wav_file_handler)
        self.btn_connect_to_server.clicked.connect(self.connect_server_handler)
        self.btn_mode_choice.clicked.connect(self.change_mode_handler)
        
        self.btn_play_wav_file.clicked.connect(self.play_wav_file_handler)
        self.btn_play_mic.clicked.connect(self.play_audio_mic_handler)

        self.btn_reboot_server.clicked.connect(self.reboot_server_handler)

        self.slider_volume.valueChanged.connect(self.slider_volume_event_handler)


    def widget_adjust(self):

        self.btn_play_wav_file.setText("Play file")
        self.btn_play_mic.setText("Record")
        self.edit_ip_address.setText(f"{TCP_IP}:{str(TCP_PORT)}")

        self.btn_play_wav_file.setEnabled(True)
        self.btn_load_wav_file.setEnabled(True)
        self.btn_play_mic.setEnabled(False)


        self.slider_volume.setMinimum(0)
        self.slider_volume.setMaximum(100)

        self.volume = self.slider_volume.value()
        self.label_volume.setText(f"{self.volume}%")
        self.volume /= 100


    def slider_volume_event_handler(self):
        self.volume = self.slider_volume.value()
        self.label_volume.setText(f"{self.volume}%")
        self.volume /= 100


    def reboot_server_handler(self):
        logger.info("Reboot server handler")

        self.thr_client_rx_should_work = False
        self.thr_client_tx_should_work = False
        self.thr_file_preparing_should_work = False

        self.set_text_browser(f"Reboot server")
        self.close_file()
        self.disable_mic()

        try:
            self._connection.send("reboot".encode("utf-8"))
        except OSError as ex:
            logger.error(f"Send reboot error: {ex}")
            self.set_text_browser(f"Send reboot error")
        except AttributeError as ex:
            logger.error(f"Send reboot error: {ex}")
            self.set_text_browser(f"Send reboot error")
        

    def closeEvent(self, event):
        logger.info("Close main window")
        self.close_connection()
        self.play_wav_file = AudioUIApp.PLAY_WAV_FILE_STOP
        self.play_audio_mic = AudioUIApp.PLAY_MIC_STOP
        self.close_file()
        self._microphone.close()

        
    def load_wav_file_handler(self):
        logger.info("Load wav file handler")

        self.close_file()
        self.file_name_url, _ = QFileDialog.getOpenFileName(self)
        logger.debug(f"Get file name: {self.file_name_url}")
        self.file_name = QUrl.fromLocalFile(self.file_name_url).fileName()

        try:
            self._file_audio.open(self.file_name_url)
            self.set_text_browser(f"File name: {self.file_name}")
            logger.debug(f"File is ready!")
            self.set_text_browser(f"File is ready!")
        except FileNotFoundError as ex:
            logger.error(f"File open error. {ex}")
            self.text_brows_info.append(f"File not found!")
        except ValueError as ex:
            logger.error(f"Parse WAV file error. {ex}")
            self.text_brows_info.append(f"File must have the format '.wav'.")
        

        # self.set_text_browser(f"{self._file_audio.get_source_sample_rate()}")

    @staticmethod
    def set_volume(x, volume):
        return x * volume


    def close_file(self):
        logger.info("Close file")
        self._file_audio.close()
        self.play_wav_file = AudioUIApp.PLAY_WAV_FILE_STOP
        self.btn_play_wav_file.setText("Play file")


    def close_connection(self):

        self.thr_client_tx_should_work = False
        self.thr_client_rx_should_work = False
        self._connection.disconnect()

    def disable_mic(self):
        logger.info("Disable mic")

        self.play_audio_mic = AudioUIApp.PLAY_MIC_STOP
        Event().wait(0.1)
        self.btn_play_mic.setText("Record")

        self._microphone.disable()



    def change_mode_handler(self):
        logger.info("Change mode handler")

        if self.current_mode == AudioUIApp.CURRENT_MODE_FILE:
            self.current_mode = AudioUIApp.CURRENT_MODE_MIC
            self.btn_mode_choice.setText("MIC")
            self.set_text_browser(f"MIC audio mode")

            self.btn_play_wav_file.setEnabled(False)
            self.btn_load_wav_file.setEnabled(False)

            self.btn_play_mic.setEnabled(True)

            self.close_file()
        elif self.current_mode == AudioUIApp.CURRENT_MODE_MIC:
            self.current_mode = AudioUIApp.CURRENT_MODE_FILE

            self.btn_play_mic.setEnabled(False)

            self.btn_play_wav_file.setEnabled(True)
            self.btn_load_wav_file.setEnabled(True)

            self.btn_mode_choice.setText("File")
            self.set_text_browser(f"File mode")
            self.disable_mic()

        Event().wait(0.1)

    def set_text_browser(self, text):
        self.text_brows_info.append(text)
        self.text_brows_info.moveCursor(QtGui.QTextCursor.End)
        

    def thread_client_configurations(self):

        self.thr_client_rx = Thread(target=self.rx_task, args=(), daemon=True)
        self.thr_client_tx = Thread(target=self.tx_task, args=(), daemon=True)
        # self.thr_file_preparing = Thread(target=self.file_preparing, args=(), daemon=True)

        self.thr_client_rx_should_work = False
        self.thr_client_tx_should_work = False
        # self.thr_file_preparing_should_work = False

        self.thr_client_rx.start()
        self.thr_client_tx.start()
        # self.thr_file_preparing.start()


    def connect_server_handler(self):
        logger.info("Connecting to the server handler")

        self.close_connection()

        try:
            tcp_ip, tcp_port = self.get_ip_address()
            self._connection.connect(tcp_ip, tcp_port)
            self.thr_client_tx_should_work = True
            self.thr_client_rx_should_work = True
            self.set_text_browser(f"Connection to {tcp_ip}:{tcp_port} successfully")
            logger.debug(f"Connection to {tcp_ip}:{tcp_port} successfully")
        except socket.timeout as ex:
            logger.error(f"Socket.timeout. Connection failed: {ex}")
            self.close_connection()
            self.set_text_browser(f"Connection failed. Address {tcp_ip}:{tcp_port}")
        except IndexError as ex:
            logger.error(f"IndexError. {ex}")
            self.close_connection()
            self.set_text_browser(f"Bad address format!")
        except ConnectionRefusedError as ex:
            logger.error(f"ConnectionRefusedError. {ex}")
            self.close_connection()
            self.set_text_browser(f"Bad address! Сheck that the address is correct!")

    def play_wav_file_handler(self):
        logger.info("Play WAV file handler")

        if self.play_wav_file == AudioUIApp.PLAY_WAV_FILE_STOP:
            self.play_wav_file = AudioUIApp.PLAY_WAV_FILE_PLAYING
            logger.debug("Play file")
            self.btn_play_wav_file.setText("Stop file")
            self.set_text_browser(f"Uploading file")

        elif self.play_wav_file == AudioUIApp.PLAY_WAV_FILE_PLAYING:
            self.play_wav_file = AudioUIApp.PLAY_WAV_FILE_STOP
            self.btn_play_wav_file.setText("Play file")
            logger.debug("Stop file")
            self.set_text_browser(f"Stop uploading file")


    def play_audio_mic_handler(self):
        logger.info("Play audio MIC handler")

        if self.play_audio_mic == AudioUIApp.PLAY_MIC_STOP:

            self._microphone.enable()
            self.play_audio_mic = AudioUIApp.PLAY_MIC_PLAYING
            logger.debug("Recording")
            self.btn_play_mic.setText("Stop")
            self.set_text_browser(f"Microphone recording")

        elif self.play_audio_mic == AudioUIApp.PLAY_MIC_PLAYING:

            self.disable_mic()

            logger.debug("Stop recording")
            self.set_text_browser(f"Microphone stop recording")


        
    def get_ip_address(self):
        text_server_address = self.edit_ip_address.text()
        list_address = text_server_address.split(":")
        return list_address[0], int(list_address[1])


    def get_time_period_message(self):
        return self.period

    def set_time_period_message(self, value):
        self.period = value

    def set_timeout_period(self, val):
        def_val = AudioUIApp.DEFAULT_TIMEOUT_MSG

        if self.current_mode == AudioUIApp.CURRENT_MODE_FILE:
            def_val = AudioUIApp.DEFAULT_TIMEOUT_MSG
        elif self.current_mode == AudioUIApp.CURRENT_MODE_MIC:
            def_val = AudioUIApp.DEFAULT_MIC_TIMEOUT_MSG
        else:
            def_val = AudioUIApp.DEFAULT_TIMEOUT_MSG

        if val >= 0 and val <= 30:
            def_val = def_val - 4 * AudioUIApp.DEFAULT_TIMEOUT_MSG_DELTA      
        elif val >= 30 and val < 40:
            def_val = def_val - 3 * AudioUIApp.DEFAULT_TIMEOUT_MSG_DELTA 
        elif val >= 40 and val < 50:
            def_val = def_val - 1 * AudioUIApp.DEFAULT_TIMEOUT_MSG_DELTA 
        elif val >= 50 and val < 70:
            def_val = def_val
        elif val >= 70 and val < 80:
            def_val = def_val + 1 * AudioUIApp.DEFAULT_TIMEOUT_MSG_DELTA 
        elif val >= 80 and val < 90:
            def_val = def_val + 3 * AudioUIApp.DEFAULT_TIMEOUT_MSG_DELTA 
        elif val >= 90:
            def_val = def_val + 4 * AudioUIApp.DEFAULT_TIMEOUT_MSG_DELTA   


        if def_val <= 0:
            def_val = 0.001
            logger.debug(f"new period < 0. Set 0.001 ms")

        self.set_time_period_message(def_val)

        logger.debug(f"{val}")
          

 
    def tx_task(self):

        idle_period = 0.03

        time_last_send_idle = time.time()
        period_send_idle = 0.5 #sec

        send_error_once = 1
        send_error_once_file = 1

        while True:

            message = "idle".encode("utf-8")

            if self.thr_client_tx_should_work is True and self.play_wav_file == AudioUIApp.PLAY_WAV_FILE_PLAYING and \
                self.current_mode == AudioUIApp.CURRENT_MODE_FILE:

                chunk = int(AudioUIApp.MSG_LEN_BYTES * 
                            (self._file_audio.get_source_sample_rate() / self._converter.get_target_sample_rate()))
                
                number_of_messages = 34 # 16000 / 34 = 1 sec of music
                
                if self._file_audio.is_prepared_data_end():
                    message = self._file_audio.read(chunk * number_of_messages)
                    message = self._converter.convert_file(message, self._file_audio.get_source_sample_rate())
                    self._file_audio.set_prepared_data(message, number_of_messages)

                if self._file_audio.is_file_end():
                    self._file_audio.restart_file()

                message = self._file_audio.get_chunk_prepared_data(AudioUIApp.MSG_LEN_BYTES)
                message = AudioUIApp.set_volume(message, self.volume)
                message = message.astype(np.int16)

                try:
                    self._connection.send(message)
                    send_error_once_file = 1
                except socket.timeout as ex:
                    if send_error_once_file != 0:
                        logger.error(f"Send audio error: {ex}")
                        self.set_text_browser(f"Send audio error!")
                        send_error_once_file -= 1
                except BrokenPipeError as ex:
                    if send_error_once_file != 0:
                        logger.error(f"Broken pip error: {ex}")
                        self.set_text_browser(f"Fatal connection lost! Reconnect to server or reboot")
                        send_error_once_file -= 1
                        self.close_connection()

                period = self.get_time_period_message()
                Event().wait(period)

            elif self.thr_client_tx_should_work is True and self.play_audio_mic == AudioUIApp.PLAY_MIC_PLAYING and \
                 self.current_mode == AudioUIApp.CURRENT_MODE_MIC and self._microphone.get_status_connect():
                
                chunk = int(AudioUIApp.MSG_LEN_BYTES * 
                            (self._microphone.get_source_sample_rate() / self._converter.get_target_sample_rate()))

                try:
                    message = self._microphone.read(chunk)

                    if message is None:
                        continue

                    message = np.frombuffer(message, dtype=np.int16)
                    message = self._converter.convert_mic(message, self._microphone.get_source_sample_rate())
                    message = AudioUIApp.set_volume(message, self.volume)
                    message = message.astype(np.int16)
                    self._connection.send(message)
                    send_error_once = 1

                except BrokenPipeError as ex:
                    if send_error_once != 0:
                        logger.error(f"Broken pip error: {ex}")
                        self.set_text_browser(f"Fatal connection lost! Try to reconnect or reboot server!")
                        send_error_once -= 1
                    self.close_connection()
                except socket.timeout as ex:
                    if send_error_once != 0:
                        logger.error(f"Send microphone data error. {ex}")
                        self.set_text_browser(f"Send microphone data error!")
                        send_error_once -= 1
                except AttributeError as ex:
                    logger.error(f"AttributeError MIC. {ex}")
                except OSError as ex:
                    logger.error(f"OSError MIC. {ex}")

                Event().wait(AudioUIApp.DEFAULT_MIC_TIMEOUT_MSG)

            else:
                try:
                    if time.time() - time_last_send_idle >= period_send_idle:
                        time_last_send_idle = time.time()
                        self._connection.send(message)
                        send_error_once = 1
                except BrokenPipeError as ex:
                    if send_error_once != 0:
                        logger.error(f"Broken pip error: {ex}")
                        self.set_text_browser(f"Fatal connection lost! Try to reconnect or reboot server!")
                    self.close_connection()
                except AttributeError as ex:
                    logger.debug(f"AttributeError. {ex}")
                except socket.timeout as ex:
                    if send_error_once != 0:
                        logger.error(f"Send idle error. {ex}")
                        self.set_text_browser(f"Fatal connection lost! Try to reconnect or reboot server!")
                except ConnectionResetError as ex:
                    if send_error_once != 0:
                        logger.error(f"Send message error. {ex}")
                        self.set_text_browser(f"Fatal connection lost! Try to reconnect or reboot server!")
                finally:
                    send_error_once -= 1

                Event().wait(idle_period)

            


    def rx_task(self):

        send_error_once = 0

        while True:
            if self.thr_client_rx_should_work is True and self._connection.get_connection_status() is True:

                try:
                    recv_data = self._connection.read(32)
                    if recv_data is not None:
                        val = self._connection.parse_answer_tcp_percent(recv_data)
                        self.set_timeout_period(val)
                        send_error_once = 0
                except socket.timeout as ex:
                    if send_error_once == 0:
                        logger.error(f"Read socket timeout")
                except OSError as ex:
                    logger.error(f"Read OSError. Bad file descriptor: {ex}")
                    if send_error_once == 0:
                        self.set_text_browser(f"Fatal connection lost! Try to reconnect or reboot server!")
                finally:
                    send_error_once = 1


                Event().wait(0.001)
            else:                
                Event().wait(0.001)
    
    def file_preparing(self):
      
        while True:
            if self.thr_file_preparing_should_work is True:

                try:

                    self.set_text_browser(f"File name: {self.file_name}")
                    self.set_text_browser(f"Preparing file...")

                    self._file_audio.open(self.file_name_url)
                    data, sample_rate = self._file_audio.read_all()
                    self._file_audio.close()
                    
                    prepared_data = self._converter.prepare_wav_file(data, sample_rate)
                    self._file_audio.set_prepared_all_data(prepared_data)
                    
                    self.set_text_browser(f"File is ready!")

                except FileNotFoundError as ex:
                    logger.error(f"File open error. {ex}")
                    self.text_brows_info.append(f"File not found!")
                except ValueError as ex:
                    logger.error(f"Parse WAV file error. {ex}")
                    self.text_brows_info.append(f"File must have the format '.wav'.")

                self.thr_file_preparing_should_work = False


            Event().wait(0.1)


def main():

    app = QApplication(sys.argv)
    form = AudioUIApp()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()