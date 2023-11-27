import sqlite3
from datetime import datetime, timedelta


class BotDB:
    def __init__(self, db):
        self.db = sqlite3.connect(db)
        self.cursor = self.db.cursor()

    def add_editor(self, editor_id):
        self.cursor.execute("INSERT INTO 'editors' ('editor_id') VALUES (?)", (editor_id, ))
        return self.db.commit()

    def get_close_orders(self):
        ans = self.cursor.execute("SELECT * FROM 'activity_orders'").fetchall()
        now = datetime.today()
        result = []
        for i in ans:
            try:
                if datetime.strptime(i[3], '%Y-%m-%d %H:%M:%S') - now < timedelta(days=2):
                    result.append(i)
            except ValueError:
                pass
        return result

    def get_editors(self):
        result = self.cursor.execute("SELECT `editor_id` from `editors`")
        return result.fetchall()

    def add_user(self, name, phone):
        self.cursor.execute("INSERT INTO 'users' ('name', 'phone') VALUES (?, ?)", (name, phone))
        return self.db.commit()

    def user_exists(self, phone):
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `phone` = ?", (phone,))
        return bool(len(result.fetchall()))

    def find_user(self, phone):
        result = self.cursor.execute("SELECT * FROM `users` WHERE `phone` = ?", (phone, ))
        return result.fetchone()

    def add_order(self, phone, order, deadline=False):
        if deadline:
            self.cursor.execute("INSERT INTO 'activity_orders' ('phone', 'orders', 'deadline') VALUES (?, ?, ?)",
                                (phone, order, deadline))
        else:
            self.cursor.execute("INSERT INTO 'activity_orders' ('phone', 'orders') VALUES (?, ?)", (phone, order))
        return self.db.commit()

