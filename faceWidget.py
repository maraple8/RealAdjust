import sys

import numpy as np
import openpyxl

from PyQt5.QtWidgets import QWidget, QApplication, QFileDialog, QTableWidgetItem, QMenu, QMessageBox
from resource.ui_faceWidget import Ui_faceWidget
from PyQt5.QtCore import Qt
from figureWidget import figureWidget
from IdialWidget import IdialWidget
from ItabWidget import ItabWidget

class FaceWidget(QWidget, Ui_faceWidget):
    def __init__(self):
        super(FaceWidget, self).__init__()
        self.setWindowTitle('mainWindow')
        self.fileCnt = 0     # 当前已加载的文件数
        self.figList = []
        self.initUI()
        # self.autoLoad()      # 自动测试代码

    def initUI(self):
        self.setupUi(self)
        self.removeWidInStack()
        self.fileTableWidget.setColumnWidth(0,260)
        self.fileTableWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.fileTableWidget.customContextMenuRequested.connect(self.showFileContextTableMenu)     # 传递QPoint
        self.fileTableWidget.itemClicked.connect(self.showPage)  # 只有 左键 点击 有item的 行才发送信号
        self.fileTableWidget.setHorizontalHeaderLabels(['Files'])
        for i in range(20):
            self.fileTableWidget.setRowHeight(i,16)

        self.handleCalcBtn.clicked.connect(self.loadedCheck)
        self.up_Shift.valueChanged.connect(self.on_restriction_changed)
        self.low_Shift.valueChanged.connect(self.on_restriction_changed)
        if self.fileCnt == 0:
            dial = IdialWidget()

            self.dataStack.addWidget(dial)
            self.dataStack.setCurrentIndex(self.fileCnt)
            print(self.dataStack.currentIndex())

    def loadedCheck(self):
        if self.fileTableWidget.currentItem() != None:
            self.handleCalc()
        else:
            reply = QMessageBox.critical(self, '提示', '好像还没有选择文件', QMessageBox.Yes)

    def loadFile(self):
        # 加载文件
        try:
            # 获取文件路径
            fpath, _ = QFileDialog.getOpenFileName(self, 'load file', '.', 'excel file(*.xlsx)')
            if fpath:
                # 获取文件名
                fname = fpath.split('/')[-1]

                # 放入fileTableWidget
                item = QTableWidgetItem()
                item.setText(fname)
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # 对齐
                self.fileTableWidget.setItem(self.fileCnt, 0, item)
                self.fileTableWidget.setCurrentCell(self.fileCnt, 0)

                # Dialstack添加数据
                if self.fileCnt != 0:
                    dial = IdialWidget()

                    self.dataStack.addWidget(dial)
                    self.dataStack.setCurrentIndex(self.fileCnt)
                    print(self.dataStack.currentIndex())

                # 从文件获取数据并在graphicStack上画一张图
                Vfig = self.getVData(fpath)  # 纵断面偏差
                Vfig.type = 'V'  # 标记纵断面图
                Vfig.calced = False
                Vfig.ani_status_changed.connect(self.setCalcEnabled)

                Hfig = self.getHData(fpath)  # 平面偏差
                Hfig.type = 'H'  # 标记平面图
                Hfig.calced = False
                Hfig.ani_status_changed.connect(self.setCalcEnabled)

                Ifigtab = ItabWidget(Vfig, Hfig)

                # stack添加数据

                self.graphicStack.addWidget(Ifigtab)
                self.graphicStack.setCurrentIndex(self.fileCnt)
                print(self.graphicStack.currentIndex())

                self.fileCnt += 1  # 加载文件数 + 1
        except:
            pass

    def checkSignal(self, bool):
        print(f'calculeting={bool}')

    def saveFile(self):
        try:
            curTab = self.graphicStack.currentWidget()               # 当前tab
            figlist = [curTab.widget(0), curTab.widget(1)]           # [纵断面，平面]

            if figlist[0].calced and figlist[1].calced:
                fpath, _ = QFileDialog.getSaveFileName(self, 'save file', '.', 'excel file(*.xlsx)')
                # 计算调整量
                figlist[0].Vadj.adjustment = figlist[0].Vadj.finSmoothLine - figlist[0].Vadj.VDeviation_orign
                figlist[1].Vadj.adjustment = figlist[1].Vadj.finSmoothLine - figlist[1].Vadj.VDeviation_orign

                # 创建一个Excel workbook 对象
                book = openpyxl.Workbook()
                sh = book.active
                sh.title = '平纵断面调整量'
                sh.column_dimensions['B'].width = 18
                sh.column_dimensions['C'].width = 18

                # 写标题栏
                sh['A1'] = '里程(m)'
                sh['B1'] = '平面调整量(mm)'
                sh['C1'] = '纵断面调整量(mm)'

                # 写入数据
                datas = np.vstack((figlist[1].Vadj.Mile, figlist[1].Vadj.adjustment, figlist[0].Vadj.adjustment)).T
                for data in datas:
                    sh.append([data[0],round(data[1],2),round(data[2],2)])

                book.save(fpath)
                reply = QMessageBox.information(self, '提示', '保存成功！', QMessageBox.Yes)
            elif figlist[0].calced:
                reply = QMessageBox.critical(self, '提示', '平面调整量还没有计算！', QMessageBox.Yes)
            elif figlist[1].calced:
                reply = QMessageBox.critical(self, '提示', '纵断面调整量还没有计算！', QMessageBox.Yes)
            else:
                reply = QMessageBox.critical(self, '提示', '调整量还没有计算！', QMessageBox.Yes)
        except:
            pass

    def showPage(self, item):    # 左键双击tableitem展示不同excel文件的不同计算界面
        self.graphicStack.setCurrentIndex(item.row())
        self.dataStack.setCurrentIndex(item.row())
        print(f'showPage{item.row()}')
        print(f'Graphicstack in page {self.graphicStack.currentIndex()}')
        print(f'Datastack in page {self.graphicStack.currentIndex()}')

    def getVData(self, fpath):
        # 获取纵断面数据,并在stackWidget上初始化数据
        Vfig = figureWidget(fpath, 'V')
        Vfig.Vadj.setRestrictions(self.up_Shift.value(),self.low_Shift.value())
        # self.figList.append(Vfig)
        Vfig.ax.plot(Vfig.Vadj.Mile, Vfig.Vadj.VDeviation_orign, linewidth=0.8, c='b', alpha=0.9, label = '原始偏差')  # 纵断面偏差
        Vfig.ax.plot(Vfig.Vadj.Mile, Vfig.Vadj.VUpperRestriction, linewidth=0.75, c='orangered', alpha=0.9, label = '调整上、下限')  # 纵断面上限
        Vfig.ax.plot(Vfig.Vadj.Mile, Vfig.Vadj.VLowerRestriction, linewidth=0.75, c='orangered', alpha=0.9)  # 纵断面下限
        Vfig.ax.legend()
        return Vfig

    def getHData(self, fpath):
        # 获取横断面数据,并在stackWidget上初始化数据
        Hfig = figureWidget(fpath, 'H')
        Hfig.Vadj.setRestrictions(self.up_Shift.value(),self.low_Shift.value())
        # self.figList.append(Hfig)
        Hfig.ax.plot(Hfig.Vadj.Mile, Hfig.Vadj.VDeviation_orign, linewidth=0.8, c='b', alpha=0.9, label = '原始偏差')  # 平面偏差
        Hfig.ax.plot(Hfig.Vadj.Mile, Hfig.Vadj.VUpperRestriction, linewidth=0.75, c='orangered', alpha=0.9, label = '调整上、下限')  # 平面上限
        Hfig.ax.plot(Hfig.Vadj.Mile, Hfig.Vadj.VLowerRestriction, linewidth=0.75, c='orangered', alpha=0.9)  # 平面下限
        Hfig.ax.legend()
        return Hfig

    def removeWidInStack(self):  # 删除stackwidget里面的widget
        curWid = self.graphicStack.currentWidget()     # 第一个stack
        while curWid:
            self.graphicStack.removeWidget(curWid)
            curWid = self.graphicStack.currentWidget()
        curWid = self.dataStack.currentWidget()        # 第二个stack
        while curWid:
            self.dataStack.removeWidget(curWid)
            curWid = self.dataStack.currentWidget()

    def showFileContextTableMenu(self, point):  # 右击item时展示菜单
        # 当前选择的行
        self.nowRow = self.fileTableWidget.selectionModel().selection().indexes()[0].row()
        menu = QMenu()
        loadAction = menu.addAction('load')

        # 如果右击的地方没有item则不显示save选项
        if self.fileTableWidget.item(self.nowRow, 0):
            saveAction = menu.addAction('save')
            saveAction.triggered.connect(self.saveFile)      # 连接到保存文件方法

        # 绑定action和功能
        loadAction.triggered.connect(self.loadFile)          # 连接到加载文件方法

        screenpos = self.fileTableWidget.mapToGlobal(point)  # 屏幕坐标，是menu.exec()的参数，menu显示的位置
        action = menu.exec(screenpos)                        # 阻塞，点击选项后才执行下面的代码

    def handleCalc(self):
        self.handleCalcBtn.setEnabled(False)
        curTab = self.graphicStack.currentWidget()
        curFig = curTab.currentWidget()

        curDialWid = self.dataStack.currentWidget()

        window_length = curDialWid.Dial_windowlength.value()           # 参数初始化
        up_ableidx = curDialWid.Dial_up_able.value()/100
        low_ableidx = curDialWid.Dial_low_able.value()/100

        curFig.Vadj.setParam(window_length, up_ableidx, low_ableidx)   # 参数初始化
        curFig.Vadj.setRestrictions(self.up_Shift.value(),self.low_Shift.value())

        # curFig.Vadj.calc_start.emit(True)  # send signal

        curFig.Vadj.handleCalc()
        cnt = 1
        while curFig.Vadj.isOutRange():  # 如果超界了
            curFig.Vadj.setParam(window_length, up_ableidx - cnt * 0.1, low_ableidx - cnt * 0.1)
            print('recalc')
            # curFig.re_calced.emit(int(curFig.Vadj.up_ableidx * 100), int(curFig.Vadj.low_ableidx * 100))
            curDialWid.on_re_calc(int(curFig.Vadj.up_ableidx * 100), int(curFig.Vadj.low_ableidx * 100))
            curFig.Vadj.handleCalc()
        curFig.calced = True

        curFig.animate()

        # curFig.Vadj.calc_end.emit(False)   # send signal

    def on_restriction_changed(self, int):
        curTab = self.graphicStack.currentWidget()
        curFig = curTab.currentWidget()
        curFig.Vadj.setRestrictions(self.up_Shift.value(), self.low_Shift.value())
        curFig.ax.cla()
        if curFig.calced == False:
            curFig.ax.plot(curFig.Vadj.Mile, curFig.Vadj.VDeviation_orign, linewidth=0.8, c='b', alpha=0.9, label='原始偏差')
        else :
            curFig.ax.plot(curFig.Vadj.Mile, curFig.Vadj.VDeviation_orign, linewidth=0.8, c='b', alpha=0.9, label='原始偏差')
            curFig.ax.plot(curFig.Vadj.Mile, curFig.Vadj.finSmoothLine, linewidth=1, c='g', alpha=1, label='调后偏差')
        curFig.ax.plot(curFig.Vadj.Mile, curFig.Vadj.VUpperRestriction, linewidth=0.75, c='orangered', alpha=0.9, label='调整上、下限')
        curFig.ax.plot(curFig.Vadj.Mile, curFig.Vadj.VLowerRestriction, linewidth=0.75, c='orangered', alpha=0.9)
        curFig.ax.grid(
            linestyle='-', which='major', axis='both', color='gray', linewidth=0.75, alpha=0.5)
        curFig.ax.legend()
        curFig.draw()

    def setCalcEnabled(self, bool):
        print('setCalcEnabled')
        self.handleCalcBtn.setEnabled(not bool)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = FaceWidget()
    mainWin.show()
    sys.exit(app.exec_())