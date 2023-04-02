from aiogram.dispatcher.filters.state import State, StatesGroup

class GetActualRate(StatesGroup):
    COUNTRY_GIVE = State()
    CITY_GIVE = State() 
    COUNTRY_GET = State()
    CITY_GET = State()

    FROM_VALUE = State()
    TO_VALUE = State()

    CARD_OR_CASH = State()
    GET_VALUE_TYPE = State()
    GET_TO_VALUE_TYPE = State()

    CRYPTO = State()
    OTHER = State()

    COUNT = State()

    REQUEST = State()

class BotStart(StatesGroup):
    CHANNEL_ID = State()
    POSTING_CONFIRM = State()
    GET_RESPONSE = State()               