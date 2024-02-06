import mainProgram
from lib import *

effect = mainProgram.home()
parent = None
class MyButton(QtWidgets.QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)

    def leaveEvent(self, event):
        self.setStyleSheet("QPushButton { background-color: rgb(45, 153, 174); color: black }")


effect.homePage.LBFilter = MyButton(parent)