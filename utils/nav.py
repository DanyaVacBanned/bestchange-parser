from aiogram.types import ReplyKeyboardMarkup, KeyboardButton



class BotNav:
    def start_keyboard(self):
        return ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Получить информацию по курсу обмена💵')).add(KeyboardButton('Посмотреть перечень валют💸'))

    def admin_keyboard(self):
        return ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Запустить постинг🖨'))

    def confirmation_keyboard(self):
        return ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Да')).add(KeyboardButton('Нет'))
 


bot_navigation = BotNav()