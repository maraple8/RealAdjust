def autoLoad(self):
    # 自动测试时的代码，发行前删除
    fpath = r'C:\Users\80473\Desktop\pyProject\GUI\DaChuangProject\resource\平纵断面偏差.xlsx'
    fname = fpath.split('\\')[-1]
    # 放入fileTableWidget
    item = QTableWidgetItem()
    item.setText(fname)
    # item.setFlags(Qt.ItemFlag.NoItemFlags)
    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # 对齐
    self.fileTableWidget.setItem(self.fileCnt, 0, item)

    # Dialstack添加数据

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

    self.fileTableWidget.setCurrentCell(0, 0)

    self.fileCnt += 1  # 加载文件数 + 1