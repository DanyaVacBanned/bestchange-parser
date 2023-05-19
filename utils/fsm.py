from aiogram.dispatcher.filters.state import State, StatesGroup

class GetActualRate(StatesGroup):
    GET_VALUE_TYPE = State()
    FROM_VALUE = State()
    CARD_OR_CASH = State()
    GET_TO_VALUE_TYPE = State()
    TO_VALUE = State()
    TO_CARD_OR_CASH = State()
    
    CRYPTO = State()
    OTHER = State()
    COUNT = State()

    COUNTRY_GIVE = State()
    CITY_GIVE = State() 
    COUNTRY_GET = State()
    CITY_GET = State()


class BotStart(StatesGroup):
    CHANNEL_ID = State()
   
    COUNTRIES_SELECTION = State()
    GET_COUNTRY = State()

    ONE_COUNTRY_GET_RESPONSE = State()
    GET_RESPONSE = State()


class StopPosing(StatesGroup):

    POSTING_NAME = State()