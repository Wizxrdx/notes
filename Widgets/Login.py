from typing import Tuple

from PyQt5 import QtGui
from PyQt5.QtCore import QPoint, QRect, Qt
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QWidget, QSizePolicy, QLabel, QAbstractButton, QGridLayout, QPushButton, QLineEdit


class ProfileButton(QAbstractButton):
    def __init__(self, parent: QWidget, name='', image=None):
        super().__init__(parent)
        self.pixmap = image
        self.name = name
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        size = self.parent().frameGeometry()
        self.setFixedSize(size.width() / 4, size.height() / 4)

    def paintEvent(self, e: QtGui.QPaintEvent) -> None:
        painter = QPainter(self)
        if self.underMouse():
            painter.setBrush(QColor(150, 150, 150))
            painter.setPen(QColor(150, 150, 150))
        else:
            painter.setBrush(QColor(200, 200, 200))
            painter.setPen(QColor(200, 200, 200))
        painter.drawRect(e.rect())

    def updateGeometry(self) -> None:
        size = self.parent().frameGeometry()
        height = size.height() / 2
        self.setFixedWidth(int(size.width() / 10))
        if (self.width() / 2) * 3 != height:
            self.setFixedHeight(int((self.width() / 2) * 3))


class ProfileCreateButton(ProfileButton):
    def __init__(self, parent):
        super().__init__(parent)

    def paintEvent(self, e: QtGui.QPaintEvent) -> None:
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setBrush(QColor(255, 255, 255))
        painter.setPen(QColor(255, 255, 255))
        size = self.frameGeometry()
        painter.drawRect(QRect((size.width()) / 2 - 5, (size.height()) / 2 - 25, 10, 50))  # vertical line
        painter.drawRect(QRect((size.width()) / 2 - 25, (size.height()) / 2 - 5, 50, 10))  # horizontal line


class ProfileLoginButton(ProfileButton):
    def __init__(self, parent, name, image=None):
        super().__init__(parent, name, image)

    def paintEvent(self, e: QtGui.QPaintEvent) -> None:
        super().paintEvent(e)
        painter = QPainter(self)
        size = self.frameGeometry()
        font = painter.font()

        painter.setBrush(QColor(255, 255, 255))
        painter.setPen(QColor(255, 255, 255))
        profile_background = QRect((size.width() / 8) / 2, (size.height() / 7) / 2, size.width() - (size.width() / 8),
                                   size.width() - (size.height() / 7))
        painter.drawRect(profile_background)
        label_background = QRect(profile_background.bottomLeft() + QPoint(0, (size.height() / 7) / 2),
                                 QPoint(profile_background.right(), size.height() - (size.height() / 7) / 2))
        painter.drawRect(label_background)

        painter.setPen(QColor(0, 0, 0))
        font.setPointSizeF((label_background.width() / 7))
        painter.setFont(font)
        painter.drawText(label_background, Qt.AlignVCenter | Qt.AlignHCenter, self.name)

        if self.pixmap is None:
            profile_background.adjust(5, 5, -5, -5)
            font.setPointSizeF(profile_background.width() - 30)
            painter.setFont(font)
            painter.drawText(profile_background, Qt.AlignVCenter | Qt.AlignHCenter, self.name[0].upper())
        else:
            painter.drawPixmap(e.rect(), self.pixmap)


class LoginLineEdit(QLineEdit):
    def __init__(self):
        super().__init__()
        self.isErrorShown = False

    def isShowingError(self):
        return self.isErrorShown

    def showError(self):
        self.isErrorShown = True
        self.setStyleSheet("border: 1px solid red")

    def stopShowingError(self):
        self.setStyleSheet('')
        self.isErrorShown = False


class Opacity(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        size = parent.size()
        self.setGeometry(0, 0, size.width(), size.height())
        self.show()

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        size = self.parent().frameGeometry()
        qp = QPainter()
        qp.begin(self)
        qp.setBrush(QColor(30, 30, 30, 120))
        qp.setPen(QColor(30, 30, 30, 120))
        qp.setRenderHint(QPainter.Antialiasing, True)
        qp.drawRect(0, 0, size.width(), size.height())

    def updateGeometry(self) -> None:
        size = self.parent().size()
        self.setGeometry(0, 0, size.width(), size.height())


class Popup(QWidget):
    def __init__(self, parent, title, *widget: QWidget):
        super().__init__(Opacity(parent))
        self.error_label = QLabel('')
        font = self.font()
        font.setPointSizeF(self.size().width() / 7)
        self.setFont(font)
        self.__initUI(title, widget)
        self.move((self.parent().size().width() - self.size().width()) / 2,
                  (self.parent().size().height() - self.size().height()) / 2)

    def __initUI(self, title, widget: Tuple[QWidget]):
        label = QLabel(self)
        label.setText(title)
        label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.error_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        close_button = QPushButton('X')
        close_button.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        close_button.clicked.connect(self.hide)

        layout = QGridLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(label, 0, 0, 1, 2)
        layout.addWidget(close_button, 0, 2, 1, 1)
        layout.addWidget(self.error_label, 1, 0, 1, 3)
        for i in range(len(widget)):
            layout.addWidget(widget[i], i+2, 0, 1, 3)

        self.setLayout(layout)
        self.show()

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        size = self.frameGeometry()
        painter = QPainter()
        painter.begin(self)
        painter.setBrush(QColor(255, 255, 255, 200))
        painter.setPen(QColor(255, 255, 255, 200))
        painter.drawRect(QRect(0, 0, size.width(), size.height()))

    def show(self) -> None:
        super().show()

    def hide(self) -> None:
        super().hide()
        self.parent().hide()


class ProfileCreatePopup(Popup):
    def __init__(self, parent):
        self.name = LoginLineEdit()
        self.password = LoginLineEdit()
        self.password2 = LoginLineEdit()
        self.create_profile_button = QPushButton('Create Profile')
        super().__init__(parent, 'Create a Profile', self.name, self.password, self.password2, self.create_profile_button)

        self.initUI()

    def initUI(self):
        self.name.setPlaceholderText('Name')
        self.name.textEdited.connect(self.clear_errors)
        self.password.setPlaceholderText('Password')
        self.password.setEchoMode(QLineEdit.Password)
        self.password.textEdited.connect(self.clear_errors)
        self.password2.setPlaceholderText('Retype Password')
        self.password2.setEchoMode(QLineEdit.Password)
        self.password2.textEdited.connect(self.clear_errors)
        self.create_profile_button.clicked.connect(self.create_profile)

    def clear_errors(self):
        self.name.stopShowingError()
        self.password.stopShowingError()
        self.password2.stopShowingError()
        self.error_label.setText('')

    def create_profile(self):
        if self.check_password():
            login_window = self.parent().parent()
            if login_window.create_profile(self.name.text(), self.password.text()):
                self.hide()
            else:
                self.error_name()

    def error_name(self):
        self.name.showError()
        self.error_label.setText('Name already exists.')

    def check_password(self):
        if not len(self.name.text()):
            self.name.showError()
            self.error_label.setText('cannot be empty')
            return False
        elif not len(self.password.text()):
            self.password.showError()
            self.error_label.setText('cannot be empty')
            return False
        elif not len(self.password2.text()):
            self.password2.showError()
            self.error_label.setText('cannot be empty')
            return False

        if (len(self.password.text()) < 4) and (len(self.password2.text()) < 4):
            self.password.showError()
            self.password2.showError()
            self.error_label.setText('password is too short')
            return False
        elif self.password.text() != self.password2.text():
            self.password.showError()
            self.password2.showError()
            self.error_label.setText('password is not the same')
            return False
        elif len(self.name.text()) > 10:
            self.name.showError()
            self.error_label.setText('name is too long')
            return False
        else:
            return True


class ProfileLoginPopup(Popup):
    def __init__(self, parent, name, password):
        self.name = name
        self.password = password

        name_box = QLineEdit()
        name_box.setText(self.name)
        name_box.setEnabled(False)
        self.password_box = LoginLineEdit()
        self.login_button = QPushButton('Login')
        self.login_button.clicked.connect(self.login_profile)

        super().__init__(parent, 'Profile Login', name_box, self.password_box, self.login_button)

        self.initUI()

    def initUI(self):
        self.password_box.setPlaceholderText('Password')
        self.password_box.setEchoMode(QLineEdit.Password)
        self.password_box.textEdited.connect(self.clear_errors)

    def clear_errors(self):
        self.password_box.stopShowingError()
        self.error_label.setText('')

    def login_profile(self):
        if self.check_password():
            login_window = self.parent().parent()
            login_window.onLogin.emit(self.name)
            self.hide()

    def check_password(self):
        if len(self.password_box.text()) < 4:
            self.password_box.showError()
            self.error_label.setText('password is too short')
            return False
        elif self.password_box.text() != self.password:
            self.password_box.showError()
            self.error_label.setText('password is incorrect')
            return False
        else:
            return True
