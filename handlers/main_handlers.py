import asyncio
from datetime import datetime

from aiogram import types


from app import BestchangeUserAction
from app import dp

from config.auth import developer_id, admin_id, second_admin_id

from utils.nav import bot_navigation
from utils.database import TasksManager


@dp.message_handler(commands='start')
async def on_start(message: types.Message):
    await message.answer('Добро пожаловать!', reply_markup=bot_navigation.start_keyboard())
    

@dp.message_handler(commands = 'retry')
async def debug_func(message: types.Message):
    if message.chat.id not in [admin_id, developer_id, second_admin_id]:
        await message.answer('У вас нет прав на использование этой команды')
    else:
        task_list = []
        tm = TasksManager('backup_db.sqlite3')
        all_tasks = tm.get_tasks()
        best_change = BestchangeUserAction()
        db = TasksManager('db.sqlite3')
        countries = []
        for single_task in all_tasks:
            country = []
            splitted_task = single_task.split()
            
            
            for word in splitted_task[2:]:
                if word == "в":
                    break
                else:
                    if word != '':
                        country.append(word)
               
            target_country = " ".join(country)

            print(target_country)

            channel_id = int(splitted_task[-1])
            if target_country not in countries:
                countries.append(target_country)
                loop = asyncio.get_event_loop()
                await message.answer('Начинаю постинг', reply_markup=bot_navigation.start_keyboard())
                task_name = f"Постинг в {target_country} в канал {channel_id}"
                task_time = datetime.now()
                db.create_task(task_name, task_time)
                task_list.append(loop.create_task(best_change.get_rate_for_choosen_country(channel_id=channel_id, country=target_country, message=message, task_name=task_name)))
        for task in task_list:
            await task