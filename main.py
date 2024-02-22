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
from functional.opus_codec import OpusCodec
from functional.pid_controller import PIDController
from communication.client_tcp import ClientTCP
from communication.client_udp import ClientUDP


import time

TCP_IP = '192.168.0.107'
TCP_PORT = 7


logger = get_logger(__name__.replace('__', ''))


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

    DEFAULT_TIMEOUT_MSG = 0.027
    DEFAULT_TIMEOUT_MSG_DELTA = 0.005
    DEFAULT_MIC_TIMEOUT_MSG = 0.003

    # MSG_LEN_BYTES = 512 # 1024 for 16sign
    MSG_LEN_BYTES = 512 # 1024 for 16sign
    # MSG_LEN_BYTES = 480
    # MSG_LEN_BYTES = 1920
    # MSG_LEN_BYTES = 2880 # with codec

    PREPARED_MSG_SECONDS = 15 # sec

    CURRENT_MODE_FILE = 1
    CURRENT_MODE_MIC = 2 
    PLAY_WAV_FILE_PLAYING = 3 
    PLAY_WAV_FILE_STOP = 4
    PLAY_MIC_PLAYING = 5
    PLAY_MIC_STOP = 6


    def __init__(self, parent=None):
        super(AudioUIApp, self).__init__(parent)
        self.setupUi(self)

        self.setWindowTitle('Audio v2.1.0')
        self.setWindowIcon(QtGui.QIcon(find_data_file("icons\\mic.png")))

        self._converter = Converter(True, 16000)
        self._file_audio = FileAudio()
        self._microphone = Microphone(1, pyaudio.paInt16)
        self._connection = ClientTCP(address_family=socket.AF_INET, socket_kind=socket.SOCK_STREAM, 
                                    timeout=1.5)
        # self._connection = ClientUDP(address_family=socket.AF_INET, socket_kind=socket.SOCK_DGRAM, 
                                    # timeout=1.5)
        # self._codec = OpusCodec(self._converter.get_target_sample_rate(), 1, "voip")

        self._num_prepared_msg_audio = int((self._converter.get_target_sample_rate() / AudioUIApp.MSG_LEN_BYTES) * AudioUIApp.PREPARED_MSG_SECONDS) + 1

        self.current_mode = AudioUIApp.CURRENT_MODE_FILE
        self.play_wav_file = AudioUIApp.PLAY_WAV_FILE_STOP
        self.play_audio_mic = AudioUIApp.PLAY_MIC_STOP
        self.period = AudioUIApp.DEFAULT_TIMEOUT_MSG 

        self._kp = -0.1
        self._ki = -0.05
        self._kd = 0.0
        self._alpha = 1
        self._pid_min_out = AudioUIApp.DEFAULT_TIMEOUT_MSG
        self._pid_max_out = AudioUIApp.DEFAULT_TIMEOUT_MSG * 5 # sec
        self._max_windup = 1

        self._pid = PIDController(kp=self._kp, ki=self._ki, kd=self._kd, max_windup=self._max_windup, 
                                alpha=self._alpha, u_bounds=[self._pid_min_out, self._pid_max_out])
        
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

        self.label.setText("Mode: FILE")

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
            self.close_connection()
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
            self._file_audio.set_correct_wav_file(True)
            self.set_text_browser(f"File name: {self.file_name}")
            logger.debug(f"File is ready!")
            self.set_text_browser(f"File is ready!")
        except FileNotFoundError as ex:
            logger.error(f"File open error. {ex}")
            self.text_brows_info.append(f"File not found!")
            self.close_file()
        except ValueError as ex:
            logger.error(f"Parse WAV file error. {ex}")
            self.text_brows_info.append(f"File must have the format '.wav'.")
            self.close_file()
            
        


    @staticmethod
    def set_volume(x, volume):
        return x * volume


    def close_file(self):
        logger.info("Close file")
        self._file_audio.close()
        self.play_wav_file = AudioUIApp.PLAY_WAV_FILE_STOP
        self.btn_play_wav_file.setText("Play file")
        self._file_audio.set_correct_wav_file(False)


    def close_connection(self):

        try:
            message = "idle".encode("utf-8") # for stop playing audio
            self._connection.send(message)
        except:
            logger.debug("Send close idle error")

        self.thr_client_tx_should_work = False
        self.thr_client_rx_should_work = False

        Event().wait(0.05)

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
            # self.btn_mode_choice.setText("MIC")
            self.label.setText("Mode: MIC")
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

            # self.btn_mode_choice.setText("File")
            # self.label.setText("FILE")
            self.label.setText("Mode: FILE")
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

        # ip = "192.168.0.107"
        # port = 7
        # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        # send_data = "Type some text to send =>";
        # s.sendto(send_data.encode('utf-8'), (ip, port))
        # print("\n\n 1. Client Sent : ", send_data, "\n\n")
        # data, address = s.recvfrom(4096)
        # print("\n\n 2. Client received : ", data.decode('utf-8'), "\n\n")
        # s.close()


        self.close_connection()

        try:
            tcp_ip, tcp_port = self.get_ip_address()
            self._connection.connect(tcp_ip, tcp_port)
            # self._connection.connect("google.com", 80)
            # self._connection.send("test".encode())
            # ret = self._connection.read(32)
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
        self._pid.reset_part()
        self._pid.setStartTime(time.time())
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
        self._pid.reset_part()
        self._pid.setStartTime(time.time())
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
        # def_val = AudioUIApp.DEFAULT_TIMEOUT_MSG

        # if self.current_mode == AudioUIApp.CURRENT_MODE_FILE:
        #     def_val = AudioUIApp.DEFAULT_TIMEOUT_MSG
        # elif self.current_mode == AudioUIApp.CURRENT_MODE_MIC:
        #     def_val = AudioUIApp.DEFAULT_MIC_TIMEOUT_MSG
        # else:
        #     def_val = AudioUIApp.DEFAULT_TIMEOUT_MSG

        # if val >= 0 and val <= 30:
        #     def_val = def_val - 0 * AudioUIApp.DEFAULT_TIMEOUT_MSG_DELTA      
        # elif val >= 30 and val < 40:
        #     def_val = def_val - 0 * AudioUIApp.DEFAULT_TIMEOUT_MSG_DELTA 
        # elif val >= 40 and val < 50:
        #     def_val = def_val - 0 * AudioUIApp.DEFAULT_TIMEOUT_MSG_DELTA 
        # elif val >= 50 and val < 70:
        #     def_val = def_val - 0 * AudioUIApp.DEFAULT_TIMEOUT_MSG_DELTA 
        # elif val >= 70 and val < 80:
        #     def_val = def_val 
        # elif val >= 80 and val < 90:
        #     def_val = def_val + 2 * AudioUIApp.DEFAULT_TIMEOUT_MSG_DELTA 
        # elif val >= 90:
        #     def_val = def_val + 4 * AudioUIApp.DEFAULT_TIMEOUT_MSG_DELTA   


        # if def_val <= 0:
        #     def_val = 0.001
        #     logger.debug(f"new period < 0. Set 0.001 ms")
        self._pid.setTarget(80);
        def_val = self._pid.update(val, time.time())
        self.set_time_period_message(def_val)
        # logger.debug(f"{def_val}, {val}")
        # logger.debug(f"{val}")
          
    def send_error_periodicaly(self, err_text, period_s, last_send):
        ret = last_send
        if time.time() - last_send >= period_s:
            ret = time.time()
            self.set_text_browser(f"{err_text}")
        return ret
    
    def clear_timestamp_error_rx(self):
        self.timestamp_timeout_oserror = 0
        self.timestamp_timeout_read_rx = 0

    def clear_timestamp_error_tx(self):
        self.timestamp_timeout_send_tx_audio = 0
        self.timestamp_timeout_send_tx_mic = 0
        self.timestamp_broken_pipe_error = 0
        self.timestamp_error_idle = 0
        self.timestamp_connection_reset_error = 0

    def ready_to_send(self, time, last_timestamp, period):
        if(time - last_timestamp >= period):
            return True
        return False
        
 
    def tx_task(self):

        idle_period = 0.03

        time_last_send_idle = 0
        period_send_idle = 0.5 #sec

        self.timestamp_timeout_send_tx_audio = 0
        self.timestamp_timeout_send_tx_mic = 0
        self.timestamp_broken_pipe_error = 0
        self.timestamp_error_idle = 0
        self.timestamp_connection_reset_error = 0

        self.last_timestamp = 0;
        self.set_time_period_message(AudioUIApp.DEFAULT_MIC_TIMEOUT_MSG)

        self.period_send_volume = 0.25 # sec
        last_timestamp_volume = time.time()

        while True:

            message = "idle".encode("utf-8")

            if self.thr_client_tx_should_work is True and self.play_wav_file == AudioUIApp.PLAY_WAV_FILE_PLAYING and \
                self.current_mode == AudioUIApp.CURRENT_MODE_FILE and self._file_audio.is_correct_wav_file():
                # self.ready_to_send(time.time(), self.last_timestamp, self.get_time_period_message()):

                self.last_timestamp = time.time()

                chunk = int(AudioUIApp.MSG_LEN_BYTES * 
                            (self._file_audio.get_source_sample_rate() / self._converter.get_target_sample_rate()))
                
                if self._file_audio.is_file_end():
                    self._file_audio.restart_file()
                
                if self._file_audio.is_prepared_data_end():
                    message = self._file_audio.read(chunk * self._num_prepared_msg_audio)

                    message = self._converter.convert_file(message, self._file_audio.get_source_sample_rate())
                    self._file_audio.set_prepared_data(message, self._num_prepared_msg_audio)


                message = self._file_audio.get_chunk_prepared_data(AudioUIApp.MSG_LEN_BYTES)
                message = AudioUIApp.set_volume(message, self.volume)
                message = message.astype(np.int16)
                message = message.tobytes()
                # print(len(message))

                # if len(message) != (2 * AudioUIApp.MSG_LEN_BYTES):
                    # message += (b"\x00" * (2 * AudioUIApp.MSG_LEN_BYTES - len(message)))
       
                
                chunk_convert = round(chunk * (self._converter.get_target_sample_rate() / self._file_audio.get_source_sample_rate()))
                # message = self._codec.encode(message, chunk_convert)

                try:
                    self._connection.send(message)
                    self.clear_timestamp_error_tx()
                except socket.timeout as ex:
                    logger.error(f"Send audio error: {ex}")
                    self.timestamp_timeout_send_tx_audio = self.send_error_periodicaly(f"[ERROR]Send audio timeout!", 2, self.timestamp_timeout_send_tx_audio)
                except BrokenPipeError as ex:
                    logger.error(f"Broken pip error: {ex}")
                    self.timestamp_broken_pipe_error = self.send_error_periodicaly(f"[ERROR]Fatal connection lost! Reconnect to server or reboot", 5, self.timestamp_broken_pipe_error)
                    self.close_connection()


                self.period = self.get_time_period_message()
                # self.set_time_period_message(self.period_tx)
                Event().wait(self.period)

            elif self.thr_client_tx_should_work is True and self.play_audio_mic == AudioUIApp.PLAY_MIC_PLAYING and \
                 self.current_mode == AudioUIApp.CURRENT_MODE_MIC and self._microphone.get_status_connect():
                # and self.ready_to_send(time.time(), self.last_timestamp, self.get_time_period_message()):
                
                self.last_timestamp = time.time()

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
                    message = message.tobytes()

                    # print(message.shape)

                    chunk_convert = round(chunk * (self._converter.get_target_sample_rate() / self._microphone.get_source_sample_rate()))
                    # message = self._codec.encode(message, chunk_convert)

                    # print(len(message))

                    self._connection.send(message)
                    self.clear_timestamp_error_tx()


                except BrokenPipeError as ex:
                    self.timestamp_error_idle = self.send_error_periodicaly(f"[ERROR]Fatal connection lost! Try to reconnect or reboot server!", 5, self.timestamp_error_idle)
                    self.close_connection()
                except socket.timeout as ex:
                    self.timestamp_timeout_send_tx_mic = self.send_error_periodicaly(f"[ERROR]Send microphone data timeout", 2, self.timestamp_timeout_send_tx_mic)
                except AttributeError as ex:
                    logger.error(f"AttributeError MIC. {ex}")
                    pass
                except OSError as ex:
                    logger.error(f"OSError MIC. {ex}")
                    pass
                   
                self.set_time_period_message(AudioUIApp.DEFAULT_MIC_TIMEOUT_MSG)

            else:
                try:
                    if time.time() - time_last_send_idle >= period_send_idle:
                    # if self.ready_to_send(time.time(), self.last_timestamp, period_send_idle):
                        # self.last_timestamp = time.time()
                        time_last_send_idle = time.time()
                        self._connection.send(message)
                        self.clear_timestamp_error_tx()
                except BrokenPipeError as ex:
                    self.timestamp_broken_pipe_error = self.send_error_periodicaly(f"[ERROR]Fatal connection lost! Reconnect to server or reboot", 5, self.timestamp_broken_pipe_error)
                    self.close_connection()
                except AttributeError as ex:
                    logger.debug(f"AttributeError. {ex}")
                except socket.timeout as ex:
                    self.timestamp_error_idle = self.send_error_periodicaly(f"[ERROR]Send heartbeat message to megaphone timeout", 5, self.timestamp_error_idle)
                except ConnectionResetError as ex:
                    self.timestamp_connection_reset_error = self.send_error_periodicaly(f"[ERROR]Fatal connection lost! Try to reconnect or reboot server!", 5, self.timestamp_connection_reset_error)
                except OSError as ex:
                    pass
                

                # self.period_tx = period_send_idle
                # self.set_time_period_message(self.period_tx)
                Event().wait(idle_period)
            # Event().wait(0.001)


    def rx_task(self):

        self.timestamp_timeout_read_rx = 0
        self.timestamp_timeout_oserror = 0

        while True:
            if self.thr_client_rx_should_work is True and self._connection.get_connection_status() is True:
                try:
                    recv_data = self._connection.read(32)
                    if recv_data is not None:
                        val = self._connection.parse_answer_percent(recv_data)
                        self.set_timeout_period(val)
                        self.clear_timestamp_error_rx()
                        self.label_telem.setText(f"{val} %")
                except socket.timeout as ex:
                        # logger.error(f"Read socket timeout")
                    self.timestamp_timeout_read_rx = self.send_error_periodicaly(f"[ERROR]Megaphone response timeout", 5, self.timestamp_timeout_read_rx)

                except OSError as ex:
                    # logger.error(f"Read OSError. Bad file descriptor: {ex}")
                    self.timestamp_timeout_oserror = self.send_error_periodicaly(f"[ERROR]Fatal connection lost! Try to reconnect or reboot server!", 5, self.timestamp_timeout_oserror)

                Event().wait(0.001)
            else:                
                Event().wait(0.001)
    


def main():

    app = QApplication(sys.argv)
    form = AudioUIApp()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()