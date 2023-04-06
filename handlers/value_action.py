import asyncio

from aiogram import types
from aiogram.dispatcher.storage import FSMContext

from app import dp, bc

from config.exhandler import logs_writer

from utils.fsm import GetActualRate
from utils.nav import bot_navigation
from utils import shortcuts

@dp.message_handler(text='Получить информацию по курсу обмена💵')
async def get_actual_rate(message: types.Message):
    await GetActualRate.GET_VALUE_TYPE.set()
    await message.answer('Какой тип валюты вы хотите отдать?', reply_markup=bot_navigation.value_type())


@dp.message_handler(state=GetActualRate.GET_VALUE_TYPE)
async def get_value_type(message: types.Message, state = FSMContext):
    if message.text == "Рубли":
        async with state.proxy() as sp:
            sp['from_value_type'] = 'rubles'
            sp['from_value'] = message.text
        await message.answer('Наличными или на карту?', reply_markup=bot_navigation.card_or_cash())
        await GetActualRate.CARD_OR_CASH.set()

    elif message.text == "Валюта":
        keys = shortcuts.get_keys_from_json('values')
        await message.answer("Выберите из перечня", reply_markup=bot_navigation.multiply_keyboard(keys[1:]))
        await GetActualRate.OTHER.set()


    elif message.text == "Криптовалюта":
        keys = shortcuts.get_keys_from_json('crypto-values')
        await message.answer("Выберите из перечня", reply_markup=bot_navigation.multiply_keyboard(keys))
        await GetActualRate.CRYPTO.set()


    elif message.text == "Вернуться в меню":
        await state.finish()
        await message.answer("Вовзращаюсь назад", reply_markup=bot_navigation.start_keyboard())



@dp.message_handler(state = GetActualRate.OTHER)
async def get_other_value(message: types.Message, state=FSMContext):
    if message.text != 'Вернуться в меню':
        async with state.proxy() as sp:
            sp['from_value_type'] = 'other'
            sp['from_value'] = message.text
        await message.answer('Наличными или на карту?', reply_markup=bot_navigation.card_or_cash())
        await GetActualRate.CARD_OR_CASH.set()

    else:
        await state.finish()
        await message.answer('Возвращаюсь назад',reply_markup=bot_navigation.start_keyboard())

@dp.message_handler(state = GetActualRate.CRYPTO)
async def get_crypto_value(message: types.Message, state = FSMContext):
    if message.text != "Вернуться в меню":
        async with state.proxy() as sp:
            sp['from_value_type'] = 'crypto'
            sp['from_value'] = message.text
            sp['card_or_cash'] = None
        # countries_list = shortcuts.get_keys_from_json('countries_and_cities')
        # values_list = shortcuts.get_keys_from_json('crypto-values')
        
        await message.answer("В чем вы хотите получить?", reply_markup=bot_navigation.crypto_or_other())
        await GetActualRate.GET_TO_VALUE_TYPE.set()

    else:
        await state.finish()
        await message.answer('Возвращаюсь назад',reply_markup=bot_navigation.start_keyboard())

@dp.message_handler(state=GetActualRate.CARD_OR_CASH)
async def get_rubbles(message: types.Message, state=FSMContext):

    if message.text == "Вернуться в меню":
        await state.finish()
        await message.answer("Вовзращаюсь назад", reply_markup=bot_navigation.start_keyboard())
    else:
        if message.text == 'Наличные💵':
            async with state.proxy() as sp:
                sp['card_or_cash'] = 'cash'
        elif message.text == "Карта💳":
            async with state.proxy() as sp:
                sp['card_or_cash'] = 'card'
    
    
        await message.answer('Какой тип валюты вы хотите получить?',reply_markup=bot_navigation.crypto_or_other())
        await GetActualRate.GET_TO_VALUE_TYPE.set()





@dp.message_handler(state=GetActualRate.GET_TO_VALUE_TYPE)
async def get_to_value_type(message: types.Message, state = FSMContext):
    if message.text != "Вернуться в меню":
        if message.text == 'В валюте':
            async with state.proxy() as sp:
                sp['to_value_type'] = 'other'
            
            await message.answer('На карту или наличными?',reply_markup=bot_navigation.card_or_cash())
            await GetActualRate.TO_CARD_OR_CASH.set()
        elif message.text == 'В криптовалюте':
            async with state.proxy() as sp:
                sp['to_value_type'] = 'crypto'
            keys = shortcuts.get_keys_from_json('crypto-values')
            
            await message.answer('Выберите из перечня', reply_markup=bot_navigation.multiply_keyboard(keys))
            await GetActualRate.TO_VALUE.set()
    else:
        await state.finish()
        await message.answer('Возвращаюсь назад',reply_markup=bot_navigation.start_keyboard())


@dp.message_handler(state=GetActualRate.TO_CARD_OR_CASH)
async def get_to_card_or_cash(message: types.Message, state=FSMContext):
    if message.text == 'Карта💳':
        async with state.proxy() as sp:
            sp['to_card_or_cash'] = 'card'
        keys = shortcuts.get_keys_from_json('values-card')
        await message.answer('Выберите из перечня', reply_markup=bot_navigation.multiply_keyboard(keys[1:]))
        await GetActualRate.TO_VALUE.set()

    elif message.text == "Наличные💵":
        async with state.proxy() as sp:
            sp['to_card_or_cash'] = 'cash'
        keys = shortcuts.get_keys_from_json('values')
        await message.answer('Выберите из перечня', reply_markup=bot_navigation.multiply_keyboard(keys[1:]))
        await GetActualRate.TO_VALUE.set()


@dp.message_handler(state=GetActualRate.TO_VALUE)
async def get_to_value(message: types.Message, state=FSMContext):
    if message.text != "Вернуться в меню":
        async with state.proxy() as sp:
            sp['to_value'] = message.text
            from_value = sp['from_value']
            to_value_type = sp['to_value_type']
            from_value_type = sp['from_value_type']

        from_card_or_cash, to_card_or_cash = [None, None]
        if 'other' == from_value_type or 'rubles' == from_value_type:
            async with state.proxy() as sp:
                
                from_card_or_cash = sp['card_or_cash']
        if 'other' == to_value_type or 'rubles' == to_value_type:
            async with state.proxy() as sp:
                to_card_or_cash = sp['to_card_or_cash']
        
        if 'cash' in [from_card_or_cash, to_card_or_cash]:
            # keys = shortcuts.get_keys_from_json('countries_and_cities')
            if from_value_type in ['other','rubles']:
                if from_card_or_cash == "card":
                    from_value_name = list(shortcuts.get_values_by_key_from_json('values-card', from_value)[0].keys())[0]
                elif from_card_or_cash == "cash":
                    if from_value_type == "rubles":
                        from_value_name = 'cash-ruble'
                    else:
                        from_value_name = list(shortcuts.get_values_by_key_from_json('values', from_value)[0].keys())[0]
                    
            elif from_value_type == "crypto":
                from_value_name = list(shortcuts.get_values_by_key_from_json('crypto-values', from_value)[0].keys())[0]

            if to_value_type in ["other", 'rubles']:
                if to_card_or_cash == "card":
                    to_value_name = list(shortcuts.get_values_by_key_from_json('values-card', message.text)[0].keys())[0]  
                elif to_card_or_cash == "cash":
                    if to_value_type == "rubles":
                        to_value_name = 'cash-ruble'
                    else:
                        to_value_name = list(shortcuts.get_values_by_key_from_json('values', message.text)[0].keys())[0]   

            elif to_value_type == "crypto":
                to_value_name = list(shortcuts.get_values_by_key_from_json('crypto-values', message.text)[0].keys())[0]    
            print(from_value_name)
            print(to_value_name)

            avaliable_cities = [list(city.keys())[0].title() for city in await bc.get_countries(from_value_name, to_value_name)]
            print(avaliable_cities)
            countries_list = []
            for city in avaliable_cities:
                country = shortcuts.get_key_by_one_of_values('countries_and_cities', city)
                if country not in countries_list:
                    if country is None:
                        continue
                    countries_list.append(country)
            print(countries_list)
            
            async with state.proxy() as sp:
                sp['avaliable_cities'] = avaliable_cities
                sp['avaliable_countries_list'] = countries_list
            await message.answer('В какой стране вы хотите отдать?', reply_markup=bot_navigation.multiply_keyboard(countries_list))
            await GetActualRate.COUNTRY_GIVE.set()
        else:
            async with state.proxy() as sp:
                sp['country_give'] = None
                sp['country_get'] = None
                sp['city_give'] = None
                sp['city_get'] = None
            await message.answer('Сколько вы хотите обменять? (введите число)')
            await GetActualRate.COUNT.set()
    else:
        await state.finish()
        await message.answer('Возвращаюсь назад',reply_markup=bot_navigation.start_keyboard())


@dp.message_handler(state=GetActualRate.COUNTRY_GIVE)
async def get_country(message: types.Message, state=FSMContext):
    if message.text != 'Вернуться в меню':
        country = message.text
        async with state.proxy() as sp:
            sp['country_give'] = country
            avaliable_cities = sp['avaliable_cities']
        banned_cities = []
        cities = shortcuts.get_values_by_key_from_json('countries_and_cities', country)[0]
        print(cities)
        for city in cities:
            if city not in avaliable_cities:
                banned_cities.append(city)
        for city in banned_cities:
            cities.remove(city)
        await message.answer('Выберите город, в котором хотите отдать', reply_markup=bot_navigation.multiply_keyboard(cities))
        await GetActualRate.CITY_GIVE.set()
    else:
        await state.finish()
        await message.answer('Возвращаюсь назад',reply_markup=bot_navigation.start_keyboard())


@dp.message_handler(state=GetActualRate.CITY_GIVE)
async def city_get_handler(message: types.Message, state = FSMContext):
    if message.text != 'Вернуться в меню':
        async with state.proxy() as sp:
            sp['city_give'] = message.text
            countries_list = sp['avaliable_countries_list']
        
        await message.answer('В какой стране вы хотите получить?',reply_markup=bot_navigation.multiply_keyboard(countries_list))
        await GetActualRate.COUNTRY_GET.set()

    else:
        await state.finish()
        await message.answer('Возвращаюсь назад',reply_markup=bot_navigation.start_keyboard())

@dp.message_handler(state=GetActualRate.COUNTRY_GET)
async def country_get_handler(message: types.Message, state=FSMContext):
    if message.text != "Вернуться в меню":
        country = message.text
        async with state.proxy() as sp:
            sp['country_get'] = country
            avaliable_cities = sp['avaliable_cities']
        cities = shortcuts.get_values_by_key_from_json('countries_and_cities', country)[0]
        for city in cities:
            if city not in avaliable_cities:
                cities.remove(city)        
        await message.answer('Выберите город, в котором хотите получить', reply_markup=bot_navigation.multiply_keyboard(cities))
        await GetActualRate.CITY_GET.set()
    else:
        await state.finish()
        await message.answer('Возвращаюсь назад',reply_markup=bot_navigation.start_keyboard())

@dp.message_handler(state=GetActualRate.CITY_GET)
async def city_give_handler(message: types.Message, state=FSMContext):
    if message.text != "Вернуться в меню":
        async with state.proxy() as sp:
            sp['city_get'] = message.text
        await message.answer('Сколько вы хотите обменять? (Введите число)')
        await GetActualRate.COUNT.set()
    else:
        await state.finish()
        await message.answer('Возвращаюсь назад',reply_markup=bot_navigation.start_keyboard())


@dp.message_handler(state = GetActualRate.COUNT)
async def get_count(message: types.Message, state = FSMContext):
    if message.text != "Вернуться в меню":
        try:
            count = int(message.text)
        except ValueError as ex:
            logs_writer(ex)
            await message.answer('Некорректный ввод, попробуйте еще раз')
        async with state.proxy() as sp:
            from_value_type = sp['from_value_type']
            to_value_type = sp['to_value_type']
            to_value = sp['to_value']
            from_value = sp['from_value']
            card_or_cash = sp['card_or_cash']
            city_get = sp['city_get']
            city_give = sp['city_give']
            country_get = sp['country_get']
            to_card_or_cash = sp['to_card_or_cash']
            if from_value_type != 'rubles':
                country_give = sp['country_give']
            else:
                country_give = 'Россия'
        
        if to_value_type == 'crypto':
            city_get = None 
        elif from_value_type == 'crypto':
            city_give = None

        first_city = await bc.get_data_from_city(
            from_value=from_value,
            to_value=to_value,
            city=city_give,
            from_value_type=from_value_type,
            to_value_type=to_value_type,
            card_or_cash=card_or_cash,
            to_card_or_cash=to_card_or_cash,
            count=count,
            give=True
            )
        second_city = await bc.get_data_from_city(
            from_value=from_value,
            to_value=to_value,
            city=city_get,
            from_value_type=from_value_type,
            to_value_type=to_value_type,
            card_or_cash=card_or_cash,
            to_card_or_cash=to_card_or_cash,
            count=count,
            get= True
            )


        if first_city is not None and second_city is not None:
            fv_join = []
            sv_join = []
            for fv in first_city['Отдаете'].split():
                try:
                    float(fv)
                    fv_join.append(fv)
                except ValueError:
                    break
            for sv in second_city['Получаете'].split():
                try:
                    float(sv)
                    sv_join.append(sv)
                except ValueError:
                    break


            give_result = float("".join(fv_join))
            get_result = float("".join(sv_join))
            print(give_result)
            print(get_result)
            course = f"1 {first_city['from_value_name']} = {first_city['course']} {second_city['to_value_name']}" if give_result < get_result else f"1 {second_city['to_value_name']} = {first_city['course']} {first_city['from_value_name']}"
            if city_get != None and city_give != None:
                await message.answer(
                    f"Перевод из {country_give} ({city_give}) {first_city['Отдаете']} в {country_get} ({city_get}) {second_city['Получаете']}\n При курсе {course}"
                    )
            else:
                await message.answer(
                    f"Перевод {first_city['Отдаете']} в {second_city['Получаете']}\n При курсе {course}"
                    )
        else:
            await message.answer("Данных по вашему запросу не найденно")
        

        await message.answer('Возвращаюсь в меню', reply_markup=bot_navigation.start_keyboard())
        await state.finish()

    else:
        await state.finish()
        await message.answer('Возвращаюсь назад',reply_markup=bot_navigation.start_keyboard())


