from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QObject, QTimer, pyqtSlot
from PyQt5.QtGui import QPalette, QColor
import sys

import logging
logger = logging.getLogger(__name__)
from utils.setup_logging import setup_logging
setup_logging()

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
        QThread.msleep(3000)
        self.signal_error.emit("Teste")
        self.stop()
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
        logger.info(f"Starting MainTimedThread {QThread.currentThread()}.")
        self.running = True
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.run)
        self.timer.start(self.THREAD_TIMEOUT)

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
    def __init__(self):
        super().__init__()

        # Main Thread
        self._thread = QThread()
        self._worker = MainTimedWorker()
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