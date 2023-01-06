import sys

from PyQt5.QtWidgets import QApplication
from libs import ViewPort


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication([])
    viewport = ViewPort()

    viewport.show()
    sys.excepthook = except_hook
    app.exec_()
