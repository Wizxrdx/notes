from PyQt5 import QtGui
from PyQt5.QtCore import QRect, Qt, QSize, QPoint
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QAbstractButton, QSizePolicy, QMenu, QMessageBox, QVBoxLayout, QLabel


class NoteButton(QAbstractButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setFixedSize(160, 240)

    def paintEvent(self, e: QtGui.QPaintEvent) -> None:
        painter = QPainter()
        painter.begin(self)
        if not self.underMouse():
            painter.setBrush(QColor(200, 200, 200))
            painter.setPen(QColor(200, 200, 200))
        else:
            painter.setBrush(QColor(150, 150, 150))
            painter.setPen(QColor(150, 150, 150))
        painter.drawRect(e.rect())


class CreateNoteButton(NoteButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.clicked.connect(self.__createNote)

    def __createNote(self):
        self.parent().noteCreated.emit()

    def paintEvent(self, e: QtGui.QPaintEvent) -> None:
        super().paintEvent(e)
        painter = QPainter()
        painter.begin(self)
        painter.setBrush(QColor(255, 255, 255))
        painter.setPen(QColor(255, 255, 255))
        center = e.rect().center()
        rect1 = QRect(center, QSize(70, 10))
        rect1.moveTo(center-QPoint(rect1.width()/2, rect1.height()/2))
        rect2 = QRect(center, QSize(10, 70))
        rect2.moveTo(center-QPoint(rect2.width()/2, rect2.height()/2))
        painter.drawRect(rect1)
        painter.drawRect(rect2)


class OpenNoteButton(NoteButton):
    def __init__(self, parent, title, favorite: bool = False):
        super().__init__(parent)
        self.__title = title
        self.__favorite = favorite
        self.__contextMenu = self.__createContextMenu()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(lambda point: self.__contextMenu.exec_(self.mapToGlobal(point)))
        self.clicked.connect(self.__openNote)

        self.initUI()

    def initUI(self):
        profile = self.parent().parent().getProfile()
        note = profile.read_note(self.__title)
        title = QLabel(self.__title)
        content = QLabel(note[1])
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        layout.addWidget(title)
        layout.addWidget(content)

        layout.addLayout(layout)
        self.setLayout(layout)

    def __createContextMenu(self):
        menu = QMenu(self)
        menu.addAction('Open', self.__openNote)
        menu.addAction('Delete', self.__deleteNote)
        menu.addSeparator()
        if self.__favorite:
            menu.addAction('Remove as favorite', self.__removeToFavorite)
        else:
            menu.addAction('Add as favorite', self.__addToFavorite)

        return menu

    def __addToFavorite(self):
        self.parent().noteFavorited.emit(self.__title, True)

    def __removeToFavorite(self):
        self.parent().noteFavorited.emit(self.__title, False)

    def __openNote(self):
        self.parent().noteOpened.emit(self.__title)

    def __deleteNote(self):
        message = QMessageBox(self)
        message.setWindowTitle('Delete ' + self.__title)
        message.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        message.setText('Are you sure you want to delete this note?')
        retval = message.exec_()

        if retval == QMessageBox.Yes:
            self.parent().noteDeleted.emit(self.__title)

    def paintEvent(self, e: QtGui.QPaintEvent) -> None:
        super().paintEvent(e)
