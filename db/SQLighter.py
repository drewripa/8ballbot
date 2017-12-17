import sqlite3
import os.path

class SQLighter:

    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "8ball.db")
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()

    def user_init(self, userid):
        with self.connection:
            self.cursor.execute('INSERT INTO users VALUES (?, 0, 0, 0, 0)', (userid,))

    def select_userdata(self, userid):
        with self.connection:
            return self.cursor.execute('SELECT * FROM users WHERE userid = ?', (userid,)).fetchall()[0]

    def write_userdata(self, userid, counter, yes, no, mb):
        with self.connection:
            self.cursor.execute('UPDATE users '
                                'SET counter = ?, stats_yes = ?, stats_no = ?, stats_mb = ? '
                                'WHERE userid = ?', (counter, yes, no, mb, userid)).fetchall()

    def close(self):
        self.connection.close()