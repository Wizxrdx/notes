import sys

from PyQt5.QtWidgets import QApplication

from NoteApp import NoteApp


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == "__main__":
    sys.excepthook = except_hook

app = QApplication(sys.argv)
win = NoteApp()

sys.exit(app.exec_())
