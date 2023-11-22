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

        # функция для добавления заказа в таблицу active_orders
    def add_order(self, phone):
        current_date = datetime.datetime.now().date()
        cursor.execute("INSERT INTO active_orders (user_id, order_date) VALUES (?, ?)", (phone, current_date))
        conn.commit()

    async def send_notification(self):
        three_days_ago = datetime.datetime.now().date() - datetime.timedelta(days=3)
        cursor.execute("SELECT user_id FROM active_orders WHERE order_date < ?", (three_days_ago,))
        users = cursor.fetchall()
        for user in users:
            await bot.send_message(user[0], "Необходимо отдать заказ!")

        return self.db.commit()
