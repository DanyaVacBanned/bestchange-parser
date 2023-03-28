import logging

from aiogram import executor

logging.basicConfig(level=logging.INFO)

async def on_shutdown(_):
    pass


def main():
    from handlers import dp
    executor.start_polling(
        dp, skip_updates=True, on_shutdown=on_shutdown
        )
    
if __name__ == "__main__":
    main()