import asyncio

from aiogram import types
from aiogram.dispatcher.storage import FSMContext

from utils.fsm import BotStart

from app import dp, bot
from app.webr import BestchangeUserAction

from utils.nav import bot_navigation

from config.auth import admin_id, developer_id
from config.exhandler import logs_writer

best_change = BestchangeUserAction()


@dp.message_handler(commands='admin')
async def admin_panel(message: types.Message):
    if message.chat.id == admin_id or message.chat.id == developer_id:
        await message.answer(
            """
            Добро пожаловать в админскую паннель, вывожу клавиатуру
            """, reply_markup=bot_navigation.admin_keyboard()
            )
    else:
        await message.answer('Вы не являетесь администратором')
    
@dp.message_handler(text='Запустить постинг🖨')
async def start_posting(message: types.Message):
    if message.chat.id == admin_id or message.chat.id == developer_id:
        await message.answer(
            """
            Введите id канала, в который хотите запустить постинг
            """
            )
        await BotStart.CHANNEL_ID.set()

    else:
        await message.answer('Вы не являетесь администратором')

@dp.message_handler(state=BotStart.CHANNEL_ID)
async def get_channel_id(message: types.Message, state=FSMContext):
    try:
        channel_id = int(message.text)
        async with state.proxy() as sp:
            sp['channel_id'] = channel_id
        await message.answer('Канал успешно выбран')
        await message.answer(f'Запустить постинг в канал с id {channel_id}?', reply_markup=bot_navigation.confirmation_keyboard())
        await BotStart.GET_RESPONSE.set()
    except ValueError as ex:
        logs_writer(ex)
        await message.answer(
            """
            Некорекктно введено ID канала! Попробуйте снова.
            """
            )
        await state.finish()



@dp.message_handler(state=BotStart.GET_RESPONSE)
async def get_response(message: types.Message, state=FSMContext):
    if message.text == 'Да':
        async with state.proxy() as sp:
            channel_id = sp['channel_id']
        await state.finish()
        loop = asyncio.get_event_loop()
        await message.answer('Начинаю парсинг', reply_markup=bot_navigation.start_keyboard())
        task = loop.create_task(best_change.get_rate_for_post(channel_id))
        await task
        
        
    elif message.text == 'Нет':
        await message.answer(
            """
            Возвращаюсь в меню
            """, reply_markup=bot_navigation.admin_keyboard()
            )
        await state.finish()

