from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram import Dispatcher, Bot, executor, types
import logging
from keys import BOT_TOKEN
from db import BotDB
import datetime

bot = Bot(token=BOT_TOKEN, proxy='http://proxy.server:3128')
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)
bot_db = BotDB('users.db')

async def add_orders(message: types.Message):

    phone = message.text


    cursor.execute("SELECT * FROM activity_orders WHERE phone=?", (phone,))
    client = cursor.fetchone()


    if client:
        orders = client[2] + ', ' + message.text
        cursor.execute("UPDATE activity_orders SET orders=? WHERE phone=?", (orders, phone))
        conn.commit()
        await message.answer(f"Заказ успешно добавлен для клиента с номером телефона {phone}")
    else:
        await message.answer("Клиент с таким номером телефона не найден")
class MSG_Add(StatesGroup):
    name = State()
    phone = State()


class MSG_Find(StatesGroup):
    phone = State()


class EnterState(StatesGroup):
    password = State()


@dp.message_handler(commands=['start'])
async def start_menu(message: types.Message):
    await message.answer('Введите пароль:')
    await EnterState.password.set()


@dp.message_handler(state=EnterState.password)
async def password(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    dat = await state.get_data()
    if dat['password'] == "Пашка Лох":
        await message.answer(f'Саламчикс {message.from_user.username}')
        await message.answer('Это меню. Вот список функций данного бота: \n'
                             '/addclient - добавление нового клиента \n'
                             '/addorder - добавляние нового заказа к клиенту \n'
                             '/clientinfo - поиск информации клиента и его заказов')
        await state.finish()
    else:
        await message.answer("Пароль неверный, попробуйте еще раз")


@dp.message_handler(commands=['addclient'])
async def add_client(message: types.Message):
    await message.answer('Как зовут клиента: ')
    await MSG_Add.name.set()

#@dp.message_handler(commands=['addorder'])
#async def process_add_orders_command(message: types.Message):
    #await add_orders(message)
    #await message.answer("Заказ добавлен")
@dp.message_handler(commands=['process_order'])
async def process_order(message: types.Message):
    user_id = message.chat.id
    command = message.get_args()

    if command == 'tomorrow':
        # отложить выполнение действий до завтра
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        cursor.execute("UPDATE active_orders SET process_date = ? WHERE user_id = ?", (tomorrow, user_id))
        conn.commit()
        await message.answer("Уведомление будет отправлено завтра")
    elif command == 'close_order':
        # переписать содержимое ячейки orders из таблицы activity_orders в таблицу closed_orders и удалить его из activity_orders
        # ваш код для выполнения SQL запросов к базе данных
        await message.answer("Заказ успешно закрыт")


@dp.message_handler(state=MSG_Add.name)
async def add_name_to_client(message: types.Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer("Отлично! Теперь введите его номер телефона:")
    await MSG_Add.next()


@dp.message_handler(state=MSG_Add.phone)
async def add_age_to_client(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    data = await state.get_data()
    if not bot_db.user_exists(data['phone']):
        bot_db.add_user(data['username'], data['phone'])
        await message.answer(f"Имя: {data['username']}\n"
                             f"Номер телефона: {data['phone']}")
    else:
        await message.answer('Данный хуй уже присутсутвиет ясно нахуй!!!!')
    await state.finish()


@dp.message_handler(commands=['clientinfo'])
async def find_client(message: types.Message):
    await message.answer('Номер телефона клиента: ')
    await MSG_Find.phone.set()


@dp.message_handler(state=MSG_Find.phone)
async def find_user_by_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    data = await state.get_data()
    user = bot_db.find_user(data['phone'])
    if user:
        await message.answer(f"Имя: {user[1]}\n"
                             f"Номер телефона: {user[2]}\n"
                             f"Дата подключения: {user[3]}\n")
    else:
        await message.answer('Клиент не найден')
    await state.finish()


if '__main__' == __name__:
    executor.start_polling(dp, skip_updates=True)


