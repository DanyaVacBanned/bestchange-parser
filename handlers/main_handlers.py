from aiogram import types


from app import dp, bc

from utils.nav import bot_navigation


@dp.message_handler(commands='start')
async def on_start(message: types.Message):
    # await message.answer('Добро пожаловать!', reply_markup=bot_navigation.start_keyboard())
    await message.answer(message.from_id)

@dp.message_handler(text='Посмотреть перечень валют💸')
async def check_values(message: types.Message):
    _, values_names= bc.sort_value_names()
    response = list()
    for value in values_names:
        response.append(value[0])
    await message.answer('\n'.join(response))



