#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys, time, os, re
from fixture import Fixture
from data import *
import numpy as np


# 多线程，用来防止界面卡死
class Worker(QThread):
    sinOut = pyqtSignal(dict)# 用来沟通主线程的信号

    def __init__(self, parent=None):
        super(Worker, self).__init__(parent)
        self.working = True #线程工作的标志

    def __del__(self):
        self.working = False
        self.wait()

    # 交换数据
    def translate_data(self, num):
        self.num = num

    # 给串口下指令
    def sendcmd(self, cmd):
        try:
            text = Fixture().senddir(cmd)
            return text
        except Exception as e:
            return str(Exception) + str(e)

    # 覆盖进程中的run函数，自定义
    def run(self):
        # 获取主线程丢过来的数据
        duty = float(self.num.get('duty'))
        cmd = self.num.get('cmd')
        infinite = self.num.get('infinite')

        if infinite:
            while True:
                if self.working:
                    return_results = self.sendcmd(cmd)
                    results = {'return_results': return_results, 'times': '∞'}
                    self.sinOut.emit(results) # 将测量结果丢给主线程
                    time.sleep(duty)
                else:
                    break

        else:
            cycle = self.num.get('cycle')

            for i in range(cycle):
                if self.working:
                    # results = self.sendcmd(cmd)
                    return_results = self.sendcmd(cmd)
                    results = {'return_results': return_results, 'times': i+1}
                    # self.label_showresult.appendPlainText(results)
                    self.sinOut.emit(results)
                    time.sleep(duty)

        self.sinOut.emit({'end':'1'})# 线程结束，返回 标志1，用来开启开始按钮


class UI(QWidget):
    emit_sig = pyqtSignal(dict) # 用来沟通子线程的信号

    def __init__(self):
        app = QApplication(sys.argv)
        app.setWindowIcon(QIcon('./b.ico'))  # 设置UI的icon

        DATA.readini()
        self.filepath = DATA.Log_Directory
        self.unit = ''

        super(UI, self).__init__()
        self.InitUI()
        self.setWindowOpacity(0.9)

        if self.product_isn != '':
        # 初始化设置
            self.textbox1.setText('0.1')
            self.textbox2.setText('5')
            self.rdbutton3.setChecked(1)# !!!
            self.bgClick()

            self.show() # 显示窗口
            app.exit(app.exec_())  # 消息循环结束之后返回0，接着调用sys.exit(0)退出程序
            # app.exec_()--------------消息循环结束之后，进程自然也会结束
        else:
            return


        # self.label_showtime.setText('eeee')

        # sshFile = "./three.qss"
        # with open(sshFile, "r") as fh:
        #     self.setStyleSheet(fh.read())

    # 设置桌面背景
    # def paintEvent(self, event):
        # qp = QPainter()
        # qp.begin(self)
        # self.drawLines(qp)
        # qp.end()
    #     painter = QPainter(self)
    #     painter.setBrush(QBrush(QColor(0xFF, 0xCC, 0xCC)))
    #     painter.drawRect(self.rect())


    def ISN_window(self):
        self.product_isn, okpressed = QInputDialog.getText(self, 'Product No.', 'Please input ISN：', QLineEdit.Normal, '')
        self.product_isn = self.product_isn.strip()

        if self.product_isn != '' and okpressed:
            return True
        else:
            return False

    def InitUI(self):
        # 固定窗口大小、设置窗口标题
        self.setFixedWidth(806)
        self.setFixedHeight(580)
        self.setWindowTitle('READ sth.')

        isn_exist = self.ISN_window()
        if not isn_exist:
            return

        # 设置最底层背景，与公司logo的白底一个颜色 1
        self.white_bglabel = QLabel(self)
        self.white_bglabel.resize(1000, 1000)
        pic = QPixmap('2.png')
        self.white_bglabel.setPixmap(pic)
        self.white_bglabel.setScaledContents(True)


        self.bglabel = QLabel(self)
        self.bglabel.resize(900, 500)
        self.bglabel.setAlignment(Qt.AlignBottom)
        self.bglabel1 = QLabel(self)
        self.bglabel1.setGeometry(700, 380, 700, 700)

        # 显示公司logo 2
        logo_label = QLabel(self)
        logo_label.setGeometry(0, 505, 306, 67)
        picture = QPixmap('company_log.png')
        logo_label.setPixmap(picture)
        logo_label.setScaledContents(True)

        self.label_showtimes = QLabel('', self)
        self.label_showtimes.setFont(QFont('Roman times', 20, ))
        self.label_showtimes.setStyleSheet('color:#227700')
        self.label_showtimes.setGeometry(650, 506, 180, 20)

        self.label_showtime = QLabel('', self)
        self.label_showtime.setFont(QFont('Roman times', 20, ))
        self.label_showtime.setStyleSheet('color:#227700')
        self.label_showtime.setGeometry(650, 546, 180, 20)

        self.label_showmax = QLabel(self)
        self.label_showmax.setFont(QFont('Roman times', 20, ))
        self.label_showmax.setStyleSheet('color:#227700')
        self.label_showmax.setGeometry(620, 302, 180, 20)

        self.label_showmin = QLabel(self)
        self.label_showmin.setFont(QFont('Roman times', 20, ))
        self.label_showmin.setStyleSheet('color:#227700')
        self.label_showmin.setGeometry(620, 343, 180, 20)

        self.label_showmean = QLabel(self)
        self.label_showmean.setFont(QFont('Roman times', 20, ))
        self.label_showmean.setStyleSheet('color:#227700')
        self.label_showmean.setGeometry(620, 384, 180, 20)

        self.label_showresult = QPlainTextEdit(self)
        self.label_showresult.setFont(QFont('Microsoft YaHei', 20))
        self.label_showresult.setStyleSheet('color:black')
        self.label_showresult.setGeometry(80, 270, 400, 165)
        self.label_showresult.setReadOnly(True)

        # 显示动态背景 2
        self.gif = QMovie('bggif.gif')
        # self.gif.setCacheMode(QMovie.CacheAll)
        self.gif.setSpeed(5)
        # self.bglabel.setScaledContents(True) #适应窗口
        self.bglabel.setMovie(self.gif)
        self.gif.start()

# ---------------
        self.startButton = QPushButton('start', self)
        self.startButton.setGeometry(200, 450, 95, 40)
        self.startButton.setStyleSheet("QPushButton{color:black;"
                                       "border-style:solid;"
                                       "border-width:2px;"
                                       "border-color: #668800;"
                                       "background:transparent;"
                                       "border-radius:13;"
                                       "padding:2px;"
                                       "font-family:Microsoft YaHei;"
                                       "font-size:30px}"
                                       "QPushButton:hover{color:red}")
        self.startButton.clicked.connect(self.start)

        self.stopButton = QPushButton('stop', self)
        self.stopButton.setGeometry(350, 450, 95, 38)
        self.stopButton.setStyleSheet("QPushButton{color:black;"
                                      "border-style:solid;"
                                      "border-width:2px;"
                                      "border-color: #668800;"
                                      "background:transparent;"
                                      "border-radius:13;"
                                      "padding:2px;"
                                      "font-family:Microsoft YaHei;"
                                      "font-size:30px}"
                                      "QPushButton:hover{color:red}")
        self.stopButton.clicked.connect(self.stop)

        self.singlesendButton = QPushButton('send', self)
        self.singlesendButton.setGeometry(320, 102, 89, 32)
        self.singlesendButton.setStyleSheet("QPushButton{color:black;"
                                            "border-style:solid;"
                                            "border-width:2px;"
                                            "border-color: #668800;"
                                            "background:transparent;"
                                            "border-radius:10;"
                                            "padding:2px;"
                                            "font-family:Microsoft YaHei;"
                                            "font-size:27px}"
                                            "QPushButton:hover{color:red}")
        self.singlesendButton.clicked.connect(self.singlesend)


# ------标签-------------------
        self.label1 = QLabel('Duty:', self)
        self.label1.setFont(QFont('Roman times', 25, ))
        self.label1.move(20, 20)


        self.label2 = QLabel('Cycle:', self)
        self.label2.setFont(QFont('Roman times', 25, ))
        self.label2.move(20, 60)

        self.label3 = QLabel('Cmd:', self)
        self.label3.setFont(QFont('Roman times', 25, ))
        self.label3.move(20, 100)

        self.label4 = QLabel('Mode:', self)
        self.label4.setFont(QFont('Roman times', 25, ))
        self.label4.move(20, 140)

        self.label5 = QLabel(' Voltage:', self)
        self.label5.setFont(QFont('Roman times', 23, ))
        self.label5.move(120, 140)

        self.label6 = QLabel(' Current:', self)
        self.label6.setFont(QFont('Roman times', 23, ))
        self.label6.move(120, 180)

        self.label6 = QLabel('Register:', self)
        self.label6.setFont(QFont('Roman times', 23, ))
        self.label6.move(120, 220)

        self.label7 = QLabel('s/t', self)
        self.label7.setFont(QFont('Roman times', 20, ))
        self.label7.move(320, 25)

        self.label8 = QLabel('times:', self)
        self.label8.setFont(QFont('Roman times', 20, ))
        self.label8.move(570, 505)

        self.label9 = QLabel(' time:', self)
        self.label9.setFont(QFont('Roman times', 20, ))
        self.label9.move(570, 540)

        self.label10 = QLabel('maximum:', self)
        self.label10.setFont(QFont('Roman times', 20, ))
        self.label10.move(510, 300)

        self.label11 = QLabel(' minimum:', self)
        self.label11.setFont(QFont('Roman times', 20, ))
        self.label11.move(510, 340)

        self.label12 = QLabel('       mean:', self)
        self.label12.setFont(QFont('Roman times', 20, ))
        self.label12.move(510, 380)


 # -----编辑框-------------
        self.textbox1 = QLineEdit(self)
        self.textbox1.setGeometry(100, 20, 200, 35)
        self.textbox1.setStyleSheet(
                        """
                        QLineEdit {
                        border: 1px solid gray;
                        border-radius: 5px;
                        color:#444444}
                        """)
        self.textbox1.setAlignment(Qt.AlignRight)
        self.textbox1.setFont(QFont('Microsoft YaHei', 22))
        self.textbox1.setMaxLength(14)

        self.textbox2 = QLineEdit(self)
        self.textbox2.setGeometry(100, 60, 200, 35)
        self.textbox2.setStyleSheet(
                        """
                        QLineEdit {
                        border: 1px solid gray;
                        border-radius: 5px;
                        color:#444444}
                        """)
        self.textbox2.setAlignment(Qt.AlignRight)
        self.textbox2.setFont(QFont('Microsoft YaHei', 22))
        self.textbox2.setValidator(QIntValidator(0, 2147483647))
        self.textbox2.setMaxLength(14)

        self.textcombox3 = QComboBox(self)
        self.textcombox3.setGeometry(100, 100, 200, 35)
        self.textcombox3.setStyleSheet(
            """
            QComboBox {
                border: 1px solid gray;
                border-radius: 5px;
                padding: 5px;
                min-width: 4em;
                font:20px;
                color:#444444;
                font-family:"Microsoft YaHei"}
            QComboBox QAbstractItemView{
                border: 1px solid red;
                selection-background-color:beige;
                selection-color:red;
                font-size: 20px}
            # QComboBox QAbstractItemView:item {height: 25px}
            QListView item:hover {background:green}

            """
# QComboBox{ border:1px solid gray;  border-radius:3px;  padding: 5px; min-width:4em;}
# QComboBox::drop-down{subcontrol-origin:padding; subcontrol-position:top right; width:20px; border-left-width:1px;border-left-color:darkgray; border-left-style:solid; border-top-right-radius:3px; border-bottom-right-radius:3px;}
        )

        self.listwidget = QListWidget(self)
        self.listwidget.setStyleSheet(
            "QListWidget{border:1px solid gray; color:black; }"
            "QListWidget::Item{padding-left:15px }"
            "QListWidget::Item:hover{background:skyblue; }"
            "QListWidget::item:selected{background:lightgray; color:red; }"
            "QListWidget::item:selected:!active{border-width:0px; background:lightgreen; }"
        )
        self.textcombox3.setModel(self.listwidget.model())
        self.textcombox3.setView(self.listwidget)
        self.textcombox3.setEditable(True)
        self.textcombox3.setCurrentIndex(0)

        # 向下拉框内加入条目
        self.listwidget.addItems(DATA.cmd_list)
        # self.combo.currentIndexChanged.connect(self.ww)


# ------单选按钮---------
        self.rdbutton1 = QRadioButton('∞', self)
        self.rdbutton1.setFont(QFont('Roman times', 24, ))
        self.rdbutton1.move(315, 63)
        self.rdbutton1.clicked.connect(self.rdb1Click)

        self.rdbutton2 = QRadioButton('', self)
        self.rdbutton2.setFont(QFont('Roman times', 24, ))
        self.rdbutton2.move(225, 148)

        self.rdbutton3 = QRadioButton('', self)
        self.rdbutton3.setFont(QFont('Roman times', 24, ))
        self.rdbutton3.move(225, 188)

        self.rdbutton4 = QRadioButton('', self)
        self.rdbutton4.setFont(QFont('Roman times', 24, ))
        self.rdbutton4.move(225, 228)

        self.bg = QButtonGroup(self)
        self.bg.addButton(self.rdbutton2, 2)
        self.bg.addButton(self.rdbutton3, 3)
        self.bg.addButton(self.rdbutton4, 4)
        self.bg.buttonClicked.connect(self.bgClick)

# --画直线
#     def paintEvent(self, e):
#         qp = QPainter()
#         qp.begin(self)
#         self.drawLines(qp)
#         qp.end()

    # def drawLines(self, qp):
    #
    #
    #     pen = QPen(Qt.black, 2, Qt.SolidLine)
    #     qp.setPen(pen)
    #     qp.drawLine(20, 40, 250, 40)
    #
    #     pen.setStyle(Qt.DashLine)
    #     qp.setPen(pen)
    #     qp.drawLine(20, 80, 250, 80)
    #
    #     pen.setStyle(Qt.DashDotLine)
    #     qp.setPen(pen)
    #     qp.drawLine(20, 120, 250, 120)
    #
    #     pen.setStyle(Qt.DotLine)
    #     qp.setPen(pen)
    #     qp.drawLine(20, 160, 250, 160)
    #
    #     pen.setStyle(Qt.DashDotDotLine)
    #     qp.setPen(pen)
    #     qp.drawLine(20, 200, 250, 200)
    #
    #     pen.setStyle(Qt.CustomDashLine)
    #     pen.setDashPattern([1, 4, 5, 4])
    #     qp.setPen(pen)
    #     qp.drawLine(20, 240, 250, 240)

# --将科学计数法 取六位小数
    def changeformat(self, data):
        # r = data.rstrip('\n')
        result = '{:.6f}'.format(float(data))
        return result

    def handledata(self, data):
        lis = []
        for i in data:
            lis.append(float(i))

        max = self.changeformat(np.max(lis)) + self.unit
        min = self.changeformat(np.min(lis)) + self.unit
        mean = self.changeformat(np.mean(lis)) + self.unit # mean均值
        self.label_showmax.setText(max)
        self.label_showmin.setText(min)
        self.label_showmean.setText(mean)


# --显示结果-------------------
    def display(self, data):
        # print(data)

        if data.get('end') == '1': # 测试结束发送的标志
            self.startButton.setEnabled(True)
            print(self.handle_datalist)
            self.handledata(self.handle_datalist)

        else:
            return_results = data.get('return_results')
            try:
                num_value = re.compile('[+-][0-9.]+[0-9]+[E|e|^][+-][0-9]+')
                result = num_value.match(return_results)
                if result.group(0):
                    text = self.changeformat(return_results) + self.unit
                    self.logV(text)
                    self.label_showresult.appendPlainText(text)
                    self.handle_datalist.append(return_results)

            except:
                if return_results.startswith('Keysight'):
                    self.logV(return_results)
                else:
                    self.logE(return_results)
                self.label_showresult.appendPlainText(return_results)

        end = time.time()
        delta = '{:.2f} seconds'.format(end - self.start_time)
        self.label_showtime.setText(delta)
        # print(data.get('times'), type(data.get('times')))

        show_times = data.get('times')
        if show_times:
            self.label_showtimes.setText(str(show_times))

            # QApplication.processEvents()
            # 为了实时显示在文本框里，否则会在卡顿之后显示输出全部结果。添加之后也不能保证每个都是逐行显示，只是比不加相对流畅一点，效果是不如多线程的。

    def singlesend(self):
        cmd_text = self.textcombox3.currentText()
        self.label_showresult.clear()
        self.label_showmax.setText('')
        self.label_showmin.setText('')
        self.label_showmean.setText('')

        if self.bg.checkedId() != -1:
            try:
                t = Fixture().senddir(cmd_text)
                print(t)
                num_value = re.compile('[+-][0-9.]+[0-9]+[E|e|^][+-][0-9]+')
                result = num_value.match(t)
                if t.startswith('Keysight'):
                    self.label_showresult.appendPlainText(t)
                    return

                if result.group(0):
                    text = self.changeformat(t) + self.unit
                    self.label_showresult.appendPlainText(text)
            except Exception as e:
                self.label_showresult.appendPlainText(str(Exception) + str(e))

        elif self.bg.checkedId() == -1:
            QMessageBox.information(self, '提示', 'Need to choose the testing model', QMessageBox.Ok)

    def start(self):
        self.start_time = time.time()  # 开始测试时间
        self.handle_datalist = []
        self.label_showmax.setText('')
        self.label_showmin.setText('')
        self.label_showmean.setText('')

        if not self.textbox1.text():
            QMessageBox.information(self, '提示', 'Need to input Duty.', QMessageBox.Ok)
            return
        if not self.textcombox3.currentText():
            QMessageBox.information(self, '提示', 'Need to input Cmd.', QMessageBox.Ok)
            return

        duty = float(self.textbox1.text())
        cmd_text = self.textcombox3.currentText()  # 获取输入的command

        self.thread = Worker()
        self.thread.working = True
        self.emit_sig.connect(self.thread.translate_data)

        self.label_showresult.clear()
        self.startButton.setEnabled(False)


        self.csvfilepath = self.filepath + '/csv/' + time.strftime('%Y-%m-%d', time.localtime(time.time()))
        self.logfilepath = self.filepath + '/log/' + time.strftime('%Y-%m-%d', time.localtime(time.time()))

        # 创建多级目录
        try:
            if not os.path.exists(self.csvfilepath):
                os.makedirs(self.csvfilepath)
            if not os.path.exists(self.logfilepath):
                os.makedirs(self.logfilepath)

        except Exception as e:
            self.label_showresult.appendPlainText(str(Exception) + str(e))

    # 存储文件的绝对路径
        self.csvfilename = self.csvfilepath + '/' + self.product_isn + time.strftime('%Y%m%d%H%M%S', time.localtime(
            time.time())) + '.csv'
        self.csvfilename = self.check_filename(self.csvfilename)
        self.logfilename = self.logfilepath + '/' + self.product_isn + time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) + '.log'
        self.logfilename = self.check_filename(self.logfilename)

        if self.bg.checkedId() != -1:
            # 无限次
            if self.rdbutton1.isChecked():
                try:
                    self.emit_sig.emit({'duty': duty, 'infinite': 1, 'cmd': cmd_text})

                    self.thread.sinOut.connect(self.display)
                    self.thread.start()
                    time.sleep(duty)

                except Exception as e:
                    self.logE(Exception, e)
                    self.label_showresult.appendPlainText(str(Exception) + str(e))

            else:
                # 设置了有限次
                if not self.textbox2.text():
                    QMessageBox.information(self, '提示', 'Need to input Cycle.', QMessageBox.Ok)
                    self.startButton.setEnabled(True)
                    return

                cycle = int(self.textbox2.text())
                try:
                    self.emit_sig.emit({'duty': duty, 'cycle': cycle, 'cmd': cmd_text, 'unit': self.unit})

                    self.thread.sinOut.connect(self.display)
                    self.thread.start()
                    time.sleep(duty)

                except Exception as e:
                    self.logE(Exception, e)
                    self.label_showresult.appendPlainText(str(Exception) + str(e))

        elif self.bg.checkedId() == -1:
            QMessageBox.information(self, '提示', 'Need to choose the testing model', QMessageBox.Ok)


    def stop(self):
        try:
            self.startButton.setEnabled(True)
            self.thread.working = False
        except:
            pass

#   --------检查是否有重复的文件，如果有的话后缀加 _0、_1以此类推
    def check_filename(self, filename):
        n = [1]

        def check_meta(file_name):
            file_name_new = file_name
            if os.path.isfile(file_name):
                file_name_new = file_name[:file_name.rfind('.')] + '_' + str(n[0]) + file_name[file_name.rfind('.'):]
                n[0] += 1
            if os.path.isfile(file_name_new):
                file_name_new = check_meta(file_name)
            return file_name_new
        return_name = check_meta(filename)
        return return_name

# -----------存入csv文档
    def logV(self, *args):

        v = ' '.join([str(s) for s in args])
        with open(self.csvfilename, 'a') as fa:
            fa.write('\n\'')
            fa.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
            fa.write(',')
            fa.write(v)

# -----------存入log文档
    def logE(self, *args):

        v = ' '.join([str(s) for s in args])
        with open(self.logfilename, 'a') as fa:
            fa.write(time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time())))
            fa.write('[error] ')
            fa.write(v)
            fa.write('\n')

# -----------无尽单选按钮绑定事件
    def rdb1Click(self):
        if not self.rdbutton1.isChecked():
            self.textbox2.setEnabled(True)
            self.textbox2.setText('')
        else:
            self.textbox2.setText('No input')
            self.textbox2.setStyleSheet('color:grey')
            self.textbox2.setEnabled(False)

# -----------模式单选按钮绑定事件————设定单位
    def bgClick(self):
        if self.bg.checkedId() == 2:
            self.unit = 'V'
        elif self.bg.checkedId() == 3:
            self.unit = 'A'
        elif self.bg.checkedId() == 4:
            self.unit = 'Ω'


if __name__ == '__main__':

    # UI() # 实例化
    ui = UI() # 一定要实例化，不然界面出不来
