import sys

from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import QtCore
from resource.ui_MainWindow import Ui_MainWindow
from faceWidget import FaceWidget
from PyQt5.QtGui import QIcon

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.initUI()

    def initUI(self):
        self.setupUi(self)
        self.resize(1300, 900)
        self.setMinimumSize(QtCore.QSize(1150, 800))
        self.setWindowTitle('RailAdjust V1.0.0')
        self.face = FaceWidget()
        self.setCentralWidget(self.face)
        self.actionload.triggered.connect(self.face.loadFile)
        self.actionsave.triggered.connect(self.face.saveFile)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    mainWin = MainWindow()
    app.setWindowIcon(QIcon('./resource/images/logo_ico.ico'))
    mainWin.show()
    sys.exit(app.exec_())