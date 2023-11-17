from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram import Dispatcher, Bot, executor, types
import logging
from keys import BOT_TOKEN
from db import BotDB
import maya

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)
bot_db = BotDB('users.db')


class MSG_Add(StatesGroup):
    name = State()
    phone = State()


class MSG_Find(StatesGroup):
    phone = State()


class EnterState(StatesGroup):
    password = State()


class MSG_Order(StatesGroup):
    phone = State()
    order = State()
    deadline = State()


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
                             '/clientinfo - поиск информации клиента и его заказов\n'
                             '/findcloseorder - поиск ближайших заказов')
        await state.finish()
    else:
        await message.answer("Пароль неверный, попробуйте еще раз")


@dp.message_handler(commands=['addclient'])
async def add_client(message: types.Message):
    await message.answer('Как зовут клиента: ')
    await MSG_Add.name.set()


@dp.message_handler(commands=['addorder'])
async def add_client(message: types.Message):
    await message.answer('Введите номер телефона клиента: ')
    await MSG_Order.phone.set()


@dp.message_handler(state=MSG_Order.phone)
async def add_name_to_client(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    if bot_db.user_exists(message.text):
        await message.answer("Отлично! Теперь введите заказ клиента:")
        await MSG_Order.next()
    else:
        await message.answer('Такого пользователя не существует')


@dp.message_handler(state=MSG_Order.order)
async def add_name_to_client(message: types.Message, state: FSMContext):
    await state.update_data(order=message.text)
    await message.answer("Теперь введите дедлайн заказа(если хотите оставить по умолчанию введите 0)\n"
                         "Формат ввода дедлайна: год-месяц-день часы:минуты")
    await MSG_Order.next()


@dp.message_handler(state=MSG_Order.deadline)
async def add_name_to_client(message: types.Message, state: FSMContext):
    await state.update_data(deadline=message.text)
    data = await state.get_data()
    if data['deadline'] == '0':
        bot_db.add_order(data['phone'], data['order'])
    else:
        bot_db.add_order(data['phone'], data['order'], data['deadline'])
    await message.answer('Данные введены')
    await state.finish()


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
