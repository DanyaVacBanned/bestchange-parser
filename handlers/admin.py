import asyncio

from datetime import datetime

from aiogram import types
from aiogram.dispatcher.storage import FSMContext

from utils.fsm import BotStart, StopPosing
from utils import shortcuts
from utils.database import TasksManager

from app import dp, bot
from app.webr import BestchangeUserAction

from utils.nav import bot_navigation

from config.auth import admin_id, developer_id, second_admin_id
from config.exhandler import logs_writer

best_change = BestchangeUserAction()
db = TasksManager('db.sqlite3')

@dp.message_handler(commands='admin')
async def admin_panel(message: types.Message):
    if message.chat.id in [admin_id, developer_id, second_admin_id]:
        await message.answer(
            """
            Добро пожаловать в админскую паннель, вывожу клавиатуру
            """, reply_markup=bot_navigation.admin_keyboard()
            )
    else:
        await message.answer('Вы не являетесь администратором')
    
@dp.message_handler(text='Запустить постинг🖨')
async def start_posting(message: types.Message, state=FSMContext):
    if message.chat.id in [admin_id, developer_id, second_admin_id]:
        if message.text != "Вернуться в меню":
            await message.answer(
                """
                Введите id канала, в который хотите запустить постинг
                """, reply_markup=bot_navigation.back_to_menu()
                )
            await BotStart.CHANNEL_ID.set()
        else:
            await state.finish()
            await message.answer("Возвращаюсь в меню", reply_markup=bot_navigation.start_keyboard())

    else:
        await message.answer('Вы не являетесь администратором')

@dp.message_handler(state=BotStart.CHANNEL_ID)
async def get_channel_id(message: types.Message, state=FSMContext):
    try:
        channel_id = int(message.text.strip())
        async with state.proxy() as sp:
            sp['channel_id'] = channel_id
        await message.answer('Канал успешно выбран')
        # await message.answer(f'Запустить постинг в канал с id {channel_id}?', reply_markup=bot_navigation.confirmation_keyboard())
        await message.answer('Постинг для одной страны или для всех?', reply_markup=bot_navigation.one_or_all_countries())

        await BotStart.COUNTRIES_SELECTION.set()
    except ValueError as ex:
        logs_writer(ex)
        await message.answer(
            """
            Некорекктно введено ID канала! Попробуйте снова.
            """
            )
        await state.finish()


@dp.message_handler(state=BotStart.COUNTRIES_SELECTION)
async def country_selection_handler(message: types.Message, state=FSMContext):
    if message.text == "Все страны📚":
        async with state.proxy() as sp:
            channel_id = sp['channel_id']
        await message.answer(f'Запустить постинг в канал с id {channel_id}?', reply_markup=bot_navigation.confirmation_keyboard())
        await BotStart.GET_RESPONSE.set()
    elif message.text == "Одна конкретная страна📕":
        all_countries = shortcuts.get_keys_from_json('countries_and_cities')
        await message.answer('Выберите страну из перечня', reply_markup=bot_navigation.multiply_keyboard(all_countries))
        await BotStart.GET_COUNTRY.set()
    elif message.text == "Вернуться в меню":
        await state.finish()
        await message.answer("Возвращаюсь в меню", reply_markup=bot_navigation.start_keyboard())


@dp.message_handler(state=BotStart.GET_COUNTRY)
async def get_country(message: types.Message, state=FSMContext):
    if message.text != 'Вернуться в меню':
        country = message.text
        async with state.proxy() as sp:
            sp['target_country'] = country
            channel_id = sp['channel_id']
        await message.answer(f'Запустить постинг в канал с id {channel_id}?', reply_markup=bot_navigation.confirmation_keyboard())
        await BotStart.ONE_COUNTRY_GET_RESPONSE.set()
    else:
        await state.finish()
        await message.answer("Возвращаюсь в меню", reply_markup=bot_navigation.start_keyboard())

@dp.message_handler(state=BotStart.ONE_COUNTRY_GET_RESPONSE)
async def one_country_get_response(message: types.Message, state=FSMContext):
    if message.text == 'Да':
        async with state.proxy() as sp:
            channel_id = sp['channel_id']
            target_country = sp['target_country']
        await state.finish()
        loop = asyncio.get_event_loop()
        await message.answer('Начинаю постинг', reply_markup=bot_navigation.start_keyboard())
        task_name = f"Постинг в {target_country} в канал {channel_id}"
        task_time = datetime.now()
        db.create_task(task_name, task_time)
        task = loop.create_task(best_change.get_rate_for_choosen_country(channel_id=channel_id, country=target_country, message=message, task_name=task_name))
        await task
    
    elif message.text == 'Нет':
        await message.answer(
            """
            Возвращаюсь в меню
            """, reply_markup=bot_navigation.admin_keyboard()
            )
        await state.finish()
        
@dp.message_handler(state=BotStart.GET_RESPONSE)
async def get_response(message: types.Message, state=FSMContext):
    if message.text == 'Да':
        async with state.proxy() as sp:
            channel_id = sp['channel_id']
        await state.finish()
        loop = asyncio.get_event_loop()
        await message.answer('Начинаю постинг', reply_markup=bot_navigation.start_keyboard())
        task_name = f'Постинг по всем странам в канал {channel_id}'
        task_time = datetime.now()
        db.create_task(task_name, task_time)
        task = loop.create_task(best_change.get_rate_for_post(channel_id, message, task_name=task_name))
        await task
        
    elif message.text == 'Нет':
        await message.answer(
            """
            Возвращаюсь в меню
            """, reply_markup=bot_navigation.admin_keyboard()
            )
        await state.finish()



@dp.message_handler(text='Остановить постинг')
async def stop_posting(message: types.Message):
    tasks_names = db.get_tasks()
    if tasks_names == []:
        await message.answer('На данный момент нет ни одного активного постинга')
    else:
        tasks_names_datetimes = db.get_tasks(with_datetime=True)
        await message.answer('\n'.join(tasks_names_datetimes))
        await message.answer('Выберите постинг, который вы хотите остановить', reply_markup=bot_navigation.multiply_keyboard(tasks_names))
        await StopPosing.POSTING_NAME.set()

@dp.message_handler(state=StopPosing.POSTING_NAME)
async def get_posting_name(message: types.Message, state=FSMContext):
    if message.text != "Вернуться в меню":
        try:
            task_name = message.text
            task_time = db.get_task_by_name(task_name)[1]
            db.delete_task_by_name(task_name)
            await message.answer(f'Постинг {task_name} от {task_time} успешно остановлен')
            await state.finish()
        except TypeError:
            await message.answer('Не обнаружено постинга с таким именем')

    else:
        await state.finish()
        await message.answer('Возвращаюсь в меню', reply_markup=bot_navigation.start_keyboard())