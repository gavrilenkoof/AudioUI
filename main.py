from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication
import sys
import AudioUI
import logging



class AudioUIApp(QtWidgets.QMainWindow, AudioUI.Ui_MainWindow):
    def __init__(self, parent=None):
        super(AudioUIApp, self).__init__(parent)
        self.setupUi(self)

        self.logger = logging.getLogger('App')

        self.init_app()

        self.widjet_adjust()
        self.widjet_functional()
    
    def widjet_functional(self):
        pass

    def widjet_adjust(self):
        pass

    def init_app(self):
        self.logger.info("Init app")

    def closeEvent(self, event):
        self.logger.info("Close app")

        # reply = QMessageBox.question(self, 'Message',
        #     "Are you sure to quit?", QMessageBox.Yes |
        #     QMessageBox.No, QMessageBox.No)

        # if reply == QMessageBox.Yes:
        #     event.accept()
        # else:
        #     event.ignore()
        pass
    

def main():
    logging.basicConfig(level=logging.DEBUG, format='%(name)s:[%(levelname)s]: %(message)s')

    app = QApplication(sys.argv)
    form = AudioUIApp()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()