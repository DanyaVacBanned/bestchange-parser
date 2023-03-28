import asyncio

from aiogram import types
from aiogram.dispatcher.storage import FSMContext

from app import dp, bc

from utils.fsm import GetActualRate


@dp.message_handler(text='Получить информацию по курсу обмена💵')
async def get_actual_rate(message: types.Message):
    await GetActualRate.VALUE.set()
    await message.answer('Введите имя первой валюты из пары')
    
@dp.message_handler(state=GetActualRate.VALUE)
async def get_first_value(message: types.Message, state=FSMContext):
    
    _, values_names = bc.sort_value_names()
    values_list = [name[0].lower() for name in values_names]
    if message.text.lower() not in values_list:
        await message.answer("""
        Возможно вы некорекктно ввели имя валюты,
        попробуйте вывести перечень и скопировать название
        """)
        await state.finish()
    else:
        async with state.proxy() as sp:
            sp['value1'] = message.text
        await message.answer('Введите имя второй валюты из пары')
        await GetActualRate.TO_VALUE.set()

@dp.message_handler(state=GetActualRate.TO_VALUE)
async def get_second_value(message: types.Message, state=FSMContext):
    values_dicks, values_names = bc.sort_value_names()
    values_list = [name[0].lower() for name in values_names]
    if message.text.lower() not in values_list:
        await message.answer("""
        Возможно вы некорекктно ввели имя валюты,
        попробуйте вывести перечень и скопировать название
        """)
        await state.finish()
    else:
        async with state.proxy() as sp:
            value2 = message.text
            value1 = sp['value1']
            for val in values_dicks:
                if value1 in list(val.keys()):
                    value1 = list(val.values())[0]
                    sp['value1'] = value1
                if value2 in list(val.keys()):
                    value2 = list(val.values())[0]
                    sp['value2'] = value2
        
    if 'cash' in value2.split('-'):
        await message.answer(
            """
            Введите город, по которому хотите получить информацию
            """
            )
        await GetActualRate.CITY.set()

@dp.message_handler(state=GetActualRate.CITY)
async def get_city(message: types.Message, state=FSMContext):
    city = message.text.lower()
    async with state.proxy() as sp:
        value1 = sp['value1']
        value2 = sp['value2']
    cities_list = bc.get_countries(value1, value2)
    for name in cities_list:
        if city in list(name.keys()):
            city_href = list(name.values())[0]
            break
        else:
            city_href = None
    if city_href is not None:
        rate_list = await bc.get_rate(city_href)
        for rate in rate_list:
            await message.answer(
                f"""
                Обменник: {rate['Обменник']}\n
                Отдаете: {rate['Отдаете']}\n
                Получаете: {rate['Получаете']}\n
                """
                )
            await asyncio.sleep(0.5)
    else:
        await message.answer('Возможны вы ввели название города неккоректно')
    await state.finish()
        