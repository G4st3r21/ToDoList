import sys
import sqlite3
from PyQt5 import uic, QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QCheckBox, \
    QLabel, QInputDialog, QDialog, QFontComboBox, QPushButton, \
    QStackedWidget, QGridLayout, QFileDialog
from PyQt5.QtCore import Qt
from datetime import datetime as dt
from pyqtgraph import PlotWidget
from random import choice
from os import replace

WeekDays = {1: ['Понедельник', 'Monday'], 2: ['Вторник', 'Tuesday'],
            3: ['Среда', 'Wensday'], 4: ['Четверг', 'Thursday'],
            5: ['Пятница', 'Friday'], 6: ['Суббота', 'Saturday'],
            7: ['Воскресенье', 'Sunday']}
Monthes = {1: ['Январь', 'January'], 2: ['Февраль', 'February'],
           3: ['Март', 'March'], 4: ['Апрель', 'April'],
           5: ['Май', 'May'], 6: ['Июнь', 'June'],
           7: ['Июль', 'July'], 8: ['Август', 'August'],
           9: ['Сентябрь', 'September'], 10: ['Октябрь', 'October'],
           11: ['Ноябрь', 'November'], 12: ['Декабрь', 'December']}


class ToDoList(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('uiFiles\\ToDoQT.ui', self)
        self.tabWidget.setTabText(0, 'На сегодня')
        self.tabWidget.setTabText(1, 'Все')

        self.WeekDays = WeekDays
        self.Monthes = Monthes

        self.setWindowTitle('ToDoList!')

        self.Numb_of_ReloadInfo = 0

        self.DataBaseOn()
        self.TasksForToday()
        self.DoneTaskCount()
        self.Header()
        self.DoNewTask.clicked.connect(self.NewTask)
        self.StartGridLayout()
        self.ShowTasks()
        self.AddStat()
        self.GraphView()
        self.QuoteTab()
        self.show()
        self.HundreedPercent()

        self.Numb_of_ReloadInfo = 1
        self.toggle = 0

    def DataBaseOn(self):
        DBname = 'DBfile\\ToDoDB.db'
        self.con = sqlite3.connect(DBname)
        self.cur = self.con.cursor()
        self.AllTasks = list(self.cur.execute(
            'SELECT * FROM Tasks').fetchall())

    def TasksForToday(self):
        today = str(dt.today())[:10].split('-')
        self.today = '.'.join(reversed(today))
        if self.today[0] == '0':
            self.today = self.today[1:]
        self.TodayTasks = [i for i in self.AllTasks if i[2] == self.today]
        self.TodayTasks.sort(key=lambda x: x[3])
        self.AllTasks.sort(key=lambda x: x[3])
        self.AllTasks.sort(key=lambda x: x[2])
        self.CountOfTasks = len(self.AllTasks)
        self.CountOfTasksForToday = len(self.TodayTasks)

    def Header(self):
        TD = dt.today()
        WD = dt.today().weekday()
        today = str(TD)[8:10]
        if today[0] == '0':
            today = today[1]

        self.WeekDay.setText(f'{self.WeekDays[WD + 1][0]}, {today}')
        self.Month.setText(self.Monthes[int(str(TD)[5:7])][0])

        self.TaskCnt.setText(f'Задач на сегодня: {self.CountOfTasksForToday}')
        self.TaskCnt2.setText(f'Задач всего: {self.CountOfTasks}')

        if self.CountOfTasksForToday:
            self.Percentnum = int(
                self.DoneTasks / self.CountOfTasksForToday * 100)
            self.Percent.setText(f'Выполнено: {self.Percentnum}%')
        else:
            self.Percent.setText('Выполнено: 0%')

    def StartGridLayout(self):
        self.gridLayoutWidget = QtWidgets.QWidget(self.Today)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(9, -1, 511, 661))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")

        self.gridLayoutWidget2 = QtWidgets.QWidget(self.All)
        self.gridLayoutWidget2.setGeometry(QtCore.QRect(9, -1, 511, 661))
        self.gridLayoutWidget2.setObjectName("gridLayoutWidget2")
        self.gridLayout2 = QtWidgets.QGridLayout(self.gridLayoutWidget2)
        self.gridLayout2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout2.setObjectName("gridLayout2")

    def ShowTasks(self):
        positions = [[(i, j) for j in range(4)]
                     for i in range(len(self.TodayTasks))]

        for (num, i) in enumerate(positions):
            task = self.TodayTasks[num]
            for pos in i:
                if pos[1] == 0:
                    CheckBox = QCheckBox(str(task[1]), self)
                    CheckBox.stateChanged.connect(self.CheckTaskOnline)
                    self.gridLayout.addWidget(CheckBox, *pos)
                elif pos[1] == 1:
                    DateLabel = QLabel(str(task[2]))
                    self.gridLayout.addWidget(DateLabel, *pos)
                elif pos[1] == 2:
                    TimeLabel = QLabel(str(task[3]))
                    self.gridLayout.addWidget(TimeLabel, *pos)
                elif pos[1] == 3:
                    PushButton = QPushButton(f'Изменить ({str(task[0])})')
                    PushButton.clicked.connect(self.ChangeTaskSetting)
                    self.gridLayout.addWidget(PushButton, *pos)

            self.CheckTask(CheckBox, DateLabel, TimeLabel, task)
        if not positions:
            templabel = QLabel('На сегодня у вас задач нет.\n\
            Добавьте, нажав на кнопку "Добавить задачу",\n\
                или, если имеется файл "bd", загрузите его.')
            templabel.font().setPointSize(12)
            self.gridLayout.addWidget(templabel)
            tempButton = QPushButton('Загрузить db')
            tempButton.clicked.connect(self.DownloadDB)
            self.gridLayout.addWidget(tempButton)

        positions = [[(i, j) for j in range(4)]
                     for i in range(len(self.AllTasks))]

        for (num, i) in enumerate(positions):
            task = self.AllTasks[num]
            for pos in i:
                if pos[1] == 0:
                    NameLabel = QLabel(str(task[1]), self)
                    self.gridLayout2.addWidget(NameLabel, *pos)
                elif pos[1] == 1:
                    DateLabel = QLabel(str(task[2]))
                    self.gridLayout2.addWidget(DateLabel, *pos)
                elif pos[1] == 2:
                    TimeLabel = QLabel(str(task[3]))
                    self.gridLayout2.addWidget(TimeLabel, *pos)
                elif pos[1] == 3:
                    PushButton = QPushButton(f'Изменить ({str(task[0])})')
                    PushButton.clicked.connect(self.ChangeTaskSetting)
                    self.gridLayout2.addWidget(PushButton, *pos)

        if not positions:
            templabel = QLabel('Задач все еще нет.\n\
            Добавьте, нажав на кнопку "Добавить задачу"')
            templabel.font().setPointSize(12)
            self.gridLayout2.addWidget(templabel)

    def DownloadDB(self):
        fname = QFileDialog.getOpenFileName(
            self, 'Выбрать DB файл', '', '*.db')[0]
        replace(fname, 'DBfile/ToDoDB.db')
        self.ReloadInfo()

    def CheckTask(self, CheckBox, Date, Time, task):
        fC = CheckBox.font()
        fC.setPointSize(12)

        fD = Date.font()
        fD.setPointSize(12)

        fT = Time.font()
        fT.setPointSize(12)

        if task[-1]:
            CheckBox.setChecked(1)
            fC.setPointSize(8)
            fD.setPointSize(8)
            fT.setPointSize(8)
        else:
            fD.setPointSize(12)
            fD.setPointSize(12)
            fT.setPointSize(12)

        CheckBox.setFont(fC)
        Date.setFont(fD)
        Time.setFont(fT)

    def CheckTaskOnline(self):
        CheckBox = self.sender()
        taskName = CheckBox.text()
        if CheckBox.isChecked():
            self.cur.execute(f"UPDATE Tasks SET Done = '1' \
                WHERE TaskName LIKE '{taskName}'")
        else:
            self.cur.execute(f"UPDATE Tasks SET Done = '0' \
                WHERE TaskName LIKE '{taskName}'")
        self.con.commit()
        if self.Numb_of_ReloadInfo:
            self.Numb_of_ReloadInfo = 0
            self.ReloadInfo()

    def ChangeTaskSetting(self):
        global ex3
        task = self.sender().text()
        ex3 = SettingOfTask(task)
        ex3.show()

    def NewTask(self, checked):
        ex2.show()

    def HundreedPercent(self):
        global ex4
        ex4 = GoodJob()
        if self.CountOfTasksForToday == 0:
            pass
        elif int(self.DoneTasks / self.CountOfTasksForToday * 100) == 100:
            ex4.show()

    def DoneTaskCount(self):
        self.DoneTasks = 0
        self.NotDoneTasks = 0
        for task in self.TodayTasks:
            if task[4]:
                self.DoneTasks += 1
            else:
                self.NotDoneTasks += 1

    def AddStat(self):
        if self.CountOfTasksForToday:
            percent = int(self.DoneTasks / self.CountOfTasksForToday * 100)
        else:
            percent = 0

        today_stat = self.cur.execute(f"SELECT * FROM Statistics \
            WHERE Date = '{self.today}'").fetchall()
        if not today_stat:
            self.cur.execute(f"INSERT INTO Statistics(Date, Percent) \
                        VALUES('{self.today}', '{percent}')")
        else:
            self.cur.execute(f"UPDATE Statistics \
                        SET Percent = '{percent}' \
                        WHERE Date = '{self.today}'")
        self.con.commit()

    def GraphView(self):
        statinfo = list(self.cur.execute(
            'SELECT * FROM Statistics').fetchall())[-1:-8:-1]
        Percents = [int(i[-1]) for i in statinfo]
        Avg = sum(Percents) // len(Percents)

        self.Statistics = QtWidgets.QWidget()
        self.Statistics.setObjectName("Statistics")
        self.StatGraph = PlotWidget(self.Statistics)
        self.StatGraph.setGeometry(QtCore.QRect(5, 40, 531, 251))
        self.StatGraph.setObjectName("StatGraph")
        self.label = QtWidgets.QLabel(self.Statistics)
        self.label.setGeometry(QtCore.QRect(4, 0, 531, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.Statistics)
        self.label_2.setGeometry(QtCore.QRect(4, 295, 531, 81))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.tabWidget.addTab(self.Statistics, "Статистика")
        self.label.setText("Статистика выполнения заданий")
        self.label_2.setText("По оси X: число сегодняшнего месяца\n"
                             "По оси Y: процент выполненных задач\n"
                             "Синяя прямая: среднее значение")

        if len(statinfo) >= 7:
            self.StatGraph.plot([int(i) for i in range(1, 8)],
                                [int(j[2]) for j in statinfo[::-1]], pen='g')
            self.StatGraph.plot([int(i) for i in range(1, 8)],
                                [Avg for j in range(7)], pen='b')
        else:
            self.label_2.setText(f"Чтобы статистика выводилась должно пройти 7\
                 \nдней после первого запуска\n\
                     Осталось: {8 - len(statinfo)}")

    def QuoteTab(self):
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("Quote")
        self.label_3 = QtWidgets.QLabel(self.tab)
        self.label_3.setGeometry(QtCore.QRect(4, 5, 351, 51))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.quote = QtWidgets.QLabel(self.tab)
        self.quote.setGeometry(QtCore.QRect(4, 65, 531, 201))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.quote.setFont(font)
        self.quote.setObjectName("quote")
        self.secretCB = QtWidgets.QCheckBox(self.tab)
        self.secretCB.setGeometry(QtCore.QRect(0, 610, 251, 51))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.secretCB.setFont(font)
        self.secretCB.setObjectName("secretCB")
        self.secretCB.clicked.connect(self.Squote)
        self.Author = QtWidgets.QLabel(self.tab)
        self.Author.setGeometry(QtCore.QRect(360, 270, 161, 41))
        self.Author.setObjectName("Author")
        self.Author.setFont(font)
        self.tabWidget.addTab(self.tab, "Цитата")
        self.label_3.setText("Мотивирующая цитата:")

        with open('Motivation.txt', mode='r', encoding='utf-8') as f:
            quotes = f.readlines()
        quote = choice(quotes[:19])
        qlist = [i for i in quote.split('.')]
        self.author = qlist[-1]
        quote = str('\n'.join(qlist[1:-1]))

        self.quotestr = ''.join(quote)

        squote = choice(quotes[19:])
        sqlist = [i for i in squote.split('.')]
        self.sauthor = sqlist[-1]
        self.squote = str('\n'.join(sqlist[1:-1]))

        self.quote.setText(f'"{self.quotestr}"')
        self.quote.adjustSize()
        self.Author.setText(self.author)
        self.secretCB.setText("Режим Я.Лицеиста")
        self.secretCB.hide()

    def keyPressEvent(self, event):
        if int(event.modifiers()) == Qt.ShiftModifier:
            if event.key() == Qt.Key_Y:
                if self.toggle:
                    self.secretCB.hide()
                    self.toggle = 0
                else:
                    self.secretCB.show()
                    self.toggle = 1

    def Squote(self):
        CheckBox = self.sender()
        if CheckBox.isChecked():
            self.quote.setText(f'"{self.squote}"')
            self.Author.setText(self.sauthor)
        else:
            self.quote.setText(f'"{self.quotestr}"')
            self.Author.setText(self.author)

    def ReloadInfo(self):
        self.DataBaseOn()
        self.TasksForToday()
        self.DoneTaskCount()
        self.gridLayoutWidget.hide()
        self.gridLayoutWidget2.hide()
        self.close()
        self.StartGridLayout()
        self.ShowTasks()
        self.Header()
        self.tabWidget.removeTab(2)
        self.tabWidget.removeTab(2)
        self.AddStat()
        self.QuoteTab()
        self.GraphView()
        self.Numb_of_ReloadInfo += 1
        self.show()
        self.HundreedPercent()


class NewTaskWidget(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(
            'uiFiles\\NewtaskQT.ui', self)

        self.setWindowTitle('Добавить задачу')

        self.pb.clicked.connect(self.change)
        self.help_event_list = []

        DBname = 'DBfile\\ToDoDB.db'
        self.con = sqlite3.connect(DBname)
        self.cur = self.con.cursor()

    def change(self):
        name = str(self.Event_input.text())
        time = str(self.timeEdit.time().toString())[:5]
        date = '.'.join(
            reversed(
                [i for i in str(
                    self.calendar.selectedDate())[19:-1].split(', ')]))
        self.TaskToDatabase(name, time, date)
        ex.ReloadInfo()
        self.close()

    def TaskToDatabase(self, name, time, date):
        self.cur.execute(f"INSERT INTO Tasks(TaskName, Data, Time, Done) \
                        VALUES('{name}', '{date}', '{time}', 0)")
        self.con.commit()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter:
            self.change()
        if event.key() == Qt.Key_Escape:
            self.close()


class SettingOfTask(QWidget):
    def __init__(self, task):
        super().__init__()
        uic.loadUi(
            'uiFiles\\ChangeTask.ui', self)

        self.setWindowTitle('Изменить задачу')

        self.pb.clicked.connect(self.change)
        self.help_event_list = []

        DBname = 'DBfile\\ToDoDB.db'
        self.con = sqlite3.connect(DBname)
        self.cur = self.con.cursor()

        self.TaskID = int(task[10:-1])

        self.TaskProp = self.cur.execute(f"SELECT * FROM Tasks \
            WHERE TaskID = '{self.TaskID}'").fetchall()

        self.name = self.TaskProp[0][1]
        time = [int(i) for i in self.TaskProp[0][3].split(':')]
        date = [int(i) for i in self.TaskProp[0][2].split('.')]

        self.Event_input.setText(self.name)
        self.dateTimeEdit.setTime(QtCore.QTime(*time))
        self.dateTimeEdit.setDate(QtCore.QDate(*reversed(date)))

        self.cnt = 0
        self.Delete.clicked.connect(self.DeleteTask)
        if self.TaskProp[0][-1]:
            self.Done.toggle()
        self.Done.stateChanged.connect(self.DoneTask)

    def change(self):
        name = str(self.Event_input.text())
        date, time = (self.dateTimeEdit.text().split(' '))
        if date[0] == '0':
            date = date[1:]
        self.NewTaskInfo(name, time, date)
        ex.ReloadInfo()
        self.close()

    def NewTaskInfo(self, name, time, date):
        self.cur.execute(f"UPDATE Tasks \
        SET TaskName = '{name}', \
            Data = '{date}', \
            Time = '{time}' \
        WHERE TaskID = {self.TaskID}")
        self.con.commit()

    def DoneTask(self):
        CheckBox = self.sender()

        if CheckBox.isChecked():
            self.cur.execute(f"UPDATE Tasks SET Done = '1' \
                WHERE TaskName LIKE '{self.name}'")
        else:
            self.cur.execute(f"UPDATE Tasks SET Done = '0' \
                WHERE TaskName LIKE '{self.name}'")
        self.con.commit()

    def DeleteTask(self):
        if self.sender().text() == 'Удалить(нажать дважды)':
            self.cnt += 1
        if self.cnt == 2:
            self.cur.execute(f"DELETE FROM Tasks \
            WHERE TaskID = {self.TaskID}")
            self.Delete.setText('Сохраните изменения')
        self.con.commit()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()


class GoodJob(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('uiFiles\\Hundreed.ui', self)

        self.setWindowTitle('100%')
        self.pushButton.clicked.connect(self.run)

    def run(self):
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ToDoList()
    ex2 = NewTaskWidget()
    sys.exit(app.exec_())
