from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QFileDialog
from PyQt5.QtCore import QUrl
import sys
import AudioUI
import logging

import wave
from threading import Thread, Event
import socket
import time
import pyaudio


from scipy.io import wavfile
import scipy.signal as sps
import numpy as np

TCP_IP = '192.168.100.10'
TCP_PORT = 7



if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class AudioUIApp(QtWidgets.QMainWindow, AudioUI.Ui_MainWindow):

    DEFAULT_TIMEOUT_MSG = 0.030
    # DEFAULT_TIMEOUT_MSG = 0.015
    DEFAULT_TIMEOUT_MSG_DELTA = 0.006
    DEFAULT_MIC_TIMEOUT_MSG = 0.005

    MSG_LEN_BYTES = 512 # 1024 for 16sign


    CURRENT_MODE_FILE = 1 # FILE MODE
    CURRENT_MODE_MIC = 2 # MIC MODE
    PLAY_WAV_FILE_PLAYING = 3 
    PLAY_WAV_FILE_STOP = 4
    PLAY_MIC_PLAYING = 5
    PLAY_MIC_STOP = 6


    def __init__(self, parent=None):
        super(AudioUIApp, self).__init__(parent)
        self.setupUi(self)
        self.logger = logging.getLogger('Main Window')

        self.socket = None

        self.connection = False
        self.tcp_ip = TCP_IP
        self.tcp_port = TCP_PORT


        self.is_file_open = False
        self.is_connect_mic = False
        self.file_name_url = ''

        self.current_mode = AudioUIApp.CURRENT_MODE_FILE
        self.play_wav_file = AudioUIApp.PLAY_WAV_FILE_STOP
        self.play_audio_mic = AudioUIApp.PLAY_MIC_STOP

        self.period = AudioUIApp.DEFAULT_TIMEOUT_MSG

        self.form_1 = pyaudio.paInt16 
        self.chans = 1 
        self.source_sample_rate = 44100
        self.target_sample_rate = 16000

        self.chunk = int(AudioUIApp.MSG_LEN_BYTES * (self.source_sample_rate / self.target_sample_rate)) # for converting 44100 to 16000 format and payload = 512

        self.number_frame = 0


        self.audio = pyaudio.PyAudio()
        self.stream = None

        
        self.thread_client_configurations()

        self.widjet_adjust()
        self.widjet_functional()
    
    def widjet_functional(self):
        # Button's handlers
        self.btn_load_wav_file.clicked.connect(self.load_wav_file_handler)
        self.btn_connect_to_server.clicked.connect(self.connect_server_handler)
        self.btn_mode_choice.clicked.connect(self.change_mode_handler)
        # self.btn_connect_mic.clicked.connect(self.connect_mic_handler)
        
        self.btn_play_wav_file.clicked.connect(self.play_wav_file_handler)
        self.btn_play_mic.clicked.connect(self.play_audio_mic_handler)

        self.btn_reboot_server.clicked.connect(self.reboot_server_handler)

    def widjet_adjust(self):

        self.btn_play_wav_file.setText("Play file")
        self.btn_play_mic.setText("Record")
        self.edit_ip_address.setText("192.168.100.10:7")

        self.btn_play_wav_file.setEnabled(True)
        self.btn_load_wav_file.setEnabled(True)
        self.btn_play_mic.setEnabled(False)

        # self.btn_connect_mic.setText("Enable")

    def reboot_server_handler(self):
        self.logger.info("Reboot server handler")

        self.thr_client_rx_should_work = False
        self.thr_client_tx_should_work = False
        self.thr_file_preparing_should_work = False
        self.connection = False

        if self.socket is not None:
            self.socket.send("reboot".encode("utf-8"))
        

    def closeEvent(self, event):
        self.logger.info("Close main window")
        self.close_connection()
        self.play_wav_file = AudioUIApp.PLAY_WAV_FILE_STOP
        self.play_audio_mic = AudioUIApp.PLAY_MIC_STOP
        self.close_file()
        
    def load_wav_file_handler(self):
        self.logger.info("Load wav file handler")

        self.close_file()
        self.file_name_url, _ = QFileDialog.getOpenFileName(self)
        self.logger.debug(f"Get file name: {self.file_name_url}")
        self.file_name = QUrl.fromLocalFile(self.file_name_url).fileName()
        self.thr_file_preparing_should_work = True

    
    def parse_wav_file(self, file_name_url):

        self.logger.info("Parse wav file")


        self.data_audio_file = None
        self.number_frame = 0
        sample_rate, data = wavfile.read(file_name_url)
        
        if len(data.shape) >= 2:
            data = data.reshape((data.shape[0] * data.shape[1], 1))
            data = np.delete(data, np.arange(1, data.shape[0], 2))

        if data.dtype == np.uint8:
            self.logger.warning("Convert from uint8 to int16 format")
            self.text_brows_info.append(f"Convert to sample width 2")
            data = data.astype(np.int16)
            # print(data.max(), data.min())
            data = AudioUIApp.map_int(data)
            # print(data.max(), data.min())

            

        self.logger.debug(f"source sample rate: {sample_rate}")

        self.text_brows_info.append(f"Preparing file...")
        number_of_samples = round(len(data) * self.target_sample_rate / sample_rate)
        self.data_audio_file = sps.resample(data, number_of_samples, window="triang")
        self.logger.debug(f"new sample rate: {self.target_sample_rate}")


        max_val = np.max(np.abs(self.data_audio_file))
        if max_val != 0:
            target_max_val = (32767 * AudioUIApp.db_to_float(-1.0))
            self.data_audio_file = AudioUIApp.normalize(self.data_audio_file, max_val, target_max_val)
            # self.data_audio_file = AudioUIApp.butter_lowpass_filter(data=self.data_audio_file,
                                    # cutoff=6000, sample_rate=self.target_sample_rate, order=5)

        self.data_audio_file = self.data_audio_file.astype(np.int16)

    
    @staticmethod
    def map_int(x, in_min=0, in_max=255, out_min=-32768, out_max=32767):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    
    @staticmethod
    def normalize(data, max_val_input, max_range_val):
        return (data / max_val_input) * max_range_val 

    @staticmethod
    def db_to_float(headroom=0.1):
        return 10 ** (headroom / 20)


    def close_file(self):
        self.logger.info("Close file")
        self.is_file_open = False
        self.play_wav_file = AudioUIApp.PLAY_WAV_FILE_STOP
        self.btn_play_wav_file.setText("Play file")


    def close_connection(self):
        self.logger.info("Close connection")

        self.thr_client_tx_should_work = False
        self.thr_client_rx_should_work = False
        self.connection = False


        if self.socket is None:
            pass
        else:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()

    def disable_mic(self):
        self.logger.info("Disable mic")

        self.play_audio_mic = AudioUIApp.PLAY_MIC_STOP
        self.btn_play_mic.setText("Record")

        if self.stream is None:
            pass
        else:
            self.stream.close()
            self.stream.stop_stream()


    def change_mode_handler(self):
        self.logger.info("Change mode handler")

        if self.current_mode == AudioUIApp.CURRENT_MODE_FILE:
            self.current_mode = AudioUIApp.CURRENT_MODE_MIC
            self.btn_mode_choice.setText("MIC")
            self.text_brows_info.append(f"MIC audio mode")

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
            self.text_brows_info.append(f"File mode")
            self.disable_mic()



    def thread_client_configurations(self):

        self.thr_client_rx = Thread(target=self.rx_task, args=(), daemon=True)
        self.thr_client_tx = Thread(target=self.tx_task, args=(), daemon=True)
        self.thr_file_preparing = Thread(target=self.file_preparing, args=(), daemon=True)

        self.thr_client_rx_should_work = False
        self.thr_client_tx_should_work = False
        self.thr_file_preparing_should_work = False
        self.connection = False

        self.thr_client_rx.start()
        self.thr_client_tx.start()
        self.thr_file_preparing.start()


    def connect_server_handler(self):
        self.logger.info("Connecting to the server handler")

        self.close_connection()

        try:
            self.tcp_ip, self.tcp_port = self.get_ip_address()
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(1.5)
            self.socket.connect((self.tcp_ip, self.tcp_port))
            self.thr_client_tx_should_work = True
            self.thr_client_rx_should_work = True
            self.connection = True
            self.text_brows_info.append(f"Connection to {self.tcp_ip}:{self.tcp_port} successfully")
            self.logger.debug(f"Connection to {self.tcp_ip}:{self.tcp_port} successfully")
        except socket.timeout as ex:
            self.logger.error(f"Socket.timeout. Connection failed: {ex}")
            self.close_connection()
            # self.text_brows_info.clear()
            self.text_brows_info.append(f"Connection failed. Address {self.tcp_ip}:{self.tcp_port}")
        except IndexError as ex:
            self.logger.error(f"IndexError. {ex}")
            # self.text_brows_info.clear()
            self.close_connection()
            self.text_brows_info.append(f"Bad address format!")




    def play_wav_file_handler(self):
        self.logger.info("Play WAV file handler")


        if self.play_wav_file == AudioUIApp.PLAY_WAV_FILE_STOP:
            self.play_wav_file = AudioUIApp.PLAY_WAV_FILE_PLAYING
            self.logger.debug("Play file")
            self.btn_play_wav_file.setText("Stop file")
            self.text_brows_info.append("Uploading file")
        elif self.play_wav_file == AudioUIApp.PLAY_WAV_FILE_PLAYING:
            self.play_wav_file = AudioUIApp.PLAY_WAV_FILE_STOP
            self.btn_play_wav_file.setText("Play file")
            self.logger.debug("Stop file")
            self.text_brows_info.append("Stop uploading file")


    
    def play_audio_mic_handler(self):
        self.logger.info("Play audio MIC handler")

        # if self.current_mode != AudioUIApp.CURRENT_MODE_MIC:
        #     return

        if self.play_audio_mic == AudioUIApp.PLAY_MIC_STOP:
            self.play_audio_mic = AudioUIApp.PLAY_MIC_PLAYING
            self.stream = self.audio.open(format=self.form_1, rate=self.source_sample_rate,
                channels=self.chans, input=True,
                frames_per_buffer=self.chunk)
            self.logger.debug("Recording")
            self.btn_play_mic.setText("Stop")
            self.text_brows_info.append("Microphone recording")
        elif self.play_audio_mic == AudioUIApp.PLAY_MIC_PLAYING:
            self.disable_mic()
            self.logger.debug("Stop recording")
            self.text_brows_info.append("Microphone stop recording")


        
    def get_ip_address(self):
        text_server_address = self.edit_ip_address.text()
        list_address = text_server_address.split(":")
        return list_address[0], int(list_address[1])

    def compress_val(self):
        return 0

    def get_time_period_message(self):
        return self.period

    def set_time_period_message(self, value):
        self.period = value

    def parse_answer_server(self, data):
        data = data.decode("utf-8")

        def_val = AudioUIApp.DEFAULT_TIMEOUT_MSG

        if self.current_mode == AudioUIApp.CURRENT_MODE_FILE:
            def_val = AudioUIApp.DEFAULT_TIMEOUT_MSG
        elif self.current_mode == AudioUIApp.CURRENT_MODE_MIC:
            def_val = AudioUIApp.DEFAULT_MIC_TIMEOUT_MSG
        else:
            def_val = AudioUIApp.DEFAULT_TIMEOUT_MSG
            
        pos_start = data.find("per:")
        pos_end = data.find(",")
        val = 50
        if pos_start != -1 and pos_end != -1:
            val = int(data[pos_start + 4:pos_end])
        
        if val >= 0 and val <= 20:
            self.set_time_period_message(def_val - 3 * AudioUIApp.DEFAULT_TIMEOUT_MSG_DELTA)
        elif val >= 20 and val < 30:
            self.set_time_period_message(def_val - 2 * AudioUIApp.DEFAULT_TIMEOUT_MSG_DELTA)
        elif val >= 30 and val < 40:
            self.set_time_period_message(def_val - AudioUIApp.DEFAULT_TIMEOUT_MSG_DELTA)
        elif val >= 40 and val < 60:
            self.set_time_period_message(def_val)
        elif val >= 60 and val < 70:
            self.set_time_period_message(def_val + AudioUIApp.DEFAULT_TIMEOUT_MSG_DELTA)
        elif val >= 70 and val < 80:
            self.set_time_period_message(def_val + 2 * AudioUIApp.DEFAULT_TIMEOUT_MSG_DELTA)
        elif val >= 80:
            self.set_time_period_message(def_val + 3 * AudioUIApp.DEFAULT_TIMEOUT_MSG_DELTA)

            
        print(f"pers: {val}")

 
    def tx_task(self):

        # first_message = True
        
        while True:
            if self.thr_client_tx_should_work is True and self.play_wav_file == AudioUIApp.PLAY_WAV_FILE_PLAYING and \
                self.is_file_open is True and self.current_mode == AudioUIApp.CURRENT_MODE_FILE:
                
                message = None

                message = self.data_audio_file[self.number_frame * AudioUIApp.MSG_LEN_BYTES: (self.number_frame + 1) * AudioUIApp.MSG_LEN_BYTES]

                if self.number_frame >= int(len(self.data_audio_file) / AudioUIApp.MSG_LEN_BYTES):
                    self.number_frame = 0

                try:
                    self.socket.send(message)
                    self.number_frame += 1
                except socket.timeout as ex:
                    self.logger.error(f"Send message error. {ex}")

                period = self.get_time_period_message()
                message = None


                # if first_message is True:
                #     period = 0.5
                #     first_message = False

                Event().wait(period)



            elif self.thr_client_tx_should_work is True and self.play_audio_mic == AudioUIApp.PLAY_MIC_PLAYING and \
                 self.current_mode == AudioUIApp.CURRENT_MODE_MIC:
                try:

                    message = None
                    data = self.stream.read(self.chunk)
                    message = np.frombuffer(data, dtype=np.int16)
                    number_of_samples = round(len(message) * self.target_sample_rate / self.source_sample_rate)
                    # message = sps.resample(message, number_of_samples)
                    message = sps.resample(message, number_of_samples, window="bohman")

                    message = message.astype(np.int16)
                    message = message.tobytes()
                    self.socket.send(message)
                    message = None

                except AttributeError as ex:
                    self.logger.warning(f"AttributeError MIC. {ex}")
                    continue
                except OSError as ex:
                    self.logger.warning(f"OSError MIC. {ex}")
                    continue

                period = self.get_time_period_message()
                Event().wait(0.005)

            elif self.connection is True:

                try:
                    self.socket.send("0".encode("utf-8"))
                    # pass
                except socket.timeout as ex:
                    self.logger.debug(f"{ex}")
                except AttributeError as ex:
                    # self.logger.debug(f"{ex}")
                    pass
                except OSError as ex:
                    self.logger.debug(f"test{ex}")

                Event().wait(0.1)
            else:
                Event().wait(0.1)

            


    def rx_task(self):
        while True:
            if self.thr_client_rx_should_work is True and self.connection is True:

                try:
                    recv_data = self.socket.recv(32)
                    if recv_data == "":
                        continue
                    self.parse_answer_server(recv_data)

                except socket.timeout as ex:
                    continue

                except:
                    continue

                Event().wait(0.001)

            else:                
                Event().wait(0.001)
    
    def file_preparing(self):
      
        while True:
            if self.thr_file_preparing_should_work is True:

                try:
                    self.text_brows_info.append("Wait for the upload to complete")
                    self.parse_wav_file(self.file_name_url)
                    self.text_brows_info.append("Upload successful")
                    self.is_file_open = True
                except FileNotFoundError as ex:
                    self.logger.error(f"File open error. {ex}")
                    self.text_brows_info.append(f"File not found!")
                    self.is_file_open = False
                except ValueError as ex:
                    self.logger.error(f"Parse WAV file error. {ex}")
                    self.text_brows_info.append(f"File must have the format '.wav'.")
                    self.is_file_open = False

                self.thr_file_preparing_should_work = False


            Event().wait(0.1)


def main():
    logging.basicConfig(level=logging.DEBUG, format='%(name)s:[%(levelname)s]: %(message)s')

    app = QApplication(sys.argv)
    form = AudioUIApp()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()