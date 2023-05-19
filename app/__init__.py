from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config.auth import token

from app.webr import BestchangeUserAction

storage = MemoryStorage()
bot = Bot(token)
dp = Dispatcher(bot, storage=storage)
bc = BestchangeUserAction()
