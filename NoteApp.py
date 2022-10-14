from PyQt5 import QtGui
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QStackedWidget, QLabel, QVBoxLayout, QPushButton, QLineEdit, \
    QTextEdit, QMessageBox, QLayout, QMenuBar, QAction

from Database import Database, Profile
from Widgets.Login import ProfileLoginButton, ProfileCreateButton, ProfileCreatePopup, ProfileLoginPopup
from Widgets.MainMenu import CreateNoteButton, OpenNoteButton


class GUIFormatter:
    def __init__(self):
        pass

    def clearAllWidgets(self: QWidget, layout: QLayout) -> QLayout:
        if layout is None:
            self.layout()

        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().setParent(None)
        return layout


class NoteApp(QStackedWidget, Database):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('icon.ico'))
        self.setWindowTitle("Note")
        self.__profile = Profile(self)
        self.__initUI()

    def __iter__(self):
        widgets = []
        for i in range(self.count()):
            widgets.append(self.widget(i))
        return iter(widgets)

    def __initUI(self):
        loginWindow = LoginUI(self)
        loginWindow.onLogin.connect(self.__profileLogin)
        loginWindow.onCreate.connect(self.__profileCreate)
        self.addWidget(loginWindow)
        mainWindow = MainUI(self)
        mainWindow.onLogout.connect(self.__profileLogout)
        mainWindow.noteOpened.connect(self.__openNote)
        mainWindow.noteFavorited.connect(self.__favoriteNote)
        mainWindow.noteDeleted.connect(self.__deleteNote)
        mainWindow.noteCreated.connect(self.__createNote)
        self.addWidget(mainWindow)
        noteWindow = NoteUI(self)
        noteWindow.noteExited.connect(self.__noteExit)
        self.addWidget(noteWindow)

        self.showMaximized()

    def __noteExit(self):
        self.setCurrentWidget('main')
        self.currentWidget().reloadUI()

    def __openNote(self, name):
        self.setCurrentWidget('note')
        self.currentWidget().setNote(name)

    def __favoriteNote(self, name, mode):
        note = self.__profile.read_note(name)
        self.__profile.update_note(note[0], note[2], note[0], note[1], mode)
        self.currentWidget().reloadUI()

    def __deleteNote(self, name):
        self.__profile.delete_note(name)
        self.currentWidget().reloadUI()

    def __createNote(self):
        self.__profile.create_note()
        self.currentWidget().reloadUI()

    def __profileCreate(self, name):
        profile = super().read_profile(name)
        self.__profile.init(profile[0], profile[1], profile[2])
        self.currentWidget().reloadUI()
        self.setCurrentWidget('main')
        self.currentWidget().reloadUI()

    def __profileLogin(self, name):
        profile = super().read_profile(name)
        self.__profile.init(profile[0], profile[1], profile[2])
        self.setCurrentWidget('main')
        self.currentWidget().reloadUI()

    def __profileLogout(self):
        self.setCurrentWidget('login')
        del self.__profile
        self.__profile = Profile(self)

    def getProfile(self) -> Profile:
        return self.__profile

    def setCurrentWidget(self, name: str):
        for widget in self:
            if str(widget) == name:
                super().setCurrentWidget(widget)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self.currentWidget().updateGeometry()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.currentWidget().close()
        super().closeDB()


class LoginUI(QWidget, GUIFormatter):
    onLogin = pyqtSignal(str)
    onCreate = pyqtSignal(str)

    def __init__(self, parent: NoteApp):
        super().__init__(parent)

        self.__layout = QHBoxLayout()
        self.__layout.setAlignment(Qt.AlignCenter)
        self.__layout.setSpacing(10)
        self.popup = None
        self.create_button = ProfileCreateButton(self)
        self.profile_buttons = []
        self.reloadUI()

    def __str__(self):
        return 'login'

    def __initUI(self):
        self.create_button.clicked.connect(self.show_create_profile_popup)
        self.__layout.addWidget(self.create_button)

        self.setLayout(self.__layout)
        self.updateGeometry()

    def reloadUI(self):
        self.create_button = ProfileCreateButton(self)
        self.profile_buttons = []
        self.__layout = super().clearAllWidgets(self.__layout)

        for profile in self.parent().get_profiles():
            button = ProfileLoginButton(self, profile[0])
            button.clicked.connect(lambda ch, name=profile[0], password=profile[1]:
                                   self.show_login_profile_popup(name, password))
            self.profile_buttons.append(button)
            self.__layout.addWidget(button)

        self.__initUI()

    def show_login_profile_popup(self, name, password):
        self.popup = ProfileLoginPopup(self, name, password)

    def show_create_profile_popup(self):
        self.popup = ProfileCreatePopup(self)

    def create_profile(self, name, password):
        if self.parent().create_profile(name, password):
            self.onCreate.emit(name)
            return True
        else:
            return False

    def updateGeometry(self) -> None:
        self.create_button.updateGeometry()
        for buttons in self.profile_buttons:
            buttons.updateGeometry()
        if self.popup is not None:
            self.popup.updateGeometry()


class MainUI(QWidget, GUIFormatter):
    onLogout = pyqtSignal()

    noteOpened = pyqtSignal(str)
    noteFavorited = pyqtSignal(str, bool)
    noteDeleted = pyqtSignal(str)
    noteCreated = pyqtSignal()

    def __init__(self, parent: QStackedWidget):
        super().__init__(parent)

        self.__favorites = QHBoxLayout()
        self.__favorites.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.__notes = QHBoxLayout()
        self.__notes.setAlignment(Qt.AlignTop | Qt.AlignLeft)

    def __str__(self):
        return 'main'

    def __initUI(self):
        favorites = QLabel('FAVORITES')
        notes = QLabel('NOTES')

        self.__menuBar = QMenuBar(self)
        profileMenu = self.__menuBar.addMenu('Profile')
        logoutAction = QAction('Logout', self)
        logoutAction.triggered.connect(lambda: self.onLogout.emit())
        profileMenu.addAction(logoutAction)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addWidget(self.__menuBar)
        layout.addWidget(favorites)
        layout.addLayout(self.__favorites)
        layout.addWidget(notes)
        layout.addLayout(self.__notes)
        self.__menuBar.move(0, 0)

        self.setLayout(layout)

    def reloadUI(self):
        self.__notes = super().clearAllWidgets(self.__notes)
        self.__favorites = super().clearAllWidgets(self.__favorites)

        profile = self.parent().getProfile()
        profile.reload()
        notes = profile.get_notes()
        for note in notes:
            if note[3]:
                self.__favorites.addWidget(OpenNoteButton(self, note[0], note[3]))
            else:
                self.__notes.addWidget(OpenNoteButton(self, note[0], note[3]))
        self.__notes.addWidget(CreateNoteButton(self))

        if self.__favorites.count() == 0:
            self.__favorites.addWidget(QLabel('Press right click on the note that you want to add as favorite.'))

        self.__initUI()


class NoteUI(QWidget):
    noteExited = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.__titleBox = QLineEdit('', self)
        self.__titleBox.setPlaceholderText('Title')
        self.__favoriteButton = QPushButton('')
        self.__favoriteButton.clicked.connect(self.__toggleFavorite)
        self.__contentBox = QTextEdit('', self)
        self.__contentBox.setPlaceholderText('Content')
        self.__favorite = None
        self.__date = None
        self.__title = None
        self.__content = None

        self.__initUI()

    def __str__(self):
        return 'note'

    def __initUI(self):
        back_button = QPushButton('<-')
        back_button.clicked.connect(self.returnEvent)
        save_button = QPushButton('save')
        save_button.clicked.connect(self.__saveButton)
        if self.__favorite:
            self.__favoriteButton.setText('added as favorite')
        else:
            self.__favoriteButton.setText('add as favorite')
        layout1 = QHBoxLayout()
        layout1.addWidget(back_button)
        layout1.addWidget(self.__titleBox)
        layout1.addWidget(self.__favoriteButton)
        layout1.addWidget(save_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout1, 0)
        main_layout.addWidget(self.__contentBox)

        self.setLayout(main_layout)

    def reloadUI(self):
        self.__titleBox.setText(self.__title)
        self.__contentBox.setText(self.__content)

        if self.__favorite:
            self.__favoriteButton.setText('added as favorite')
        else:
            self.__favoriteButton.setText('add as favorite')

    def __toggleFavorite(self):
        if not self.__getFavoriteButtonValue():
            self.__favoriteButton.setText('added as favorite')
        else:
            self.__favoriteButton.setText('add as favorite')

    def __getFavoriteButtonValue(self):
        if self.__favoriteButton.text() == 'added as favorite':
            return True
        else:
            return False

    def __showExitPopup(self, title):
        if self.__content != self.__contentBox.toPlainText() or self.__title != self.__titleBox.text() or \
                self.__favorite != self.__getFavoriteButtonValue():
            saveMessageBox = QMessageBox()
            saveMessageBox.setWindowTitle(title)
            saveMessageBox.setText('Do you want to save your progress?')
            saveMessageBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            return saveMessageBox.exec_()
        else:
            return QMessageBox.No

    def __showSaveErrorPopup(self):
        errorMessageBox = QMessageBox()
        errorMessageBox.setWindowTitle('Failed saving ' + self.__title)
        errorMessageBox.setText('Title already exists.')
        errorMessageBox.setIcon(QMessageBox.Critical)
        errorMessageBox.exec_()

    def __saveButton(self):
        if not self.save():
            self.__showSaveErrorPopup()
        else:
            self.setNote(self.__titleBox.text())

    def save(self):
        return self.parent().getProfile().update_note(self.__title, self.__date, self.__titleBox.text(),
                                                      self.__contentBox.toPlainText(), self.__getFavoriteButtonValue())

    def setNote(self, title):
        profile = self.parent().getProfile()
        note = profile.read_note(title)
        self.__title = note[0]
        self.__content = note[1]
        self.__date = note[2]
        self.__favorite = note[3]

        self.reloadUI()

    def returnEvent(self):
        retval = self.__showExitPopup('Go Back')

        if retval == QMessageBox.Yes:
            if self.save():
                self.noteExited.emit()
            else:
                self.__showSaveErrorPopup()
        elif retval == QMessageBox.No:
            self.noteExited.emit()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        retval = self.__showExitPopup('Exit')

        if retval == QMessageBox.Yes:
            if self.save():
                a0.accept()
            else:
                self.__showSaveErrorPopup()
        elif retval == QMessageBox.No:
            a0.accept()
        else:
            a0.ignore()
