'''
封装一个自定义的画图控件类
包含一张子图 (axes)

'''
import sys
import numpy as np
import matplotlib

matplotlib.use("Qt5Agg")

from PyQt5.QtWidgets import QApplication,QSizePolicy
from PyQt5.QtCore import pyqtSignal, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from Adjuster import Vadjuster

class figureWidget(FigureCanvas):
    ani_status_changed = pyqtSignal(bool)
    re_calced = pyqtSignal(int, int)

    def __init__(self, fpath, flag, parent=None):
        plt.rcParams['font.family'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        self.initUI()
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.Vadj = Vadjuster(fpath, flag)

        '''======非线形动画参数====='''
        self.Hz = 30                          # 动画帧率
        self.sec = 0.8                          # 动画维持时间
        self.t_vmax = 0.25
        self.frameCnt = int(self.Hz * self.sec)    # 动画帧总数

        self.create_animation_route()

    def initUI(self):
        self.fig = Figure()  # Figure类，继承自FigureBase
        self.ax = self.fig.add_subplot(111)
        self.ax.spines['top'].set_color('none')
        self.ax.spines['right'].set_color('none')
        self.ax.xaxis.set_major_locator(plt.MultipleLocator(200))
        self.ax.grid(
            linestyle='-',
            which='major',
            axis='both',
            color='gray',
            linewidth=0.75,
            alpha=0.5)
        plt.tight_layout()

    def animate(self):
        print('animate start')
        self.ani_status_changed.emit(True)
        '''Hz:帧率  sec:动画时间'''

        self.route_copy = self.ani_route.copy() * len(self.Vadj.Mile)
        self.curFrameCnt = 1

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_figure)
        self.timer.start(int(1000/self.Hz))

    def update_figure(self):
        self.ax.cla()

        self.ax.plot(self.Vadj.Mile, self.Vadj.VDeviation_orign, linewidth=0.8, c='b', alpha=0.9, label = '原始偏差')

        self.ax.plot(
            self.Vadj.Mile[0 : int(self.route_copy[self.curFrameCnt])], self.Vadj.finSmoothLine[0 : int(self.route_copy[self.curFrameCnt])],
            linewidth=1, c='g', alpha=1, label = '调后偏差')

        self.ax.plot(self.Vadj.Mile, self.Vadj.VUpperRestriction, linewidth=0.75, c='orangered', alpha=0.9, label = '调整上、下限')
        self.ax.plot(self.Vadj.Mile, self.Vadj.VLowerRestriction, linewidth=0.75, c='orangered', alpha=0.9)

        self.ax.grid(
            linestyle='-', which='major', axis='both', color='gray', linewidth=0.75, alpha=0.5)
        self.ax.legend()
        self.draw()
        self.curFrameCnt += 1

        if self.curFrameCnt == self.frameCnt:
            self.timer.stop()
            print('animate stop')
            self.ani_status_changed.emit(False)

    def create_animation_route(self):
        '''创造一个动画 s-t 图像   t:速度最大时的时间百分数'''
        t=self.t_vmax
        self.timespace = np.linspace(0,1,self.frameCnt)                       # 时间序列

        A = np.matrix([[t**2, -(t - 1)**2],[t, 1 - t]]).I
        ab = np.array(np.dot(A, np.matrix([[1], [0]]))).reshape(2,)           # 系数

        s1 = np.array(ab[0] * self.timespace ** 2)[0 : int(self.frameCnt * t)]
        s2 = np.array(ab[1] * (self.timespace - 1) ** 2 + 1)[int(self.frameCnt * t) : self.frameCnt]
        self.ani_route = np.append(s1,s2)        # 路程序列



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = figureWidget('./resource/平纵断面偏差.xlsx', 'V')
    ui.show()
    sys.exit(app.exec_())
