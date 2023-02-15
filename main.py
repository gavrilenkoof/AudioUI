from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QFileDialog
from PyQt5.QtCore import QUrl
import sys
import AudioUI
import logging

import wave, struct
from threading import Thread


class AudioUIApp(QtWidgets.QMainWindow, AudioUI.Ui_MainWindow):
    def __init__(self, parent=None):
        super(AudioUIApp, self).__init__(parent)
        self.setupUi(self)

        self.logger = logging.getLogger('Main Window')
        self.open_file = None

        self.init_app()

        self.widjet_adjust()
        self.widjet_functional()
    
    def widjet_functional(self):
        # Button's handlers
        self.btn_load_wav_file.clicked.connect(self.load_wav_file_handler)
        self.btn_connect_to_server.clicked.connect(self.connect_server_handler)



    def widjet_adjust(self):
        pass

    def init_app(self):
        self.logger.info("Init main window")

    def closeEvent(self, event):
        self.logger.info("Close main window")
        self.close_file()

        pass


    def load_wav_file_handler(self):
        self.logger.info("Load wav file handler")

        # close prev file
        self.close_file()

        file_name_url, _ = QFileDialog.getOpenFileName(self)
        self.logger.debug(f"Get file name: {file_name_url}")

        file_name = QUrl.fromLocalFile(file_name_url).fileName()

        self.text_brows_wav_file_info.clear()
        self.text_brows_wav_file_info.append(file_name)

        self.parse_wav_file(file_name_url)

    
    def parse_wav_file(self, file_name_url):
        self.logger.info("Parse wav file")

        self.open_file = wave.open(file_name_url, 'r')
        number_frames = self.open_file.getnframes()
        frame_rate = self.open_file.getframerate()

        self.logger.debug(f"number_frames: {number_frames}")
        self.logger.debug(f"frame_rate: {frame_rate}")

        self.text_brows_wav_file_info.append(f"frame rate: {frame_rate} Hz")


    def close_file(self):

        if self.open_file is None:
            return
        else:
            self.open_file.close()



    def connect_server_handler(self):
        self.logger.info("Connect to server handler")
    

def main():
    logging.basicConfig(level=logging.DEBUG, format='%(name)s:[%(levelname)s]: %(message)s')

    app = QApplication(sys.argv)
    form = AudioUIApp()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()