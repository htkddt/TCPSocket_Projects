import os
import sys
import socket
import json

from PyQt5.QtCore import QThread, QDate, QTime, Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QMainWindow, QApplication, QCheckBox, QPushButton, QToolButton, 
                             QDialog, QCalendarWidget, QMenu, QSizePolicy, QVBoxLayout, QHBoxLayout, 
                             QDial, QLabel, QMessageBox, QFileDialog)

from datetime import datetime, timedelta, timezone
from applicationUI import MainWindowUI

EMAILS = ["sangx.phan@intel.com", "thex.do@intel.com", "tuanx.nguyen@intel.com", 
          "maix.tan@intel.com", "taix.them@intel.com", "thinhx.le@intel.com", "kiet.huynh@terralogic.com"]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.uic = MainWindowUI()
        self.uic.initUI(self)

        for mail in EMAILS:
            checkbox = QCheckBox(mail)
            self.uic.layoutReports.addWidget(checkbox)
        self.uic.layoutReports.addStretch()

        self.socket = TCPSocketConnection()
        self.socket.connectFinished.connect(self.initData)
        self.socket.responseFinished.connect(self.serverResponseAct)

        self.uic.btnConDis.clicked.connect(self.establishConnectAct)
        self.uic.btnAddBuildVersion.clicked.connect(self.addBuildAct)
        self.uic.btnOK.clicked.connect(self.runAct)
        self.uic.btnCancel.clicked.connect(self.clearSelection)
        self.uic.txtDate.mousePressEvent = lambda event: self.showDateDialog()
        self.uic.txtTime.mousePressEvent = lambda event: self.showTimeDialog()

    def establishConnectAct(self):
        if self.uic.btnConDis.text() == "Connect to server":
            self.uic.btnConDis.setText("Disconnect to server")

            HOST = self.uic.txtHOST.text()
            Port = int(self.uic.txtPort.text())

            self.socket.serverAddress(HOST, Port)
            self.socket.start()

        elif self.uic.btnConDis.text() == "Disconnect to server":
            self.uic.btnConDis.setText("Connect to server")
            sendData = {
                "argv":"server",
                "value":"stop"
            }
            self.socket.clientRequest(sendData)
            self.uic.txtTicket.clear()
            if (self.uic.cBoxBuildVersions.count() > 0): self.uic.cBoxBuildVersions.clear()
            for i in reversed(range(self.uic.layoutTestSuites.count())):
                checkbox = self.uic.layoutTestSuites.itemAt(i).widget()
                if isinstance(checkbox, QCheckBox):
                    self.uic.layoutTestSuites.removeWidget(checkbox)
                    checkbox.setParent(None)
                    checkbox.deleteLater()
            self.uic.txtTime.setText("hh:mm:ss")
            self.uic.txtDate.setText("dd/mm/yyyy")
            self.clearCheckedItems(self.uic.layoutReports)

    def close(self):
        if self.connected:
            sendData = {
                "argv":"server",
                "value":"stop"
            }
            self.socket.clientRequest(sendData)
            while True:
                if not self.connected: break

    def initData(self, connected):
        if not connected: return
        sendData = {
            "argv":"server",
            "value":"init"
        }
        self.socket.clientRequest(sendData)
        self.connected = True

    def addBuildAct(self):
        filePath, _ = QFileDialog.getOpenFileName(
            self,
            "Open file",
            "",
            "Executable Files (*.exe);;All Files (*)"
        )

        if filePath:
            fileName = filePath.split("/")[-1].split(".")[0]
            fileSize = os.path.getsize(filePath)
            sendData = {
                "argv":"header",
                "value":[fileName, str(fileSize)]
            }
            # print(f"filePath: {filePath}")
            # print(f"fileName: {fileName}")
            # print(f"fileSize: {str(fileSize)}")
            self.socket.clientRequest(sendData)
            with open(filePath, 'rb') as f:
                while True:
                    bin = f.read(4096)
                    if not bin:
                        break
                    self.socket.clientRequest(bin, True)

    def serverResponseAct(self, recvData):
        if (len(recvData) == 2):
            if recvData["argv"] == "client":
                if recvData["value"] == "disconnected":
                    self.socket.stop()
                    self.connected = False
                elif recvData["value"] == "finished":
                    self.uic.btnOK.setEnabled(True)
                    self.uic.btnCancel.setEnabled(True)
                    self.uic.btnConDis.setEnabled(True)
                else:
                    buildVersions = recvData["value"]["build-version"]
                    for build in buildVersions:
                        self.uic.cBoxBuildVersions.addItem(build)
                    testSuites = recvData["value"]["test-suites"]
                    for test in testSuites:
                        checkbox = QCheckBox(test)
                        self.uic.layoutTestSuites.addWidget(checkbox)
                    self.uic.layoutTestSuites.addStretch()
            elif recvData["argv"] == "updated":
                buildUpdated = recvData["value"]
                for build in buildUpdated:
                    self.uic.cBoxBuildVersions.addItem(build)
            elif recvData["argv"] == "status":
                if recvData["value"] == "successful":
                    if (self.uic.cBoxBuildVersions.count() > 0): self.uic.cBoxBuildVersions.clear()
                    sendData = {
                        "argv":"header",
                        "value":"update"
                    }
                    self.socket.clientRequest(sendData)
                elif recvData["value"] == "running":
                    self.uic.btnOK.setEnabled(False)
                    self.uic.btnCancel.setEnabled(False)
                    self.uic.btnConDis.setEnabled(False)
                elif recvData["value"] == "finished":
                    QMessageBox.information(
                        self,
                        "Information",
                        f"The scheduled task {self.uic.txtTicket.text()} has successfully been created.\nDate: {self.uic.txtDate.text()}\nTime: {self.uic.txtTime.text()}",
                        QMessageBox.StandardButton.Ok
                    )
                    self.uic.btnOK.setEnabled(True)
                    self.uic.btnCancel.setEnabled(True)
                    self.uic.btnConDis.setEnabled(True)

    def runAct(self):
        ticket = self.uic.txtTicket.text()
        test = self.getCheckedItems(self.uic.layoutTestSuites)
        time = self.uic.txtTime.text()
        date = self.uic.txtDate.text()
        reports = self.getCheckedItems(self.uic.layoutReports)
        if (ticket == "") or (len(test) == 0) or (len(reports) == 0) or (time == "hh:mm:ss") or (date == "dd/mm/yyyy"): return

        time = time.split(":")
        hour = int(time[0])
        minute = int(time[1])
        second = int(time[2])

        date = date.split("/")
        day = int(date[0])
        month = int(date[1])
        year = int(date[2])

        localTime = datetime(year, month, day, hour, minute, second)

        localTimeZone = timezone(timedelta(hours=7))   # Local GMT+7
        serverTimeZone = timezone(timedelta(hours=-7)) # Server GMT-7

        localTime = localTime.replace(tzinfo=localTimeZone)
        serverTime = localTime.astimezone(serverTimeZone)

        timeValue = serverTime.strftime("%H:%M:%S")
        dateValue = serverTime.strftime("%m/%d/%Y")

        schedule = [timeValue, dateValue]

        sendData = {
            "ticket-id":ticket,
            "build-version-name":self.uic.cBoxBuildVersions.currentText(),
            "test-suites":test,
            "schedule":schedule,
            "reports":reports
        }
        self.socket.clientRequest(sendData)
    
    def getCheckedItems(self, obj):
        checked = []
        for i in range(obj.count() - 1):
            checkbox = obj.itemAt(i).widget()
            if isinstance(checkbox, QCheckBox):
                if checkbox.isChecked():
                    checked.append(checkbox.text())
        return checked

    def clearCheckedItems(self, obj):
        for i in range(obj.count() - 1):
            checkbox = obj.itemAt(i).widget()
            if isinstance(checkbox, QCheckBox):
                if checkbox.isChecked(): 
                    checkbox.setChecked(False)

    def clearSelection(self):
        self.uic.txtTicket.clear()
        self.clearCheckedItems(self.uic.layoutTestSuites)
        self.clearCheckedItems(self.uic.layoutReports)
##----------------------------------------------------------------------------------------------------------
##-------------------------Modify layout of month and year tool button--------------------------------------
##----------------------------------------------------------------------------------------------------------
    def showDateDialog(self):
        dlg = DateDialog()  # Create default calendar and set that layout on dialog
        btnMonth = dlg.calendar.findChild(QToolButton, "qt_calendar_monthbutton")
        btnYear = dlg.calendar.findChild(QToolButton, "qt_calendar_yearbutton")
        if btnMonth:
            btnMonth.setMinimumWidth(300)
            btnMonth.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        if btnYear:
            btnYear.setMinimumWidth(300)
            btnYear.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btnYear.setPopupMode(QToolButton.InstantPopup)
            menu = QMenu()
            menu.setStyleSheet("""
                QMenu {
                    background-color: #ffffff;
                    border: 1px solid #ccc;
                    font-size: 14px;
                }
                QMenu::item {
                    padding: 5px 10px;
                }
                QMenu::item:selected {
                    background-color: #2d8cf0;
                    color: white;
                }
            """)

        currentYear = QDate.currentDate().year()
        for y in range(currentYear - 5, currentYear + 6):
            action = menu.addAction(str(y))
            action.triggered.connect(
                lambda checked, year=y: 
                    dlg.calendar.setSelectedDate(
                        QDate(year, dlg.calendar.selectedDate().month(), dlg.calendar.selectedDate().day())
                    )
                )
        btnYear.setMenu(menu)
        dlg.setFixedSize(620, 300)
        dlg.dateSelected.connect(self.onDateSelected)
        dlg.exec_()
##----------------------------------------------------------------------------------------------------------
##----------------------------------------------------------------------------------------------------------
##----------------------------------------------------------------------------------------------------------
    def showTimeDialog(self):
        dlg = TimeDialog()
        dlg.timeSelected.connect(self.onTimeSelected)
        dlg.exec_()

    def onDateSelected(self, date):
        self.uic.txtDate.setText(date.toString("dd/MM/yyyy"))

    def onTimeSelected(self, time):
        self.uic.txtTime.setText(time.toString("HH:mm:ss"))


class TCPSocketConnection(QThread):
    connectFinished = pyqtSignal(bool)
    responseFinished = pyqtSignal(dict)
    def __init__(self):
        super(TCPSocketConnection, self).__init__()
        self.HOST = ''
        self.Port = 0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # print("TCPSocket thread Finished Init")

    def run(self):
        try:
            self.socket.connect((self.HOST, self.Port))
            # print("Connection is established...")
            # print("------------------------------------------")
            self.connected = True
            self.receiver = TCPSocketReceiver(self.socket)
            self.receiver.start()
            self.receiver.response.connect(self.serverResponse)
        except Exception as e:
            self.connected = False
            print("Error:", e)
        self.connectFinished.emit(self.connected)

    def stop(self):
        if self.receiver:
            self.receiver.stop()

        if self.socket:
            self.socket.close()
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        # print("Disconnected")

    def serverAddress(self, HOST, Port):
        self.HOST = HOST
        self.Port = Port

    def clientRequest(self, sendData, addBuild=False):
        if addBuild:
            self.socket.sendall(sendData)
        else:
            sendJSON = json.dumps(sendData)
            self.socket.sendall((sendJSON + "\n").encode())

    def serverResponse(self, recvJSON):
        recvData = json.loads(recvJSON.strip())
        self.responseFinished.emit(recvData)


class TCPSocketReceiver(QThread):
    response = pyqtSignal(str)
    def __init__(self, socket):
        super(TCPSocketReceiver, self).__init__()
        self.socket = socket
        self.running = True

    def run(self):
        while self.running:
            try:
                recvJSON = ""
                while not recvJSON.endswith("\n"):
                    recvJSON += self.socket.recv(1).decode()
                if recvJSON:
                    self.response.emit(recvJSON)
                else:
                    break
            except Exception as e:
                pass
                break
    
    def stop(self):
        self.running = False
        if self.socket:
            self.socket.shutdown(socket.SHUT_RDWR)
        # print("TCPSocketReceiver is close")


class TimeDialog(QDialog):
    timeSelected = pyqtSignal(QTime)
    def __init__(self):
        super().__init__()
        font = QFont("Time New Roman", 13)
        font.setBold(True)

        self.hourLabel = QLabel()
        self.hourLabel.setFont(font)
        self.hourLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.minuteLabel = QLabel()
        self.minuteLabel.setFont(font)
        self.minuteLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.secondLabel = QLabel()
        self.secondLabel.setFont(font)
        self.secondLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.hourDial = QDial()
        self.hourDial.setRange(0, 23)
        self.hourDial.setNotchesVisible(True)
        self.hourDial.setWrapping(True)

        self.minuteDial = QDial()
        self.minuteDial.setRange(0, 59)
        self.minuteDial.setNotchesVisible(True)
        self.minuteDial.setWrapping(True)

        self.secondDial = QDial()
        self.secondDial.setRange(0, 59)
        self.secondDial.setNotchesVisible(True)
        self.secondDial.setWrapping(True)

        btnOK = QPushButton("OK")
        btnOK.setFont(font)
        btnOK.clicked.connect(self.emitTime)
        btnCancel = QPushButton("Cancel")
        btnCancel.setFont(font)
        btnCancel.clicked.connect(self.reject)

        dialLayout = QHBoxLayout()
        dialLayout.addWidget(self.hourDial)
        dialLayout.addWidget(self.minuteDial)
        dialLayout.addWidget(self.secondDial)

        labelLayout = QHBoxLayout()
        labelLayout.addWidget(self.hourLabel, Qt.AlignmentFlag.AlignCenter)
        labelLayout.addWidget(self.minuteLabel, Qt.AlignmentFlag.AlignCenter)
        labelLayout.addWidget(self.secondLabel, Qt.AlignmentFlag.AlignCenter)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(btnCancel)
        buttonLayout.addWidget(btnOK)

        layout = QVBoxLayout()
        layout.addLayout(dialLayout)
        layout.addSpacing(5)
        layout.addLayout(labelLayout)
        layout.addSpacing(5)
        layout.addLayout(buttonLayout)
        self.setLayout(layout)

        now = QTime.currentTime()
        self.hourDial.setValue(now.hour())
        self.minuteDial.setValue(now.minute())
        self.secondDial.setValue(now.second())
        self.updateLabel()

        self.hourDial.valueChanged.connect(self.updateLabel)
        self.minuteDial.valueChanged.connect(self.updateLabel)
        self.secondDial.valueChanged.connect(self.updateLabel)

    def updateLabel(self):
        h = self.hourDial.value()
        m = self.minuteDial.value()
        s = self.secondDial.value()
        self.hourLabel.setText(f"{h:02d}")
        self.minuteLabel.setText(f"{m:02d}")
        self.secondLabel.setText(f"{s:02d}")
        self.timeEdit = QTime(h, m, s)
    
    def emitTime(self):
        self.timeSelected.emit(self.timeEdit)
        self.accept()


class DateDialog(QDialog):
    dateSelected = pyqtSignal(QDate)
    def __init__(self):
        super().__init__()
        font = QFont("Time New Roman", 13)
        font.setBold(True)

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setSelectedDate(QDate.currentDate())
        self.calendar.setStyleSheet("""
            QCalendarWidget QAbstractItemView {
                font-size: 16px;
            }

            QCalendarWidget QToolButton {
                background-color: #ffffff;
                color: #000000;
                font-size: 16px;
                icon-size: 24px;
            }

            QCalendarWidget QMenu {
                background-color: #ffffff;
                border: 1px solid #ccc;
                font-size: 14px;
            }

            QCalendarWidget QMenu::item {
                padding: 5px 10px;
            }

            QCalendarWidget QMenu::item:selected {
                background-color: #2d8cf0;
                color: white;
            }
        """)

        btnPrev = self.calendar.findChild(QToolButton, "qt_calendar_prevmonth")
        btnNext = self.calendar.findChild(QToolButton, "qt_calendar_nextmonth")
        if btnPrev: btnPrev.hide()
        if btnNext: btnNext.hide()

        btnOK = QPushButton("OK")
        btnOK.setFont(font)
        btnOK.clicked.connect(self.emitDate)
        btnCancel = QPushButton("Cancel")
        btnCancel.setFont(font)
        btnCancel.clicked.connect(self.reject)

        layoutButton = QHBoxLayout()
        layoutButton.addWidget(btnCancel)
        layoutButton.addWidget(btnOK)

        layout = QVBoxLayout()
        layout.addWidget(self.calendar)
        layout.addSpacing(5)
        layout.addLayout(layoutButton)
        self.setLayout(layout)

    def emitDate(self):
        selectetDate = self.calendar.selectedDate()
        self.dateSelected.emit(selectetDate)
        self.accept()

if __name__ == "__main__":
    # os.system('pyinstaller --onefile --noconsole --name TCPAutomation --icon=nsicon.ico --distpath=. ./App/applicationCore.py')
    # try:
    #     import PyInstaller.__main__
    # except ImportError:
    #     import subprocess
    #     subprocess.check_call(['pip', 'install', 'pyinstaller'])
    #     import PyInstaller.__main__

    # PyInstaller.__main__.run([
    #     '--onefile',
    #     '--noconsole',
    #     '--name=TCPAutomation',
    #     '--icon=nsicon.ico',
    #     '--distpath=.',
    #     './App/applicationCore.py'
    # ])
    # if os.path.exists("build"):
    #     shutil.rmtree("build")

    app = QApplication(sys.argv)
    window = MainWindow()
    window.setMinimumSize(400, 600)
    window.show()
    sys.exit(app.exec())