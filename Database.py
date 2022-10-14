import sqlite3
from time import time

CREATE_PROFILES_TABLE = \
    '''CREATE TABLE IF NOT EXISTS Profiles(Name TEXT, Password TEXT, Icon TEXT, Date INT, PRIMARY KEY(Name))'''
CREATE_NOTES_TABLE = \
    '''CREATE TABLE IF NOT EXISTS Notes(Title TEXT, Content TEXT, Favorite BOOLEAN, Date INT, Name TEXT)'''

CREATE_PROFILE = \
    '''INSERT INTO Profiles(Name, Password, Icon, Date) VALUES (:name, :password, NULL, :date)'''
READ_PROFILE = \
    '''SELECT * FROM Profiles WHERE Name=:name'''
UPDATE_PROFILE = ''''''
DELETE_PROFILE = ''''''
READ_PROFILES = \
    '''SELECT * FROM Profiles'''

CREATE_NOTE = \
    '''INSERT INTO Notes (Title, Content, Date, Name, Favorite) VALUES (:title, :content, :date, :name, :favorite);'''
READ_NOTE = \
    '''SELECT Title, Content, Date, Favorite FROM Notes WHERE Title=:title AND Name=:name'''
UPDATE_NOTE = \
    '''UPDATE Notes SET Title =:newTitle, Content =:content, Favorite =:favorite WHERE Title =:oldTitle AND Date =:date
       AND Name =:name;'''
DELETE_NOTE = \
    '''DELETE FROM Notes WHERE Title =:title AND Name =:name;'''
READ_NOTES = \
    '''SELECT Title, Content, Date, Favorite FROM Notes WHERE Name=:name ORDER BY Date'''


class Profile:
    def __init__(self, database):
        self.__database = database
        self.__name = None
        self.__password = None
        self.__date_created = None
        self.__notes = []

    def get_name(self):
        return self.__name

    def init(self, name, password, date_created):
        self.__name = name
        self.__password = password
        self.__date_created = date_created

    def reload(self):
        self.__notes = self.__database.read_notes(self.__name)

    def get_notes(self):
        return self.__notes

    def create_note(self):
        flag = True
        i = 1
        while flag:
            title = 'Note' + str(i)
            flag = not self.__database.create_note(self.__name, title)
            i += 1

    def read_note(self, title):
        return self.__database.read_note(title, self.__name)

    def update_note(self, oldTitle, date, newTitle, content, favorite):
        return self.__database.update_note(self.__name, oldTitle, newTitle, content, favorite, date)

    def delete_note(self, title):
        self.__database.delete_note(title, self.__name)


class Database:
    def __init__(self):
        super().__init__()
        self.connection = sqlite3.connect('Notes.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute(CREATE_PROFILES_TABLE)
        self.cursor.execute(CREATE_NOTES_TABLE)
        self.connection.commit()

    def get_profiles(self):
        return self.cursor.execute(READ_PROFILES)

    def read_profile(self, name):
        self.cursor.execute(READ_PROFILE, {'name': name})
        data = self.cursor.fetchone()

        return data

    def create_profile(self, name, password):
        self.cursor.execute(READ_PROFILE, {'name': name})
        data = self.cursor.fetchone()

        if data is None:
            self.cursor.execute(CREATE_PROFILE, {'name': name, 'password': password, 'date': int(time())})
            self.connection.commit()
            return True
        else:
            return False

    def create_note(self, name, title):
        self.cursor.execute(READ_NOTE, {'title': title, 'name': name})
        data = self.cursor.fetchone()

        if data is None:
            self.cursor.execute(CREATE_NOTE,
                                {
                                    'title': title,
                                    'content': '',
                                    'date': time(),
                                    'name': name,
                                    'favorite': False
                                })
            self.connection.commit()
            return True
        else:
            return False

    def read_note(self, title, name):
        self.cursor.execute(READ_NOTE,
                            {'title': title, 'name': name})
        return self.cursor.fetchone()

    def read_notes(self, name):
        self.cursor.execute(READ_NOTES,
                            {'name': name})
        return self.cursor.fetchall()

    def delete_note(self, title, name):
        self.cursor.execute(DELETE_NOTE,
                            {'title': title, 'name': name})
        self.connection.commit()

    def update_note(self, name, oldTitle, newTitle, content, favorite, date):
        self.cursor.execute(READ_NOTE, {'title': newTitle, 'name': name})
        data = self.cursor.fetchall()
        alreadyExist = False
        for note in data:
            if note[2] != date:
                alreadyExist = True

        if alreadyExist:
            return False
        else:
            self.cursor.execute(UPDATE_NOTE,
                                {
                                    'newTitle': newTitle,
                                    'content': content,
                                    'favorite': favorite,
                                    'oldTitle': oldTitle,
                                    'date': date,
                                    'name': name
                                })
            self.connection.commit()
            return True

    def closeDB(self):
        self.connection.commit()
        self.connection.close()
