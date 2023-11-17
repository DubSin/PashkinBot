import sqlite3


class BotDB:
    def __init__(self, db):
        self.db = sqlite3.connect(db)
        self.cursor = self.db.cursor()

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

