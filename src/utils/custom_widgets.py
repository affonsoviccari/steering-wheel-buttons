from PyQt5.QtWidgets import *
from PyQt5.QtCore import QPoint, QSize, QSettings, pyqtSlot
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5 import uic
import sys, pathlib
import keyboard
from keyboard import KeyboardEvent
from utils.bind import *

WHEEL_BUTTON_FIXED_HEIGHT = 70
WHEEL_BUTTON_FIXED_WIDTH = 70
WHEEL_BUTTON_FIXED_OFFSET_X = -42
WHEEL_BUTTON_FIXED_OFFSET_Y = -42

SELECTOR_FIXED_HEIGHT = 23
SELECTOR_FIXED_WIDTH = 23
SELECTOR_FIXED_OFFSET_X = -20
SELECTOR_FIXED_OFFSET_Y = -20

# Get the absolute path
ABS_PATH = pathlib.Path(__file__).parent.parent

WARNING_LABEL = "⚠️"
GPIO_LINK_LABEL = "🪢"
KEY_LINK_LABEL = "🕹️"

class BindDialog(QDialog):
    def __init__(self, parent, settings:QSettings, id:str):
        super().__init__(parent)

        self.absPath = ABS_PATH
        self.ui = uic.loadUi(self.absPath/'gui/bindDialog.ui', self)

        # Keyboard Eventcallback
        keyboard.on_press(self.keyboard_event_callback)

        self.settings = settings
        self.id = id

        useDefault = self.settings.value("/bind/use-default", True)
        self.ui.checkBoxKey.setChecked(useDefault)
        if useDefault:
            self.ui.lineEditKey.setEnabled(False)
            self.ui.lineEditKey.setText(f"DEFAULT-PARAMETER-ID-{self.id}")
        self.ui.checkBoxKey.stateChanged.connect(self.use_bind_default_value_changed)
        
    @pyqtSlot(int)
    def use_bind_default_value_changed(self, value: int):
        self.ui.checkBoxKey.setChecked(value)
        self.settings.setValue("/bind/use-default", value)
        if value is True:
            self.ui.lineEditKey.setText(f"DEFAULT-PARAMETER-ID-{self.id}")

    def keyboard_event_callback(self, event:KeyboardEvent):
        print(event.name)

class WheelButton(QPushButton):
    def __init__(self, settings:QSettings, id:str, label:QLabel, xpos:int, ypos:int, height:int, width: int, offsetX:int, offsetY:int):
        super().__init__()

        self.absPath = ABS_PATH
        self.id = id
        self.settings = settings

        self.setParent(label)
        self.setFixedHeight(height)
        self.setFixedWidth(width)
        self.setStyleSheet(
            "QPushButton {background-color: transparent;border: none; font-size:23px;}"
            "QPushButton:hover {background-color: rgba(100, 100, 100, 100);border: 1px solid grey;}"
            )
        pos = QPoint(xpos+offsetX, ypos+offsetY)
        self.move(pos)

        if not get_gpio_binded_button(self.settings, self.id):
            self.setToolTip(KEY_LINK_LABEL)
            self.setText(WARNING_LABEL)
        if not get_key_binded_button(self.settings, self.id):
            self.setToolTip(self.toolTip()+GPIO_LINK_LABEL)
            self.setText(WARNING_LABEL)