from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import asyncio
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from crud_functions import *

api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button1 = KeyboardButton(text='Рассчитать')
button2 = KeyboardButton(text='Информация')
button1_1 = KeyboardButton(text='Купить')
button2_1 = KeyboardButton(text='Регистрация')
kb.row(button1, button2)
kb.add(button1_1, button2_1)

kb2 = InlineKeyboardMarkup(resize_keyboard=True)
button3 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button4 = InlineKeyboardButton('Формулы расчёта', callback_data='formulas')
kb2.add(button3, button4)

kb3 = InlineKeyboardMarkup(resize_keyboard=True)
button5 = InlineKeyboardButton(text='Product1', callback_data='product_buying')
button6 = InlineKeyboardButton(text='Product2', callback_data='product_buying')
button7 = InlineKeyboardButton(text='Product3', callback_data='product_buying')
button8 = InlineKeyboardButton(text='Product4', callback_data='product_buying')
kb3.row(button5, button6, button7, button8)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = 1000


@dp.message_handler(text='Регистрация')
async def sing_up(message):
    await message.answer("Введите имя пользователя (только латинский алфавит):")
    await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    if is_included(message.text):
        await message.answer("Пользователь существует, введите другое имя")
        await RegistrationState.username.set()
    else:
        await state.update_data(first_0=message.text)
        await message.answer("Введите свой email:")
        await RegistrationState.email.set()


@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    await state.update_data(second_0=message.text)
    await message.answer("Введите свой возраст:")
    await RegistrationState.age.set()


@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    await state.update_data(third_0=message.text)
    data = await state.get_data()
    add_user(data['first_0'], data['second_0'], data['third_0'])
    await state.finish()
    await message.answer("Регистрация прошла успешно", reply_markup=kb)


@dp.message_handler(text='Купить')
async def get_buying_list(message):
    Products = get_all_products()
    for product in Products:
        id, title, description, price = product
        await message.answer(f'Название: {title} | Описание: {description} | Цена: {price}')
        with open(f'files/pic{id}.png', 'rb') as img:
            await message.answer_photo(img)
    await message.answer('Выберите продукт для покупки:', reply_markup=kb3)


@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer("Вы успешно приобрели продукт!")


@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=kb2)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer("https://www.calc.ru/Formula-Mifflinasan-Zheora.html")


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer("Введите свой возраст:")
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(first=message.text)
    await message.answer("Введите свой рост:")
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(second=message.text)
    await message.answer("Введите свой вес:")
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(third=message.text)
    data = await state.get_data()
    result = float(10 * float(data['third']) + 6.25 * float(data['second']) - 5 * float(data['first']) + 5)
    await message.answer(f'Ваша норма калорий {result}')
    state.finish()


@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.\n'
                         'Что бы узнать Вашу суточную норму калорий,'
                         'введите или выберете "Рассчитать"', reply_markup=kb)


@dp.message_handler()
async def all_massages(message):
    await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
