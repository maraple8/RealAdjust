'''
widowlength:平滑处理的窗口长度
up_ableidx:压缩时的向上可移动系数
low_ableidx:压缩时的向下可移动系数
'''
from PyQt5.QtCore import QObject, pyqtSignal
import numpy as np
import xlrd

class Vadjuster(QObject):
    '''调整断面的类，初始化传入文件路径，获取偏差量和上下限
    handleCalc计算调整量'''
    calc_start = pyqtSignal(bool)
    calc_end = pyqtSignal(bool)

    def __init__(self, fpath, flag):
        super(Vadjuster, self).__init__()
        self.fpath = fpath

        self.getData(flag)

    def setParam(self, window_length, up_ableidx, low_ableidx):

        self.up_ableidx = up_ableidx             # 0.5-1之间
        self.low_ableidx = low_ableidx           # 0.5-1之间

        self.up_saveidx = 0.9 - self.up_ableidx
        self.low_saveidx = 0.9 - self.low_ableidx

        self.window_length = window_length

    def setRestrictions(self, up_Shift, low_Shift):
        '''设置上下限'''
        self.up_Shift = up_Shift
        self.low_Shift = low_Shift
        self.VUpperRestriction = self.VDeviation_orign + up_Shift
        self.VLowerRestriction = self.VDeviation_orign - low_Shift

    def handleCalc(self):
        self.VDeviation = self.VDeviation_orign.copy()  # 拷贝一份

        self.compress(self.up_ableidx, self.low_ableidx)
        self.strighten(self.VDeviation, self.up_saveidx, self.low_saveidx)
        self.fitting_using_np(self.window_length)

    def getData(self, flag):
        # 获取文件里的里程数、纵断面偏差和上下限
        # flag 指出要处理平面还是纵断面
        book = xlrd.open_workbook(self.fpath)
        sheet = book.sheet_by_index(0)

        if flag == 'V':
            self.Mile = np.array(sheet.col_values(0, 1), dtype='i4')                 # 里程数
            self.VDeviation_orign = np.array(sheet.col_values(2, 1), dtype='f4')     # 偏差值
            self.VDeviation = self.VDeviation_orign.copy()                           # 拷贝一份

        elif flag == 'H':
            self.Mile = np.array(sheet.col_values(0, 1), dtype='i4')              # 里程数
            self.VDeviation_orign = np.array(sheet.col_values(1, 1), dtype='f4')  # 偏差值
            self.VDeviation = self.VDeviation_orign.copy()                        # 拷贝一份

    def compress(self, up_ableidx, low_ableidx):
        '''压缩到近0的位置'''
        for i in range(len(self.VDeviation)):
            if self.VDeviation[i] > 0:  # 需要下移
                low_ableDistance = low_ableidx * (self.VDeviation[i] - self.VLowerRestriction[i])
                if self.VDeviation[i] - low_ableDistance <= 0:  # 可以移到0
                    self.VDeviation[i] = 0
                else:                                  # 不可以移到0
                    self.VDeviation[i] -= low_ableDistance
            else:                       # 需要上移
                up_ableDistance = up_ableidx * (self.VUpperRestriction[i] - self.VDeviation[i])
                if self.VDeviation[i] + up_ableDistance >= 0:
                    self.VDeviation[i] = 0
                else:
                    self.VDeviation[i] += up_ableDistance

    def strighten(self, line, up_saveidx, low_saveidx):
        '''拉直'''
        Mile = self.Mile
        i = 0
        while i < len(Mile) - 2:
            idx = 0
            for j in range(i + 2, len(Mile)):
                flag = False
                k = (line[j] - line[i]) / (Mile[j] - Mile[i])
                for cnt in range(i+1, j):
                    value = line[i] + k * (Mile[cnt] - Mile[i])
                    up_closest = up_saveidx * (self.up_Shift)
                    low_closest = low_saveidx * (self.low_Shift)
                    if self.VLowerRestriction[cnt] < value - low_closest and value + up_closest < self.VUpperRestriction[cnt]:
                        flag = True
                    else:
                        flag = False
                        break
                if flag:
                    idx = j
            if idx:
                k = (line[idx] - line[i]) / (Mile[idx] - Mile[i])
                for i_ in range(i+1, idx):
                    line[i_] = line[i] + k * (Mile[i_] - Mile[i])
                i = idx
            else:
                i += 1

    def fitting_using_np(self, box_pts):
        '''np的卷积进行拟合'''
        box = np.ones(box_pts) / box_pts
        self.finSmoothLine = np.convolve(self.VDeviation, box, mode='same')

    def isOutRange(self):
        flag = False
        for i, y in enumerate(self.finSmoothLine):
            if not self.VLowerRestriction[i] < y < self.VUpperRestriction[i]:
                flag = True
                break
        return flag
