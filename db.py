import sqlite3
from datetime import datetime, timedelta


class BotDB:
    def __init__(self, db):
        self.db = sqlite3.connect(db)
        self.cursor = self.db.cursor()

    def add_editor(self, editor_id):
        self.cursor.execute("INSERT INTO 'editors' ('editor_id') VALUES (?)", (editor_id, ))
        return self.db.commit()

    def editor_exists(self, editor_id):
        result = self.cursor.execute("SELECT `id` FROM `editors` WHERE `editor_id` = ?", (editor_id,))
        return bool(len(result.fetchall()))

    def get_close_orders(self, one_time=False):
        orders = self.cursor.execute("SELECT * FROM 'activity_orders'").fetchall()
        now = datetime.today()
        result = []
        way = []
        if orders:
            for i in orders:
                try:
                    deadline = i[3].replace(':', '/')
                    if datetime.strptime(i[3], '%Y-%m-%d %H:%M:%S') - now < timedelta(days=2):
                        result.append([*i[:-1], deadline])
                        way.append([*i, datetime.strptime(i[3], '%Y-%m-%d %H:%M:%S') - now])
                except ValueError:
                    pass
            if one_time:
                result = min(way, key=lambda x: x[4])
            return result

    def get_editors(self):
        result = self.cursor.execute("SELECT `editor_id` from `editors`")
        return result.fetchall()

    def from_activity_to_closed(self, phone, orders, deadline):
        self.cursor.execute("INSERT INTO `closed_orders` (`phone`, `orders`) VALUES (?, ?)", (phone, orders))
        self.cursor.execute("DELETE FROM `activity_orders` WHERE `phone` = ? AND `orders` = ? AND `deadline` = ?",
                            (phone, orders, deadline))
        return self.db.commit()

    def update_deadline(self, phone, deadline):
        deadline = deadline.replace(',', ':')
        self.cursor.execute("UPDATE `activity_orders` SET `deadline` = ? WHERE `phone` = ?",
                            (datetime.strptime(deadline, '%Y-%m-%d %H:%M:%S') + timedelta(days=1), phone))
        return self.db.commit()

    def add_user(self, name, phone):
        self.cursor.execute("INSERT INTO 'users' ('name', 'phone') VALUES (?, ?)", (name, phone))
        return self.db.commit()

    def user_exists(self, phone):
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `phone` = ?", (phone,))
        return bool(len(result.fetchall()))

    def find_user(self, phone):
        result = self.cursor.execute("SELECT * FROM `users` WHERE `phone` = ?", (phone, ))
        return result.fetchone()

    def users_closed_orders(self, phone):
        result = self.cursor.execute("SELECT * FROM `closed_orders` WHERE `phone` = ?", (phone, ))
        return result.fetchall()

    def add_order(self, phone, order, deadline=False):
        if deadline:
            self.cursor.execute("INSERT INTO 'activity_orders' ('phone', 'orders', 'deadline') VALUES (?, ?, ?)",
                                (phone, order, deadline))
        else:
            self.cursor.execute("INSERT INTO 'activity_orders' ('phone', 'orders') VALUES (?, ?)", (phone, order))
        return self.db.commit()

