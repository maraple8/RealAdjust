import sys

from PyQt5.QtWidgets import QWidget, QApplication
from resource.ui_IdialWidget import Ui_dialWidget


class IdialWidget(QWidget, Ui_dialWidget):
    def __init__(self):
        super(IdialWidget, self).__init__()
        self.setWindowTitle('mainWindow')

        self.initUI()

    def initUI(self):
        self.setupUi(self)
        self.Dial_windowlength.valueChanged['int'].connect(self.on_window_length_changed)
        self.Dial_up_able.valueChanged['int'].connect(self.on_up_ableIdx_Changed)
        self.Dial_low_able.valueChanged['int'].connect(self.on_low_ableidx_Changed)

    def on_window_length_changed(self, value):
        self.label_windowlength.setText(f'平滑窗口长度: {value} (5-40)')

    def on_up_ableIdx_Changed(self, value):
        self.label_ableidx.setText(f'上可调系数: {value/100:.2f} (0.00-0.90)')

    def on_low_ableidx_Changed(self, value):
        self.label_3.setText(f'下可调系数: {value/100:.2f} (0.00-0.90)')

    def on_re_calc(self, up_ableidx, low_ableidx):
        self.on_up_ableIdx_Changed(up_ableidx)
        self.on_low_ableidx_Changed(low_ableidx)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = IdialWidget()
    mainWin.show()
    sys.exit(app.exec_())