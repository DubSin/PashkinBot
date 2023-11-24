import sqlite3

conn = sqlite3.connect('orders.db')
cursor = conn.cursor()
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

    async def send_notification(self, user_id,  message):
        await bot.send_message(user_id, message)

    async def track_orders(self):
        while True:
            current_date = datetime.date.today()
            three_days_ago = current_date - datetime.timedelta(days=3)
            cursor.execute("SELECT user_phone, order_id FROM active_orders WHERE order_date = ?", (three_days_ago,))
            orders = cursor.fetchall()
            for order in orders:
                user_id, order_id = order
                message = f"Пожалуйста, отдайте заказ {order_id}"
                await send_notification(user_id, message)
            await asyncio.sleep(86400)
    def find_user(self, phone):
        result = self.cursor.execute("SELECT * FROM `users` WHERE `phone` = ?", (phone, ))
        return result.fetchone()

    async def on_startup(_):
        asyncio.create_task(track_orders())

    #def add_order(self, phone):
        #current_date = datetime.datetime.now().date()
        #cursor.execute("INSERT INTO active_orders (user_id, order_date) VALUES (?, ?)", (phone, current_date))
        #conn.commit()


        return self.db.commit()

