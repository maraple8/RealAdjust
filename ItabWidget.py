import sys

from PyQt5.QtWidgets import QWidget, QApplication, QTabWidget

class ItabWidget(QTabWidget):
    def __init__(self, Vfig, Hfig):
        super(ItabWidget, self).__init__()
        self.Hfig = Hfig
        self.Vfig = Vfig
        self.initUi()

    def initUi(self):
        self.setWindowTitle('QTabWidgetDemo')
        self.resize(400, 300)

        self.tab1 = self.Vfig
        self.tab2 = self.Hfig

        self.addTab(self.tab1, '纵断面')
        self.addTab(self.tab2, '平面')

        self.setTabPosition(QTabWidget.West)
        self.setTabBarAutoHide(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = ItabWidget()
    mainWin.show()
    sys.exit(app.exec_())