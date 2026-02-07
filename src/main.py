from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QObject, QTimer, pyqtSlot, QSettings
from PyQt5.QtGui import QPalette, QColor, QMouseEvent
from PyQt5 import uic
import sys, pathlib

from utils.custom_widgets import WheelButton, BindDialog
from utils.custom_widgets import WHEEL_BUTTON_FIXED_HEIGHT, WHEEL_BUTTON_FIXED_WIDTH, WHEEL_BUTTON_FIXED_OFFSET_X, WHEEL_BUTTON_FIXED_OFFSET_Y
from utils.custom_widgets import SELECTOR_FIXED_HEIGHT, SELECTOR_FIXED_WIDTH, SELECTOR_FIXED_OFFSET_X, SELECTOR_FIXED_OFFSET_Y

import logging
logger = logging.getLogger(__name__)
from utils.setup_logging import setup_logging
setup_logging()

SOFTWARE_NAME = "SWB"
SOFTWARE_VERSION = "1.0.0"

# Get the absolute path
ABS_PATH = pathlib.Path(__file__).parent

class TimedWorker(QObject):
    THREAD_TIMEOUT = 1000 # ms
    signal_stop = pyqtSignal()
    signal_info = pyqtSignal(str)
    signal_warning = pyqtSignal(str)
    signal_error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.running = False
        self.signal_stop.connect(self.stop)

    @pyqtSlot()
    def start(self):
        logger.info(f"Starting timedThread {QThread.currentThread()}.")
        self.running = True
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.run)
        # User thread initialization
        # ==========================
        self.timer.start(self.THREAD_TIMEOUT)

    @pyqtSlot()
    def run(self):
        '''Periodic loop'''
        # QThread.msleep(3000)
        # self.signal_error.emit("Teste")
        # self.stop()
        return

    @pyqtSlot()
    def stop(self):
        '''This slot could be triggered at any moment, but only will run after ```this``` thread
        event loop is free, after ```self.run``` finished.'''
        if not self.running:
            logger.info(f"timedThread {QThread.currentThread()} already stopped.")
            return
        logger.info(f"Stopping timedThread {QThread.currentThread()}.")
        self.timer.stop()
        logger.info(f"timedThread {QThread.currentThread()} stopped.")
        self.running = False

class MainTimedWorker(QObject):
    THREAD_TIMEOUT = 200 # ms
    signal_stop = pyqtSignal()
    signal_info = pyqtSignal(str)
    signal_warning = pyqtSignal(str)
    signal_error = pyqtSignal(str)

    def __init__(self, mainWindow: QMainWindow):
        super().__init__()
        self.running = False
        self.signal_stop.connect(self.stop)

        self.mainWindow = mainWindow

    @pyqtSlot()
    def start(self):
        logger.info(f"Starting MainTimedThread {QThread.currentThread()}.")
        self.running = True
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.run)
        self.timer.start(self.THREAD_TIMEOUT)

        self.mainWindow.signal_start_post_processing.emit()

        # Inner Threads
        self._thread0 = QThread()
        self._worker0 = TimedWorker()
        self._worker0.moveToThread(self._thread0)
        self._thread0.started.connect(self._worker0.start)
        self._worker0.signal_info.connect(self.event_info)
        self._worker0.signal_warning.connect(self.event_warning)
        self._worker0.signal_error.connect(self.event_error)
        self._thread0.start()

    @pyqtSlot()
    def run(self):
        '''Periodic loop'''

        pass

    @pyqtSlot()
    def stop(self):
        '''This slot could be triggered at any moment, but only will run after ```this``` thread
        event loop is free, after ```self.run``` finished.'''
        logger.info(f"Stopping MainTimedThread {QThread.currentThread()}.")
        self.timer.stop()
        self._worker0.signal_stop.emit()
        while True:
            if self._worker0.running:
                continue
            # ...
            # if self._worker10.running:
            #     continue
            break
        logger.info(f"MainTimedThread {QThread.currentThread()} stopped.")
        self.running = False

    @pyqtSlot(str)
    def event_info(self, message):
        self.signal_info.emit(message)
    @pyqtSlot(str)
    def event_warning(self, message):
        self.signal_warning.emit(message)
    @pyqtSlot(str)
    def event_error(self, message):
        self.signal_error.emit(message)

class MainWindow(QMainWindow):
    signal_start_post_processing = pyqtSignal()

    def __init__(self):
        super().__init__()

        # Get the absolute path
        self.absPath = ABS_PATH

        # Loading GUI
        self.ui = uic.loadUi(self.absPath/'gui/mainwindow.ui', self)

        self.setWindowTitle(f"{SOFTWARE_NAME} - v{SOFTWARE_VERSION}")

        self.settings = QSettings("swb","swb")

        self.signal_start_post_processing.connect(self.post_processing)

        self.centralWidget().setMouseTracking(True)
        self.status = self.statusBar()

        imageLabel = self.ui.label

        buttonHeight = WHEEL_BUTTON_FIXED_HEIGHT
        buttonWidth = WHEEL_BUTTON_FIXED_WIDTH
        buttonOffsetX = WHEEL_BUTTON_FIXED_OFFSET_X
        buttonOffsetY = WHEEL_BUTTON_FIXED_OFFSET_Y
        self.buttons = [
            WheelButton(self.settings, '00', imageLabel, 856, 86, buttonHeight, buttonWidth, buttonOffsetX, buttonOffsetY),   # Top Top Right
            WheelButton(self.settings, '01', imageLabel, 789, 114, buttonHeight, buttonWidth, buttonOffsetX, buttonOffsetY),  # Top Mid Right
            WheelButton(self.settings, '02', imageLabel, 759, 191, buttonHeight, buttonWidth, buttonOffsetX, buttonOffsetY),  # Top Bottom Right
            WheelButton(self.settings, '03', imageLabel, 732, 308, buttonHeight, buttonWidth, buttonOffsetX, buttonOffsetY),  # Bottom Top Right
            WheelButton(self.settings, '04', imageLabel, 724, 391, buttonHeight, buttonWidth, buttonOffsetX, buttonOffsetY),  # Bottom Mid Right
            WheelButton(self.settings, '05', imageLabel, 724, 475, buttonHeight, buttonWidth, buttonOffsetX, buttonOffsetY),  # Bottom Bottom Right
            WheelButton(self.settings, '06', imageLabel, 177, 85, buttonHeight, buttonWidth, buttonOffsetX, buttonOffsetY),   # Top Top Left
            WheelButton(self.settings, '07', imageLabel, 243, 117, buttonHeight, buttonWidth, buttonOffsetX, buttonOffsetY),  # Top Mid Left
            WheelButton(self.settings, '08', imageLabel, 273, 190, buttonHeight, buttonWidth, buttonOffsetX, buttonOffsetY),  # Top Bottom Left
            WheelButton(self.settings, '09', imageLabel, 300, 305, buttonHeight, buttonWidth, buttonOffsetX, buttonOffsetY),  # Bottom Top Left
            WheelButton(self.settings, '10', imageLabel, 309, 391, buttonHeight, buttonWidth, buttonOffsetX, buttonOffsetY),  # Bottom Mid Left
            WheelButton(self.settings, '11', imageLabel, 311, 475, buttonHeight, buttonWidth, buttonOffsetX, buttonOffsetY),  # Bottom Bottom Left
        ]

        selectorButtonHeight = SELECTOR_FIXED_HEIGHT
        selectorButtonWidth = SELECTOR_FIXED_WIDTH
        selectorButtonOffsetX = SELECTOR_FIXED_OFFSET_X
        selectorButtonOffsetY = SELECTOR_FIXED_OFFSET_Y
        self.leftSelectorsButtons = [
            WheelButton(self.settings, '12', imageLabel, 415, 171, selectorButtonHeight, selectorButtonWidth, selectorButtonOffsetX, selectorButtonOffsetY),  # Left Selector 00
            WheelButton(self.settings, '13', imageLabel, 437, 181, selectorButtonHeight, selectorButtonWidth, selectorButtonOffsetX, selectorButtonOffsetY),  # Left Selector 01
            WheelButton(self.settings, '14', imageLabel, 451, 196, selectorButtonHeight, selectorButtonWidth, selectorButtonOffsetX, selectorButtonOffsetY),  # Left Selector 02
            WheelButton(self.settings, '15', imageLabel, 458, 222, selectorButtonHeight, selectorButtonWidth, selectorButtonOffsetX, selectorButtonOffsetY),  # Left Selector 03
            WheelButton(self.settings, '16', imageLabel, 451, 244, selectorButtonHeight, selectorButtonWidth, selectorButtonOffsetX, selectorButtonOffsetY),  # Left Selector 04
            WheelButton(self.settings, '17', imageLabel, 437, 262, selectorButtonHeight, selectorButtonWidth, selectorButtonOffsetX, selectorButtonOffsetY),  # Left Selector 05
            WheelButton(self.settings, '18', imageLabel, 415, 270, selectorButtonHeight, selectorButtonWidth, selectorButtonOffsetX, selectorButtonOffsetY),  # Left Selector 06
            WheelButton(self.settings, '19', imageLabel, 394, 262, selectorButtonHeight, selectorButtonWidth, selectorButtonOffsetX, selectorButtonOffsetY),  # Left Selector 07
            WheelButton(self.settings, '20', imageLabel, 379, 244, selectorButtonHeight, selectorButtonWidth, selectorButtonOffsetX, selectorButtonOffsetY),  # Left Selector 08
            WheelButton(self.settings, '21', imageLabel, 374, 222, selectorButtonHeight, selectorButtonWidth, selectorButtonOffsetX, selectorButtonOffsetY),  # Left Selector 09
            WheelButton(self.settings, '22', imageLabel, 381, 196, selectorButtonHeight, selectorButtonWidth, selectorButtonOffsetX, selectorButtonOffsetY),  # Left Selector 10
            WheelButton(self.settings, '23', imageLabel, 395, 181, selectorButtonHeight, selectorButtonWidth, selectorButtonOffsetX, selectorButtonOffsetY),  # Left Selector 11
        ]
        selectorButtonOffsetX = SELECTOR_FIXED_OFFSET_X+200
        selectorButtonOffsetY = SELECTOR_FIXED_OFFSET_Y
        self.rightSelectors = [
            WheelButton(self.settings, '24', imageLabel, 415, 171, selectorButtonHeight, selectorButtonWidth, selectorButtonOffsetX, selectorButtonOffsetY),  # Right Selector 00
            WheelButton(self.settings, '25', imageLabel, 437, 181, selectorButtonHeight, selectorButtonWidth, selectorButtonOffsetX, selectorButtonOffsetY),  # Right Selector 01
            WheelButton(self.settings, '26', imageLabel, 451, 196, selectorButtonHeight, selectorButtonWidth, selectorButtonOffsetX, selectorButtonOffsetY),  # Right Selector 02
            WheelButton(self.settings, '27', imageLabel, 458, 222, selectorButtonHeight, selectorButtonWidth, selectorButtonOffsetX, selectorButtonOffsetY),  # Right Selector 03
            WheelButton(self.settings, '28', imageLabel, 451, 244, selectorButtonHeight, selectorButtonWidth, selectorButtonOffsetX, selectorButtonOffsetY),  # Right Selector 04
            WheelButton(self.settings, '29', imageLabel, 437, 262, selectorButtonHeight, selectorButtonWidth, selectorButtonOffsetX, selectorButtonOffsetY),  # Right Selector 05
            WheelButton(self.settings, '30', imageLabel, 415, 270, selectorButtonHeight, selectorButtonWidth, selectorButtonOffsetX, selectorButtonOffsetY),  # Right Selector 06
            WheelButton(self.settings, '31', imageLabel, 394, 262, selectorButtonHeight, selectorButtonWidth, selectorButtonOffsetX, selectorButtonOffsetY),  # Right Selector 07
            WheelButton(self.settings, '32', imageLabel, 379, 244, selectorButtonHeight, selectorButtonWidth, selectorButtonOffsetX, selectorButtonOffsetY),  # Right Selector 08
            WheelButton(self.settings, '33', imageLabel, 374, 222, selectorButtonHeight, selectorButtonWidth, selectorButtonOffsetX, selectorButtonOffsetY),  # Right Selector 09
            WheelButton(self.settings, '34', imageLabel, 381, 196, selectorButtonHeight, selectorButtonWidth, selectorButtonOffsetX, selectorButtonOffsetY),  # Right Selector 10
            WheelButton(self.settings, '35', imageLabel, 395, 181, selectorButtonHeight, selectorButtonWidth, selectorButtonOffsetX, selectorButtonOffsetY),  # Right Selector 11
        ]
        selectorButtonOffsetX = SELECTOR_FIXED_OFFSET_X+100
        selectorButtonOffsetY = SELECTOR_FIXED_OFFSET_Y+312
        self.bottomSelectors = [
            WheelButton(self.settings, '36', imageLabel, 415, 171, selectorButtonHeight, selectorButtonWidth, selectorButtonOffsetX, selectorButtonOffsetY),  # Bottom Selector 00
            WheelButton(self.settings, '37', imageLabel, 437, 181, selectorButtonHeight, selectorButtonWidth, selectorButtonOffsetX, selectorButtonOffsetY),  # Bottom Selector 01
            WheelButton(self.settings, '38', imageLabel, 451, 196, selectorButtonHeight, selectorButtonWidth, selectorButtonOffsetX, selectorButtonOffsetY),  # Bottom Selector 02
            WheelButton(self.settings, '39', imageLabel, 458, 222, selectorButtonHeight, selectorButtonWidth, selectorButtonOffsetX, selectorButtonOffsetY),  # Bottom Selector 03
            WheelButton(self.settings, '40', imageLabel, 451, 244, selectorButtonHeight, selectorButtonWidth, selectorButtonOffsetX, selectorButtonOffsetY),  # Bottom Selector 04
            WheelButton(self.settings, '41', imageLabel, 437, 262, selectorButtonHeight, selectorButtonWidth, selectorButtonOffsetX, selectorButtonOffsetY),  # Bottom Selector 05
            WheelButton(self.settings, '42', imageLabel, 415, 270, selectorButtonHeight, selectorButtonWidth, selectorButtonOffsetX, selectorButtonOffsetY),  # Bottom Selector 06
            WheelButton(self.settings, '43', imageLabel, 394, 262, selectorButtonHeight, selectorButtonWidth, selectorButtonOffsetX, selectorButtonOffsetY),  # Bottom Selector 07
            WheelButton(self.settings, '44', imageLabel, 379, 244, selectorButtonHeight, selectorButtonWidth, selectorButtonOffsetX, selectorButtonOffsetY),  # Bottom Selector 08
            WheelButton(self.settings, '45', imageLabel, 374, 222, selectorButtonHeight, selectorButtonWidth, selectorButtonOffsetX, selectorButtonOffsetY),  # Bottom Selector 09
            WheelButton(self.settings, '46', imageLabel, 381, 196, selectorButtonHeight, selectorButtonWidth, selectorButtonOffsetX, selectorButtonOffsetY),  # Bottom Selector 10
            WheelButton(self.settings, '47', imageLabel, 395, 181, selectorButtonHeight, selectorButtonWidth, selectorButtonOffsetX, selectorButtonOffsetY),  # Bottom Selector 11
        ]

        self.allButtons = (self.buttons + self.leftSelectorsButtons + self.rightSelectors + self.bottomSelectors)
        # for button in self.allButtons:
        #     button.clicked.connect()

        # Main Thread
        self._thread = QThread()
        self._worker = MainTimedWorker(self)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.start)
        self._worker.signal_info.connect(self.event_info)
        self._worker.signal_warning.connect(self.event_warning)
        self._worker.signal_error.connect(self.event_error)
        self._thread.start()

    @pyqtSlot()
    def cleanUp(self):
        '''CleanUp shutdown garantee a thread safety application shutdown.'''
        logger.info("Starting shutdown...")
        self._worker.signal_stop.emit()
        logger.info("Waiting until all threads quit...")
        while True:
            if not self._worker.running:
                break
        logger.info("Quitting application.")

    @pyqtSlot(str)
    def event_info(self, message):
        QMessageBox.information(self, "Info", message)
    @pyqtSlot(str)
    def event_warning(self, message):
        QMessageBox.warning(self, "Warning", message)
    @pyqtSlot(str)
    def event_error(self, message):
        QMessageBox.critical(self, "Error", message)
        self.close()

    @pyqtSlot()
    def post_processing(self):
        BindDialog(self, self.settings, id='00').show()
    
    def mouseMoveEvent(self, event:QMouseEvent):
        x = event.pos().x()
        y = event.pos().y()
        gx = event.globalPos().x()
        gy = event.globalPos().y()
        self.status.showMessage(f"Mouse Position: ({x}, {y}) | Mouse GPosition: ({gx}, {gy})")

    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    # https://stackoverflow.com/questions/48256772/dark-theme-for-qt-widgets
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.black)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    mainWindow = MainWindow()
    mainWindow.show()
    app.aboutToQuit.connect(mainWindow.cleanUp)
    app.processEvents()
    app.exec_()