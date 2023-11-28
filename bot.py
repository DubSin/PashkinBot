from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.callback_data import CallbackData
from aiogram import Dispatcher, Bot, executor, types
from datetime import datetime
import asyncio
import logging
from keys import BOT_TOKEN
from db import BotDB

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)
bot_db = BotDB('users.db')


def orders_markup(phone, orders, deadline):
    order_data = CallbackData('state', 'phone', 'orders', 'deadline')
    inline_btn_post = InlineKeyboardButton('Перенести', callback_data=order_data.new(
        state='post',
        phone=phone,
        orders=orders,
        deadline=deadline
    ))
    inline_btn_accept = InlineKeyboardButton('Принять', callback_data=order_data.new(
        state='accept',
        phone=phone,
        orders=orders,
        deadline=deadline
    ))
    inline_kb = InlineKeyboardMarkup().add(inline_btn_post).add(inline_btn_accept)
    return inline_kb


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


def converting_to_date(info):
    try:
        date, time = info.split()
        dt = [int(i) for i in date.split('-')]
        tm = [int(i) for i in time.split(':')]
        if len(tm) == 0:
            result = datetime(dt[0], dt[1], dt[2])
        if len(tm) == 1:
            result = datetime(dt[0], dt[1], dt[2], tm[0])
        if len(tm) == 2:
            result = datetime(dt[0], dt[1], dt[2], tm[0], tm[1])
        if len(tm) == 3:
            result = datetime(dt[0], dt[1], dt[2], tm[0], tm[1], tm[2])
        return result
    except Exception as e:
        print(e)
        return None


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
        editor_exist = bot_db.editor_exists(message.from_user.id)
        if not editor_exist:
            bot_db.add_editor(message.from_user.id)
        await message.answer('Это меню. Вот список функций данного бота: \n'
                             '/addclient - добавление нового клиента \n'
                             '/addorder - добавляние нового заказа к клиенту \n'
                             '/clientinfo - поиск информации клиента и его заказов\n'
                             '/findcloseorder - поиск ближайших заказов\n')
        await state.finish()
    else:
        await message.answer("Пароль неверный, попробуйте еще раз")


@dp.message_handler(commands=['findcloseorder'])
async def add_client(message: types.Message):
    if bot_db.editor_exists(message.from_user.id):
        close_orders = bot_db.get_close_orders()
        for orders in close_orders:
            inline_markup = orders_markup(orders[1], orders[2], orders[3])
            await message.answer(f'phone: {orders[1]}\n'
                                 f'description: {orders[2]}\n'
                                 f'deadline: {orders[3]}', reply_markup=inline_markup)
    else:
        await message.answer('У вас нет доступа')


async def notifications(time):
    while True:
        editors = bot_db.get_editors()
        for editor in editors:
            orders = bot_db.get_close_orders(one_time=True)
            inline_markup = orders_markup(orders[1], orders[2], orders[3])
            await bot.send_message(editor[0], f'phone: {orders[1]}\n'
                                              f'description: {orders[2]}\n'
                                              f'deadline: {orders[3]}', reply_markup=inline_markup)
        await asyncio.sleep(time)


@dp.callback_query_handler(lambda c: c.data.state == 'accept')
async def process_callback_button1(callback_query: CallbackQuery, callback_data: dict):
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_reply_markup(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=None)
    await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text=callback_query.message.text + '\n Заказ принят'
                                )
    phone = callback_data.get('phone')
    deadline = callback_data.get('deadline')

    bot_db.update_deadline(phone, deadline)


@dp.callback_query_handler(lambda c: c.data.state == 'post')
async def process_callback_button1(callback_query: CallbackQuery, callback_data: dict):
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_reply_markup(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=None)
    await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text=callback_query.message.text + '\n Заказ перенесен на 1 день'
    )


@dp.message_handler(commands=['addclient'])
async def add_client(message: types.Message):
    if bot_db.editor_exists(message.from_user.id):
        await message.answer('Как зовут клиента: ')
        await MSG_Add.name.set()
    else:
        await message.answer('У вас нет доступа')


@dp.message_handler(commands=['addorder'])
async def add_client(message: types.Message):
    if bot_db.editor_exists(message.from_user.id):
        await message.answer('Введите номер телефона клиента: ')
        await MSG_Order.phone.set()
    else:
        await message.answer('У вас нет доступа')


@dp.message_handler(state=MSG_Order.phone)
async def add_name_to_client(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    if bot_db.user_exists(message.text):
        await message.answer("Отлично! Теперь введите заказ клиента:")
        await MSG_Order.next()
    else:
        await message.answer('Такого пользователя не существует')
        await state.finish()


@dp.message_handler(state=MSG_Order.order)
async def add_name_to_client(message: types.Message, state: FSMContext):
    await state.update_data(order=message.text)
    await message.answer("Теперь введите дедлайн заказа(если хотите оставить по умолчанию введите 0)\n"
                         "Формат ввода дедлайна: год-месяц-день час")
    await message.answer("Год: вводить целую дату (2020, 2021, 2022)\n"
                         "Месяц, день и час: вводить 2 цифрами (01, 02, 03, ... , 11, 12)")
    await MSG_Order.next()


@dp.message_handler(state=MSG_Order.deadline)
async def add_name_to_client(message: types.Message, state: FSMContext):
    await state.update_data(deadline=message.text)
    data = await state.get_data()
    if data['deadline'] == '0':
        bot_db.add_order(data['phone'], data['order'])
        await message.answer('Данные введены')
    else:
        deadline = converting_to_date(data['deadline'])
        if deadline:
            bot_db.add_order(data['phone'], data['order'], deadline.strftime("%Y-%m-%d %H:%M:%S"))
            await message.answer('Данные введены')
        else:
            await message.answer('Данные введены некорректно')

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
        await message.answer('Данный хуй уже присутсутвиет ясно нахуй!!!!(или номер телефона)')
    await state.finish()


@dp.message_handler(commands=['clientinfo'])
async def find_client(message: types.Message):
    if bot_db.editor_exists(message.from_user.id):
        await message.answer('Номер телефона клиента: ')
        await MSG_Find.phone.set()
    else:
        await message.answer('У вас нет доступа')


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
        await message.answer('Клиент не найден нахуй!!!!!!!')
    await state.finish()


if '__main__' == __name__:
    loop = asyncio.get_event_loop()
    loop.create_task(notifications(1000000))
    executor.start_polling(dp, skip_updates=True)
