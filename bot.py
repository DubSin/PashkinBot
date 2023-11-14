from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram import Dispatcher, Bot, executor, types
import logging
from keys import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)


class MachineStatementsGroup(StatesGroup):
    name = State()
    age = State()
    phone = State()


@dp.message_handler(commands=['start'])
async def start_menu(message: types.Message):
    await message.answer(f'Привет {message.from_user.username}')
    await message.answer('Это меню. Вот список функций данного бота: \n'
                         '/addclient - добавление нового клиента \n'
                         '/addorder - добавляние нового заказа к клиенту \n'
                         '/clientinfo - поиск информации клиента и его заказов')


@dp.message_handler(commands=['addclient'])
async def add_client(message: types.Message):
    await message.answer('Как зовут клиента: ')
    await MachineStatementsGroup.name.set()


@dp.message_handler(state=MachineStatementsGroup.name)
async def add_name_to_client(message: types.Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer("Отлично! Теперь введите его возраст:")
    await MachineStatementsGroup.next()


@dp.message_handler(state=MachineStatementsGroup.age)
async def add_age_to_client(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("Отлично! Теперь введите его номер телефона:")
    await MachineStatementsGroup.next()


@dp.message_handler(state=MachineStatementsGroup.phone)
async def add_age_to_client(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    data = await state.get_data()
    await message.answer(f"Имя: {data['username']}\n"
                         f"Возраст: {data['age']}\n"
                         f"Номер телефона: {data['phone']}")
    await state.finish()

if '__main__' == __name__:
    executor.start_polling(dp, skip_updates=True)