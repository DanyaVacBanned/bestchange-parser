from aiogram.types import ReplyKeyboardMarkup, KeyboardButton



class BotNav:
    def start_keyboard(self):
        return ReplyKeyboardMarkup(
            resize_keyboard=True
            ).add(KeyboardButton('Получить информацию по курсу обмена💵'))

    def admin_keyboard(self):
        return ReplyKeyboardMarkup(
            resize_keyboard=True
            ).add(
            KeyboardButton('Запустить постинг🖨')
            ).add(
            KeyboardButton("Остановить постинг")
            )

    def back_to_menu(self):
        return ReplyKeyboardMarkup(
            resize_keyboard=True
            ).add(
            KeyboardButton("Вернуться в меню")
            )
            

    def confirmation_keyboard(self):
        return ReplyKeyboardMarkup(
            resize_keyboard=True
            ).add(KeyboardButton('Да')).add(KeyboardButton('Нет'))
 
    def value_type(self):
        return ReplyKeyboardMarkup(
            resize_keyboard=True
            ).add(
            KeyboardButton(text='Криптовалюта')
            ).add(
            KeyboardButton(text='Рубли')
            ).add(
            KeyboardButton(text="Валюта")
            ).add(
            KeyboardButton(text="Вернуться в меню")
            )
    
    def card_or_cash(self):
        return ReplyKeyboardMarkup(
            resize_keyboard=True
            ).add(
            KeyboardButton('Карта💳')
            ).add(
            KeyboardButton("Наличные💵")
            )
    
    def crypto_or_other(self):
        return ReplyKeyboardMarkup(
            resize_keyboard=True
            ).add(
            KeyboardButton(text='В валюте')
            ).add(
            KeyboardButton(text='В криптовалюте')
            )
    
    def multiply_keyboard(self, preset_names: list):
        mult_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for btn in preset_names:
            mult_keyboard.add(KeyboardButton(text=btn))
        return mult_keyboard.add(KeyboardButton('Вернуться в меню'))
    
    def one_or_all_countries(self):
        return ReplyKeyboardMarkup(
            resize_keyboard=True
            ).add(
            KeyboardButton('Все страны📚')
            ).add(
            KeyboardButton('Одна конкретная страна📕')
            ).add(
            KeyboardButton('Вернуться в меню')
            )


bot_navigation = BotNav()