from PyQt5.QtWidgets import QPushButton, QToolButton, QLabel, QLineEdit, QComboBox, QProgressBar, QScrollArea
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class MainWindowUI(object):
    def initUI(self, mainWindow):
        mainWindow.setObjectName("MainWindow")
        mainWindow.setWindowTitle("GUI Automation Tool")
        centralWidget = QWidget()
        mainWindow.setCentralWidget(centralWidget)

        self.defaultFontBold = QFont("Time New Roman", 10)
        self.defaultFontBold.setBold(True)
        self.defaultFontRegular = QFont("Time New Roman", 10)
        self.defaultFontRegular.setBold(False)

        self.mainLayout = QVBoxLayout()

        self.initConnectionGroup()
        self.initPropertiesGroup()
        self.initProcessingGroup()

        centralWidget.setLayout(self.mainLayout)

    def initConnectionGroup(self):
        grConnection = QGroupBox()
        grConnection.setTitle("CONNECTION")
        grConnection.setFont(self.defaultFontBold)

        mainLayout = QVBoxLayout(grConnection)
        componentLayout = QGridLayout()

        lbIP = QLabel("HOST", grConnection)
        lbIP.setFont(self.defaultFontRegular)
        lbIP.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.txtHOST = QLineEdit("10.148.98.226", grConnection)
        self.txtHOST.setAlignment(Qt.AlignmentFlag.AlignLeft)

        lbPort = QLabel("Port", grConnection)
        lbPort.setFont(self.defaultFontRegular)
        lbPort.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.txtPort = QLineEdit("9999", grConnection)
        self.txtPort.setAlignment(Qt.AlignmentFlag.AlignLeft)

        componentLayout.addWidget(lbIP, 0, 0, Qt.AlignmentFlag.AlignVCenter)
        componentLayout.addWidget(self.txtHOST, 0, 1)
        componentLayout.addWidget(lbPort, 1, 0, Qt.AlignmentFlag.AlignVCenter)
        componentLayout.addWidget(self.txtPort, 1, 1)

        self.btnConDis = QPushButton("Connect to server", grConnection)
        self.btnConDis.setFont(self.defaultFontBold)

        mainLayout.addLayout(componentLayout)
        mainLayout.addSpacing(5)
        mainLayout.addWidget(self.btnConDis, alignment=Qt.AlignmentFlag.AlignHCenter)

        grConnection.setLayout(mainLayout)
        self.mainLayout.addWidget(grConnection)

    def initPropertiesGroup(self):
        grProperties = QGroupBox()
        grProperties.setTitle("PROPERTIES")
        grProperties.setFont(self.defaultFontBold)

        mainLayout = QVBoxLayout(grProperties)
        componentLayout = QGridLayout()
#-------------------------------Ticket id-----------------------------------------
        lbTicket = QLabel("Ticket:", grProperties)
        lbTicket.setFont(self.defaultFontRegular)
        lbTicket.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.txtTicket = QLineEdit("", grProperties)
        self.txtTicket.setAlignment(Qt.AlignmentFlag.AlignLeft)
#-----------------------------Build Versions--------------------------------------
        lbBuildVersions = QLabel("Build Versions:", grProperties)
        lbBuildVersions.setFont(self.defaultFontRegular)
        lbBuildVersions.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.cBoxBuildVersions = QComboBox(grProperties)
        self.cBoxBuildVersions.setFont(self.defaultFontRegular)

        self.btnAddBuildVersion = QPushButton("+", grProperties)
        self.btnAddBuildVersion.setFixedWidth(50)
        self.btnAddBuildVersion.setFont(self.defaultFontRegular)

        boxBuildVersionLayout = QHBoxLayout()
        boxBuildVersionLayout.addWidget(self.cBoxBuildVersions, Qt.AlignmentFlag.AlignCenter)
        boxBuildVersionLayout.addSpacing(5)
        boxBuildVersionLayout.addWidget(self.btnAddBuildVersion, Qt.AlignmentFlag.AlignCenter)
#---------------------------Test Suites--------------------------------------------
        lbTestSuites = QLabel("Test Suites:", grProperties)
        lbTestSuites.setFont(self.defaultFontRegular)
        lbTestSuites.setAlignment(Qt.AlignmentFlag.AlignLeft)

        scrollTestSuites = QScrollArea(grProperties)
        scrollTestSuites.setFont(self.defaultFontRegular)
        scrollTestSuites.setWidgetResizable(True)
        containerTestSuites = QWidget()
        self.layoutTestSuites = QVBoxLayout(containerTestSuites)
        self.layoutTestSuites.setSpacing(5)
        self.layoutTestSuites.setContentsMargins(5, 5, 5, 5)
        scrollTestSuites.setWidget(containerTestSuites)
#-----------------------------Schedule---------------------------------------------
        lbSchedule = QLabel("Schedule:", grProperties)
        lbSchedule.setFont(self.defaultFontRegular)
        lbSchedule.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.txtTime = QLineEdit("hh:mm:ss", grProperties)
        self.txtTime.setReadOnly(True)
        self.txtTime.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.txtDate = QLineEdit("dd/mm/yyyy", grProperties)
        self.txtDate.setReadOnly(True)
        self.txtDate.setAlignment(Qt.AlignmentFlag.AlignCenter)

        scheduleLayout = QHBoxLayout()
        scheduleLayout.addWidget(self.txtTime, Qt.AlignmentFlag.AlignCenter)
        scheduleLayout.addSpacing(5)
        scheduleLayout.addWidget(self.txtDate, Qt.AlignmentFlag.AlignCenter)
#-----------------------------Reports----------------------------------------------
        lbReport = QLabel("Report to:", grProperties)
        lbReport.setFont(self.defaultFontRegular)
        lbReport.setAlignment(Qt.AlignmentFlag.AlignLeft)

        scrollReports = QScrollArea(grProperties)
        scrollReports.setFont(self.defaultFontRegular)
        scrollReports.setWidgetResizable(True)
        containerReports = QWidget()
        self.layoutReports = QVBoxLayout(containerReports)
        self.layoutReports.setSpacing(5)
        self.layoutReports.setContentsMargins(5, 5, 5, 5)
        scrollReports.setWidget(containerReports)
#----------------------------------------------------------------------------------
        componentLayout.addWidget(lbTicket, 0, 0, Qt.AlignmentFlag.AlignVCenter)
        componentLayout.addWidget(self.txtTicket, 0, 1)
        componentLayout.addWidget(lbBuildVersions, 1, 0, Qt.AlignmentFlag.AlignVCenter)
        componentLayout.addLayout(boxBuildVersionLayout, 1, 1)
        componentLayout.addWidget(lbTestSuites, 2, 0)
        componentLayout.addWidget(scrollTestSuites, 2, 1)
        componentLayout.addWidget(lbSchedule, 3, 0, Qt.AlignmentFlag.AlignVCenter)
        componentLayout.addLayout(scheduleLayout, 3, 1)
        componentLayout.addWidget(lbReport, 4, 0)
        componentLayout.addWidget(scrollReports, 4, 1)

        mainLayout.addLayout(componentLayout)

        grProperties.setLayout(mainLayout)
        self.mainLayout.addWidget(grProperties)
    
    def initProcessingGroup(self):
        grProcessing = QGroupBox()
        grProcessing.setTitle("PROCESSING")
        grProcessing.setFont(self.defaultFontBold)

        mainLayout = QVBoxLayout(grProcessing)
        componentLayout = QHBoxLayout()
        leftLayout = QHBoxLayout()
        rightLayout = QHBoxLayout()

        lbProgress = QLabel("Progress:", grProcessing)
        lbProgress.setFont(self.defaultFontRegular)
        lbProgress.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)

        self.btnCancel = QPushButton("Cancel", grProcessing)
        self.btnCancel.setFont(self.defaultFontRegular)
        self.btnOK = QPushButton("OK", grProcessing)
        self.btnOK.setFont(self.defaultFontRegular)

        leftLayout.addWidget(lbProgress, Qt.AlignmentFlag.AlignVCenter)
        leftLayout.addWidget(self.progress, Qt.AlignmentFlag.AlignVCenter)

        rightLayout.addWidget(self.btnCancel, Qt.AlignmentFlag.AlignCenter)
        rightLayout.addWidget(self.btnOK, Qt.AlignmentFlag.AlignCenter)

        componentLayout.addLayout(leftLayout)
        componentLayout.addSpacing(10)
        componentLayout.addLayout(rightLayout)
        mainLayout.addLayout(componentLayout)

        grProcessing.setLayout(mainLayout)
        self.mainLayout.addWidget(grProcessing)