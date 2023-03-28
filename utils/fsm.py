from aiogram.dispatcher.filters.state import State, StatesGroup

class GetActualRate(StatesGroup):
    VALUE = State()
    TO_VALUE = State()
    CITY = State()


class BotStart(StatesGroup):
    CHANNEL_ID = State()
    POSTING_CONFIRM = State()
    GET_RESPONSE = State()               