
import logging

from utils.database import TasksManager

from aiogram import executor

logging.basicConfig(level=logging.INFO)

db = TasksManager('db.sqlite3')
backup_db = TasksManager('backup_db.sqlite3')
async def on_shutdown(_):
    all_tasks = db.get_tasks(with_datetime=True)
    backup_db.delete_all_data()
    for task in all_tasks:
        splitted_task = task.split()
        task_time = f"{splitted_task[-2]} {splitted_task[-1]}"
        country = []
            
            
            
        for word in splitted_task[2:]:
            if word == "в":
                break
            else:
                if word != '':
                    country.append(word)
               
        target_country = " ".join(country)
        channel_id = splitted_task[-3]
        task_name = f"Постинг в {target_country} в канал {channel_id}"
        backup_db.create_task(task_name, task_time)

    db.delete_all_data()


def main():
    from handlers import dp
    executor.start_polling(
        dp, skip_updates=True, on_shutdown=on_shutdown
        )
    
if __name__ == "__main__":
    main()
  