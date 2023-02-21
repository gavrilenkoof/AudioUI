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
import audioop


from scipy.io import wavfile
import scipy.signal as sps
import numpy as np

TCP_IP = '192.168.100.10'
TCP_PORT = 7


# class ClientTCP:

#     def __init__(self, host_address=0):
#         self.host_address = 0
#         self.connect = False



class AudioUIApp(QtWidgets.QMainWindow, AudioUI.Ui_MainWindow):

    DEFAULT_TIMEOUT_MSG = 0.030
    # DEFAULT_TIMEOUT_MSG = 0.015
    DEFAULT_TIMEOUT_MSG_DELTA = 0.006
    DEFAULT_MIC_TIMEOUT_MSG = 0.007
    SOURCE_SAMP_WIDTH = 2
    TARGET_SAMP_WIDTH = 1
    UINT8_BIAS = 128
    MSG_LEN_BYTES = 512 # 1024 for 16sign


    def __init__(self, parent=None):
        super(AudioUIApp, self).__init__(parent)
        self.setupUi(self)

        # self.connection = ClientTCP()

        self.logger = logging.getLogger('Main Window')

        self.socket = None
        self.connection = False

        self.audio_file = None
        self.is_file_open = False
        self.is_connect_mic = False
        self.play_wav_file = False
        self.play_audio_mic = False
        self.mode_play_file = True

        
        self.period = AudioUIApp.DEFAULT_TIMEOUT_MSG

        self.form_1 = pyaudio.paInt16 
        self.chans = 1 
        self.source_sample_rate = 44100
        self.target_sample_rate = 16000

        self.chunk = int(AudioUIApp.MSG_LEN_BYTES * (self.source_sample_rate / self.target_sample_rate)) # for converting 44100 to 8000 format and payload = 512
        # self.chunk = 512
        self.number_frame = 0
        # self.chunk = 5645

        self.audio = pyaudio.PyAudio()
        self.stream = None
        # self.ratio = self.target_sample_rate / self.source_sample_rate
        # self.stream_output = None
        
        self.thread_client_configurations()

        self.widjet_adjust()
        self.widjet_functional()
    
    def widjet_functional(self):
        # Button's handlers
        self.btn_load_wav_file.clicked.connect(self.load_wav_file_handler)
        self.btn_connect_to_server.clicked.connect(self.connect_server_handler)
        self.btn_mode_choice.clicked.connect(self.change_mode_handler)
        self.btn_connect_mic.clicked.connect(self.connect_mic_handler)
        
        self.btn_play_wav_file.clicked.connect(self.play_wav_file_handler)
        self.btn_play_mic.clicked.connect(self.play_audio_mic_handler)

    def widjet_adjust(self):

        self.btn_play_wav_file.setText("Play file")
        self.btn_play_mic.setText("Record")
        self.edit_ip_address.setText("192.168.100.10:7")

    def closeEvent(self, event):
        self.logger.info("Close main window")
        self.close_connection()
        self.play_wav_file = False
        self.play_audio_mic = False
        self.close_file()
        
    def load_wav_file_handler(self):
        self.logger.info("Load wav file handler")

        # close prev file
        self.close_file()

        try:
            file_name_url, _ = QFileDialog.getOpenFileName(self)
            self.logger.debug(f"Get file name: {file_name_url}")

            file_name = QUrl.fromLocalFile(file_name_url).fileName()

            # self.text_brows_info.clear()
            self.text_brows_info.append(f"File name: {file_name}")
            self.text_brows_info.append(f"Convert to {self.target_sample_rate} Hz format")

            self.is_file_open = True

            self.parse_wav_file(file_name_url)
        except FileNotFoundError as ex:
            self.logger.error(f"File open error. {ex}")
            # self.text_brows_info.clear()
            self.text_brows_info.append(f"File not found!")
            self.is_file_open = False

    
    def parse_wav_file(self, file_name_url):

        self.logger.info("Parse wav file")

        # try:
        #     self.audio_file = wave.open(file_name_url, 'r')
        #     number_frames = self.audio_file.getnframes()
        #     frame_rate = self.audio_file.getframerate()
        #     # stat = self.audio_file.getparams()
        #     self.logger.debug(f"number_frames: {number_frames}")
        #     self.logger.debug(f"frame_rate: {frame_rate}")

        #     # self.text_brows_info.append(f"frame rate: {frame_rate} Hz")
        # except wave.Error as ex:
        #     self.logger.error(f"Parse WAV file error: {ex}")
        #     # self.text_brows_info.clear()
        #     self.text_brows_info.append(f"File must have the format '.wav'.")
        #     self.is_file_open = False
        # self.number_frame = 0
        # sample_rate, data = wavfile.read(file_name_url)
        # number_of_samples = round(len(data) * self.target_sample_rate / sample_rate)
        # self.logger.debug(f"source sample rate: {sample_rate}")
        # self.data_audio_file = sps.resample(data, number_of_samples)
        # self.data_audio_file = self.data_audio_file.astype(np.uint8)
        # self.data_audio_file = self.data_audio_file[:].tobytes()
        # self.logger.debug(f"new sample rate: {self.target_sample_rate}")

        self.number_frame = 0
        sample_rate, data = wavfile.read(file_name_url)
        number_of_samples = round(len(data) * self.target_sample_rate / sample_rate)
        self.logger.debug(f"source sample rate: {sample_rate}")
        self.data_audio_file = sps.resample(data, number_of_samples)
        self.data_audio_file = self.data_audio_file.astype(np.int16)
        self.logger.debug(f"new sample rate: {self.target_sample_rate}")


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

        self.connection = False


        if self.socket is None:
            pass
        else:
            self.socket.close()

    def disable_mic(self):
        self.logger.info("Disable mic")

        if self.stream is None:
            pass
        else:
            self.stream.stop_stream()
            self.stream.close()


    def change_mode_handler(self):
        self.logger.info("Change mode")
        self.mode_play_file = not self.mode_play_file

        if self.mode_play_file is True:
            self.btn_mode_choice.setText("File")
            self.text_brows_info.append(f"File playback mode")
        else:
            self.btn_mode_choice.setText("MIC")
            self.text_brows_info.append(f"MIC audio mode")


    def thread_client_configurations(self):

        self.thr_client_rx = Thread(target=self.rx_task, args=(), daemon=True)
        self.thr_client_tx = Thread(target=self.tx_task, args=(), daemon=True)

        self.thr_client_rx_should_work = False
        self.thr_client_tx_should_work = False
        self.connection = False

        self.thr_client_rx.start()
        self.thr_client_tx.start()

    def connect_mic_handler(self):
        self.logger.info("Connecting to the MIC handler")

        self.is_connect_mic = True

        self.disable_mic()

        self.text_brows_info.append(f"Enable MIC")
        

    def connect_server_handler(self):
        self.logger.info("Connecting to the server handler")

        try:
            tcp_ip, tcp_port = self.get_ip_address()

            # self.text_brows_info.clear()
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(1.5)
            self.socket.connect((tcp_ip, tcp_port))
            self.thr_client_tx_should_work = True
            self.thr_client_rx_should_work = True
            self.connection = True
            self.text_brows_info.append(f"Connection to {tcp_ip}:{tcp_port} successfully")
            self.logger.debug(f"Connection to {tcp_ip}:{tcp_port} successfully")
        except socket.timeout as ex:
            self.logger.error(f"Socket.timeout. Connection failed: {ex}")
            self.close_connection()
            # self.text_brows_info.clear()
            self.text_brows_info.append(f"Connection failed. Address {tcp_ip}:{tcp_port}")
        except IndexError as ex:
            self.logger.error(f"IndexError. {ex}")
            # self.text_brows_info.clear()
            self.close_connection()
            self.text_brows_info.append(f"Bad address format!")


    def play_wav_file_handler(self):
        self.logger.info("Play WAV file handler")

        self.play_wav_file = not self.play_wav_file

        if self.play_wav_file:
            self.logger.debug("Play file")
            self.btn_play_wav_file.setText("Stop file")
            self.text_brows_info.append("Uploading file")
        else:
            self.btn_play_wav_file.setText("Play file")
            self.logger.debug("Stop file")
            self.text_brows_info.append("Stop uploading file")

    
    def play_audio_mic_handler(self):
        self.logger.info("Play audio MIC handler")

        self.play_audio_mic = not self.play_audio_mic

        if self.play_audio_mic:
            self.stream = self.audio.open(format=self.form_1, rate=self.source_sample_rate, 
                channels=self.chans, input = True,
                frames_per_buffer=self.chunk)
            self.logger.debug("Recording")
            self.btn_play_mic.setText("Stop")
            self.text_brows_info.append("Microphone recording")
        else:
            self.disable_mic()
            self.logger.debug("Stop recording")
            self.btn_play_mic.setText("Record")
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

    def parse_data(self, data):
        data = data.decode("utf-8")

        def_val = AudioUIApp.DEFAULT_TIMEOUT_MSG

        if self.play_audio_mic is True:
            def_val = AudioUIApp.DEFAULT_MIC_TIMEOUT_MSG
            # print("MIC")
        elif self.play_wav_file is True:
            def_val = AudioUIApp.DEFAULT_TIMEOUT_MSG
            # print("Audio")
        else:
            def_val = AudioUIApp.DEFAULT_TIMEOUT_MSG
            # print("Def")

        if data.find("fastly") != -1:
            self.set_time_period_message(def_val - AudioUIApp.DEFAULT_TIMEOUT_MSG_DELTA)
        elif data.find("slowly") != -1:
            self.set_time_period_message(def_val + AudioUIApp.DEFAULT_TIMEOUT_MSG_DELTA)
        elif data.find("normal") != -1:
            self.set_time_period_message(def_val)
            
        pos_start = data.find("per:")
        pos_end = data.find(",")
        if pos_start != -1 and pos_end != -1:
            print(data[pos_start:pos_end], self.period)
 
    def tx_task(self):
        
        cvstate_mic = None
        cvstate_audio = None
        number = 0

        while True:
            if self.thr_client_tx_should_work is True and self.play_wav_file is True and self.is_file_open is True and self.mode_play_file is True:
                
                # wave_bytes = self.audio_file.readframes(512)
                # message = ""
                # for i in range(0, len(wave_bytes)):
                #     message += hex(wave_bytes[i])[2:]
                # message = message.encode("utf-8")
                # # print(len(message))
                # self.socket.send(message)
                # period = self.get_time_period_message()
                # Event().wait(period)
                
                # read_bytes = int(1024 * (self.source_sample_rate / self.target_sample_rate))
                # # wave_bytes = self.audio_file.readframes(1024)
                # wave_bytes = self.audio_file.readframes(read_bytes)
                # message, cvstate_audio = audioop.ratecv(wave_bytes, 1, 1, self.source_sample_rate, self.target_sample_rate, cvstate_audio, 10, 10)
                # # message = wave_bytes
                # self.socket.send(message)
                # period = self.get_time_period_message()
                # print(len(message), period)
                # Event().wait(period)

                # message = self.data_audio_file[self.number_frame * AudioUIApp.MSG_LEN_BYTES: (self.number_frame + 1) * AudioUIApp.MSG_LEN_BYTES]
                # self.number_frame += 1

                # if self.number_frame >= int(len(self.data_audio_file) / AudioUIApp.MSG_LEN_BYTES):
                #     self.number_frame = 0

                # self.socket.send(message)
                # period = self.get_time_period_message()
                # print(len(message), period)
                # Event().wait(period)




                message = self.data_audio_file[self.number_frame * AudioUIApp.MSG_LEN_BYTES: (self.number_frame + 1) * AudioUIApp.MSG_LEN_BYTES]
                self.number_frame += 1

                if self.number_frame >= int(len(self.data_audio_file) / AudioUIApp.MSG_LEN_BYTES):
                    self.number_frame = 0
                    
                self.socket.send(message)
                period = self.get_time_period_message()
                print(len(message), period)
                Event().wait(period)

                # message = self.data_audio_file[self.number_frame * AudioUIApp.MSG_LEN_BYTES: (self.number_frame + 1) * AudioUIApp.MSG_LEN_BYTES]
                # self.number_frame += 1

                # # print(message[0], message[1])

                # if self.number_frame >= int(len(self.data_audio_file) / AudioUIApp.MSG_LEN_BYTES):
                #     self.number_frame = 0

                # self.socket.send(message)
                # period = self.get_time_period_message()
                # print(len(message), period)
                # Event().wait(period)




            elif self.thr_client_tx_should_work is True and self.play_audio_mic is True and self.is_connect_mic is True and self.mode_play_file is False:
                try:
                    # data = self.stream.read(self.chunk)
                    
                    # message = audioop.lin2lin(data, AudioUIApp.SOURCE_SAMP_WIDTH, AudioUIApp.TARGET_SAMP_WIDTH)
                    # message = audioop.bias(message, AudioUIApp.TARGET_SAMP_WIDTH, AudioUIApp.UINT8_BIAS)
                    # message = np.frombuffer(message, dtype=np.uint8)
                    # number_of_samples = round(len(message) * self.target_sample_rate / self.source_sample_rate)
                    # message = sps.resample(message, number_of_samples)
                    # message = message.astype(np.uint8)
                    # message = message[:].tobytes()
                    # print(type(message))
                    # self.socket.send(message)

                    # print(len(message))

                    data = self.stream.read(self.chunk)
                    
                    # message = audioop.lin2lin(data, AudioUIApp.SOURCE_SAMP_WIDTH, AudioUIApp.TARGET_SAMP_WIDTH)
                    # message = audioop.bias(message, AudioUIApp.TARGET_SAMP_WIDTH, AudioUIApp.UINT8_BIAS)
                    # print(len(data))
                    message = np.frombuffer(data, dtype=np.int16)
                    number_of_samples = round(len(message) * self.target_sample_rate / self.source_sample_rate)
                    message = sps.resample(message, number_of_samples)
                    message = message.astype(np.int16)
                    message = message[:].tobytes()
                    self.socket.send(message)
                    # print(len(message), message[:10])

                except:
                    continue

                period = self.get_time_period_message()
                Event().wait(0.005)

            else:
                Event().wait(0.1)



    def rx_task(self):
        while True:
            if self.thr_client_rx_should_work is True and self.connection is True:

                try:
                    recv_data = self.socket.recv(64)
                    if recv_data == "":
                        continue
                    self.parse_data(recv_data)

                except socket.timeout as ex:
                    continue

                except:
                    continue

                Event().wait(0.001)

            else:                
                Event().wait(0.001)
    

def main():
    logging.basicConfig(level=logging.DEBUG, format='%(name)s:[%(levelname)s]: %(message)s')

    app = QApplication(sys.argv)
    form = AudioUIApp()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()