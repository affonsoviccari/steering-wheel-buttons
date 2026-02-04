from PyQt5.QtWidgets import *
from PyQt5.QtCore import QPoint, QSize
from PyQt5.QtGui import QIcon, QPixmap
import sys, pathlib

WHEEL_BUTTON_FIXED_HEIGHT = 70
WHEEL_BUTTON_FIXED_WIDTH = 70
WHEEL_BUTTON_FIXED_OFFSET_X = -42
WHEEL_BUTTON_FIXED_OFFSET_Y = -42

SELECTOR_FIXED_HEIGHT = 23
SELECTOR_FIXED_WIDTH = 23
SELECTOR_FIXED_OFFSET_X = -20
SELECTOR_FIXED_OFFSET_Y = -20

# Get the absolute path
ABS_PATH = pathlib.Path(__file__).parent

class WheelButton(QPushButton):
    def __init__(self, id:str, label:QLabel, xpos:int, ypos:int, height:int, width: int, offsetX:int, offsetY:int):
        super().__init__()

        self.absPath = ABS_PATH

        self.setParent(label)
        self.setFixedHeight(height)
        self.setFixedWidth(width)
        self.setStyleSheet(
            "QPushButton {background-color: transparent;border: none; font-size:23px;}"
            "QPushButton:hover {background-color: rgba(100, 100, 100, 100);border: 1px solid grey;}"
            )
        pos = QPoint(xpos+offsetX, ypos+offsetY)
        self.move(pos)

        self.setText("⚠️")