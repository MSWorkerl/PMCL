from _mclauncher import *
from mlpi import *
import sys
import os
import ctypes
import ctypes.wintypes
import configparser
import psutil
import multiprocessing
from gamebox import Ui_GroupBox as _GroupBox


class GroupBox(QtWidgets.QGroupBox):
    def __init__(self, window, version, typetext, config):
        QtWidgets.QGroupBox.__init__(self, window)
        self.box = _GroupBox()
        self.box.setupUi(self)
        self.version = version
        self._tr = QtCore.QCoreApplication.translate
        self.config = config
        self.error = False
        self.window = window
        if typetext == "JSON Not Exists":
            text = self._tr("GroupBox", "(JSON文件不存在)")
        elif typetext == "":
            self.error = True
            text = ""
        elif typetext == "JSON is NULL":
            text = self._tr("GroupBox", "(JSON文件为空)")
        else:
            text = typetext
        self.box.label.setText('<h5>{}\n</h5><font size=1 color=gray>{}<font>'.format(version, text))
        self.setLayout(self.box.horizontalLayout)

    @QtCore.pyqtSlot()
    def on_pushButton_4_clicked(self):
        if self.error:
            if self.config.get("PMCL::Java", "JavaPath"):
                if self.config.get("PMCL::Game", "UserName"):

                    api.async_launch_game(".minecraft", self.version,
                                          self.config.get("PMCL::Game", "UserName"),
                                          self.config.get("PMCL::Java", "JavaPath"),
                                          width=self.config.get("PMCL::Screen", "Width"),
                                          height=self.config.get("PMCL::Screen", "Height"),
                                          fullscreen=bool(self.config.get("PMCL::Screen", "Fullscreen")),
                                          max_memory=self.config.getint("PMCL::Java", "MemorySize"),
                                          server=self.config.get("PMCL::Server", "Server"),
                                          port=self.config.get("PMCL::Server", "Port")
                                          )
                else:
                    QtWidgets.QMessageBox.critical(self.window, "PMCL", self._tr("GroupBox", "无法启动游戏:没有登录"))
            else:
                QtWidgets.QMessageBox.critical(self.window, "PMCL", self._tr("GroupBox", "无法启动游戏:没有选择Java"))
        else:
            QtWidgets.QMessageBox.critical(self.window, "PMCL", self._tr("GroupBox", "无法启动游戏:文件缺失"))


class SplashScreen(QtWidgets.QSplashScreen):
    def __init__(self):
        QtWidgets.QSplashScreen.__init__(self)
        self.setPixmap(QtGui.QPixmap("resource/splash.png"))

    def mousePressEvent(self, event):
        pass


class MCLauncher(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self._tr = QtCore.QCoreApplication.translate
        self.start = False
        self.main = Ui_MainWindow()
        self.main.setupUi(self)
        self.load_data()
        self.setFixedSize(self.width(), self.height())
        self.center()
        self.main.stackedWidget.setCurrentIndex(0)
        self.main.stackedWidget_2.setCurrentIndex(0)
        self.main.stackedWidget_3.setCurrentIndex(0)
        self.main.stackedWidget_4.setCurrentIndex(0)
        self.main.stackedWidget_5.setCurrentIndex(0)
        self.show()
    def load_data(self):
        if not os.path.exists(".minecraft"):
            api.init_minecraft()
        if not os.path.exists("PMCL"):
            os.mkdir("PMCL")
            try:
                SetFileAttributes = ctypes.windll.kernel32.SetFileAttributesW
                SetFileAttributes.argtypes = ctypes.wintypes.LPWSTR, ctypes.wintypes.DWORD
                SetFileAttributes("PMCL", 0x02)
            except:
                pass
            open(os.path.join("PMCL", "launcher.ini"), "w")

        self.config = configparser.ConfigParser()
        self.config.read(os.path.join("PMCL", "launcher.ini"), encoding='utf-8')
        if not list(self.config.sections()):
            self.config.add_section("PMCL::Java")
            self.config.set("PMCL::Java", "JavaPath", "")
            self.config.set("PMCL::Java", "JVM", const.DEFAULT_JVM_ARGS)
            self.config.set("PMCL::Java", "MemorySize", "512")
            self.config.add_section("PMCL::Game")
            self.config.set("PMCL::Game", "UserName", "")
            self.config.add_section("PMCL::Screen")
            self.config.set("PMCL::Screen", "Width", str(const.DEFAULT_SCREEN_WIDTH))
            self.config.set("PMCL::Screen", "Height", str(const.DEFAULT_SCREEN_HEIGHT))
            self.config.set("PMCL::Screen", "Fullscreen", "")
            self.config.add_section("PMCL::Server")
            self.config.set("PMCL::Server", "Server","" )
            self.config.set("PMCL::Server", "Port","")
            self.config.write(open(os.path.join("PMCL", "launcher.ini"), 'w',encoding='utf-8'))

        version = api.get_minecraft_version(".minecraft")
        self.version_groupboxes = QtWidgets.QWidget()
        lb = QtWidgets.QVBoxLayout()
        self.version_groupboxes.setLayout(lb)
        for i in list(version.keys()):
            lb.addWidget(GroupBox(self.version_groupboxes, i, version[i], self.config))
        self.main.scrollArea.setWidget(self.version_groupboxes)

        self.javas = api.search_java()
        if self.javas:
            self.main.comboBox.addItems(list(self.javas.values()))
        self.main.lineEdit_2.setText(self.config.get("PMCL::Java", "JVM"))

        if self.config.get("PMCL::Game", "UserName"):
            self.main.label_3.setText(self.config.get("PMCL::Game", "UserName"))
        if self.config.get("PMCL::Java", "JavaPath"):
            if not os.path.exists(self.config.get("PMCL::Java", "JavaPath")):
                self.config.set("PMCL::Java", "JavaPath", "")
                self.config.write(open(os.path.join("PMCLs", "launcher.ini"), 'w'))
            else:
                self.main.comboBox.setCurrentText(
                    self.javas[self.config.get("PMCL::Java", "JavaPath")])
        self.main.lineEdit_3.setText(self.config.get("PMCL::Screen", "Width"))
        self.main.lineEdit_4.setText(self.config.get("PMCL::Screen", "Height"))
        if self.config.get("PMCL::Screen", "Fullscreen"):

            self.main.checkBox.setChecked(True)
        self.main.lineEdit.setText(self.config.get("PMCL::Game", "UserName"))
        self.main.lineEdit_5.setText(self.config.get("PMCL::Server", "Server"))
        self.main.lineEdit_6.setText(self.config.get("PMCL::Server", "Port"))
        self.main.horizontalSlider.setValue(int((self.config.getint("PMCL::Java", "MemorySize")/1024)*10))
        self.main.label_14.setText("{}GB".format(round(self.config.getint("PMCL::Java", "MemorySize")/1024,1)))
        if self.config.getint("PMCL::Java", "MemorySize")/1024>(psutil.virtual_memory().free/ 1024 / 1024 / 1024):
            self.main.label_15.setText("{}GB".format(round(psutil.virtual_memory().free/ 1024 / 1024 / 1024,1)))
        else:
            self.main.label_15.setText("{}GB".format(round(self.config.getint("PMCL::Java", "MemorySize")/1024,1)))
        self.start = True
        splash.finish(self)
        splash.deleteLater()
        self.raise_()

    def center(self):
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 2), int((screen.height() - size.height()) / 2))

    @QtCore.pyqtSlot()
    def on_lineEdit_5_editingFinished(self):
        self.config.set("PMCL::Server", "Server", self.main.lineEdit_5.text())
        self.config.write(open(os.path.join("PMCL", "launcher.ini"), 'w', encoding='utf-8'))

    @QtCore.pyqtSlot()
    def on_lineEdit_6_ditingFinished(self):
        self.config.set("PMCL::Server", "Port", self.main.lineEdit_6.text())
        self.config.write(open(os.path.join("PMCL", "launcher.ini"), 'w', encoding='utf-8'))

    @QtCore.pyqtSlot()
    def on_lineEdit_3_editingFinished(self):

        self.config.set("PMCL::Screen", "Width",self.main.lineEdit_3.text())
        self.config.write(open(os.path.join("PMCL", "launcher.ini"), 'w',encoding='utf-8'))

    @QtCore.pyqtSlot()
    def on_lineEdit_4_editingFinished(self):
        self.config.set("PMCL::Screen", "Height", self.main.lineEdit_4.text())
        self.config.write(open(os.path.join("PMCL", "launcher.ini"), 'w',encoding='utf-8'))

    @QtCore.pyqtSlot()
    def on_pushButton_15_clicked(self):
        self.main.stackedWidget_5.setCurrentIndex(1)

    @QtCore.pyqtSlot()
    def on_pushButton_14_clicked(self):
        self.main.stackedWidget_5.setCurrentIndex(0)

    @QtCore.pyqtSlot(int)
    def on_checkBox_stateChanged(self,checked):

        if checked:
            self.config.set("PMCL::Screen", "Fullscreen", "open")
        else:
            self.config.set("PMCL::Screen", "Fullscreen", "")
        self.config.write(open(os.path.join("PMCL", "launcher.ini"), 'w',encoding='utf-8'))

    @QtCore.pyqtSlot()
    def on_pushButton_clicked(self):
        self.main.stackedWidget_3.setCurrentIndex(0)

    @QtCore.pyqtSlot()
    def on_pushButton_2_clicked(self):
        self.main.stackedWidget_3.setCurrentIndex(1)

    @QtCore.pyqtSlot()
    def on_pushButton_3_clicked(self):
        self.main.stackedWidget_3.setCurrentIndex(1)

    @QtCore.pyqtSlot()
    def on_pushButton_4_clicked(self):
        self.main.stackedWidget_2.setCurrentIndex(0)

    @QtCore.pyqtSlot()
    def on_pushButton_5_clicked(self):
        self.main.stackedWidget_2.setCurrentIndex(2)

    @QtCore.pyqtSlot()
    def on_pushButton_6_clicked(self):
        self.main.stackedWidget_2.setCurrentIndex(1)

    @QtCore.pyqtSlot()
    def on_pushButton_7_clicked(self):
        self.main.stackedWidget_2.setCurrentIndex(2)

    @QtCore.pyqtSlot()
    def on_pushButton_8_clicked(self):
        self.main.stackedWidget.setCurrentIndex(1)

    @QtCore.pyqtSlot()
    def on_pushButton_9_clicked(self):
        self.main.stackedWidget.setCurrentIndex(0)

    @QtCore.pyqtSlot()
    def on_pushButton_10_clicked(self):
        self.main.stackedWidget_4.setCurrentIndex(0)

    @QtCore.pyqtSlot()
    def on_pushButton_11_clicked(self):
        self.main.stackedWidget_4.setCurrentIndex(1)

    @QtCore.pyqtSlot()
    def on_pushButton_12_clicked(self):
        self.main.stackedWidget_4.setCurrentIndex(2)

    @QtCore.pyqtSlot(int)
    def on_horizontalSlider_valueChanged(self,value):
        _value=value/10
        value=str(int(value/10*1024))
        if self.start:
            self.main.label_14.setText("{}GB".format(_value))
            if _value > (
                    psutil.virtual_memory().free / 1024 / 1024 / 1024):
                self.main.label_15.setText("{}GB".format(round(psutil.virtual_memory().free / 1024 / 1024 / 1024,1)))
                self.config.set("PMCL::Java", "MemorySize", str(psutil.virtual_memory().free / 1024 / 1024 ))
            else:
                self.config.set("PMCL::Java", "MemorySize", value)
                self.main.label_15.setText("{}GB".format(_value))
            self.config.write(open(os.path.join("PMCL", "launcher.ini"), 'w',encoding='utf-8'))

    @QtCore.pyqtSlot()
    def on_lineEdit_returnPressed(self):
        self.on_pushButton_13_clicked()

    @QtCore.pyqtSlot()
    def on_pushButton_13_clicked(self):
        self.config.set("PMCL::Game", "UserName", self.main.lineEdit.text())
        self.config.write(open(os.path.join("PMCL", "launcher.ini"), 'w',encoding='utf-8'))
        if not self.main.lineEdit.text():
            text = "尚未登陆"
        else:
            text = self.main.lineEdit.text()
        self.main.label_3.setText(text)
        self.main.stackedWidget.setCurrentIndex(0)

    @QtCore.pyqtSlot(str)
    def on_comboBox_currentTextChanged(self, text):
        if self.start:
            java = list(self.javas.keys())[self.main.comboBox.currentIndex()]
            api.const.LAUNCH_JAVA = java
            self.config.set("PMCL::Java", "JavaPath", java)
            self.config.write(open(os.path.join("PMCL", "launcher.ini"), 'w',encoding='utf-8'))

    @QtCore.pyqtSlot()
    def on_pushButton_14_clicked(self):
        self.main.stackedWidget_5.setCurrentIndex(0)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)
    app = QtWidgets.QApplication(sys.argv)
    splash = SplashScreen()
    splash.show()
    mc = MCLauncher()
    sys.exit(app.exec())
