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
        async with state.proxy() as sp:
            sp['from_value_type'] = 'other'
            await message.answer("Наличными или на карту?", reply_markup=bot_navigation.card_or_cash())
            await GetActualRate.CARD_OR_CASH.set()


    elif message.text == "Криптовалюта":
        keys = shortcuts.get_keys_from_json('crypto-values')
        await message.answer("Выберите из перечня", reply_markup=bot_navigation.multiply_keyboard(keys))
        await GetActualRate.CRYPTO.set()


    elif message.text == "Вернуться в меню":
        await state.finish()
        await message.answer("Вовзращаюсь назад", reply_markup=bot_navigation.start_keyboard())





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
        async with state.proxy() as sp:
            value_type = sp['from_value_type']
        if message.text == 'Наличные💵':
            async with state.proxy() as sp:
                sp['card_or_cash'] = 'cash'
                

        elif message.text == "Карта💳":
            async with state.proxy() as sp:
                sp['card_or_cash'] = 'card'
        
        if value_type == 'rubles':
            await message.answer('Какой тип валюты вы хотите получить?',reply_markup=bot_navigation.crypto_or_other())
            await GetActualRate.GET_TO_VALUE_TYPE.set()
        elif value_type == 'other':
            if message.text == "Наличные💵":
                values_list = shortcuts.get_keys_from_json('values')

            elif message.text == "Карта💳":
                values_list = shortcuts.get_keys_from_json('values-card')
            await message.answer('Выберите из перечня', reply_markup=bot_navigation.multiply_keyboard(values_list))
            await GetActualRate.OTHER.set()

@dp.message_handler(state=GetActualRate.OTHER)
async def get_other_value(message: types.Message, state=FSMContext):
    if message.text != "Вернуться в меню":
        async with state.proxy() as sp:
            sp['from_value'] = message.text
        await message.answer('Какой тип валюты вы хотите получить?', reply_markup=bot_navigation.crypto_or_other())
        await GetActualRate.GET_TO_VALUE_TYPE.set()

    else:
        await state.finish()
        await message.answer("Вовзращаюсь назад", reply_markup=bot_navigation.start_keyboard())
        

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
                sp['to_card_or_cash'] = None
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
        
            
        
        if 'cash' in [from_card_or_cash, to_card_or_cash]:
            # keys = shortcuts.get_keys_from_json('countries_and_cities')
               

               
            avaliable_cities_from_value = await bc.get_countries('tether-trc20', from_value_name)
            avaliable_cities_to_value = await bc.get_countries('tether-trc20', to_value_name)
            if avaliable_cities_to_value is not None:
                async with state.proxy() as sp:
                    sp['avaliable_cities_to_value'] = avaliable_cities_to_value
            avaliable_cities_from_value_one_city = await bc.get_countries('tether-trc20', from_value_name, one_city=True)
            avaliable_cities_to_value_one_city = await bc.get_countries('tether-trc20', to_value_name, one_city=True)
            if avaliable_cities_from_value is not None:
                avaliable_cities = [list(av_city.keys())[0].title() for av_city in avaliable_cities_from_value]

            elif avaliable_cities_to_value is not None:
                avaliable_cities = [list(av_city.keys())[0].title() for av_city in avaliable_cities_to_value]

            elif avaliable_cities_from_value_one_city is not None:
                avaliable_cities = [avaliable_cities_from_value_one_city]
            elif avaliable_cities_to_value_one_city is not None:
                avaliable_cities = [avaliable_cities_to_value_one_city]

            
            
            if avaliable_cities == []:
                await message.answer('К сожалению, обменных пунктов по вашему запросу не найденно')
                await state.finish()
                return
            print(avaliable_cities)
            countries_list = []
            for city in avaliable_cities:
                country = shortcuts.get_key_by_one_of_values('countries_and_cities', city)
                if country not in countries_list:
                    if country is None:
                        continue
                    countries_list.append(country)
            if countries_list == []:
                await message.answer('Такой вариант обмена недоступен', reply_markup=bot_navigation.start_keyboard())
                await state.finish()
            
            else:
                async with state.proxy() as sp:
                    sp['avaliable_cities'] = avaliable_cities
                    sp['avaliable_countries_list'] = countries_list
                if avaliable_cities_from_value is not None or avaliable_cities_from_value_one_city is not None:
                    await message.answer('В какой стране вы хотите отдать?', reply_markup=bot_navigation.multiply_keyboard(countries_list))
                    await GetActualRate.COUNTRY_GIVE.set()
                else:
                    async with state.proxy() as sp:
                        sp['city_give'] = None
                        sp['country_give'] = None
                    await message.answer('В какой стране вы хотите получить', reply_markup=bot_navigation.multiply_keyboard(countries_list))
                    await GetActualRate.COUNTRY_GET.set()
        else:
            trade_status = await bc.get_trade_status(from_value_name, to_value_name)
            if trade_status is False:
                await message.answer('Такой вариант обмена недоступен', reply_markup=bot_navigation.start_keyboard())
                await state.finish()
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
            to_card_or_cash = sp['to_card_or_cash']
            try:
                avaliable_cities_to_value = sp['avaliable_cities_to_value']
                avaliable_cities = [list(av_city.keys())[0].title() for av_city in avaliable_cities_to_value]
            except:
                avaliable_cities = sp['avaliable_cities']
            
            countries_list = []
            for city in avaliable_cities:
                country = shortcuts.get_key_by_one_of_values('countries_and_cities', city)
                if country not in countries_list:
                    if country is None:
                        continue
                    countries_list.append(country)
            if countries_list == []:
                await message.answer('Такой вариант обмена недоступен', reply_markup=bot_navigation.start_keyboard())
                await state.finish()
            
            
        if to_card_or_cash == "cash":
            await message.answer('В какой стране вы хотите получить?',reply_markup=bot_navigation.multiply_keyboard(countries_list))
            await GetActualRate.COUNTRY_GET.set()
        else:
            await message.answer('Сколько вы хотите обменять? (Введите число)')
            async with state.proxy() as sp:
                sp['city_get'] = None
            await GetActualRate.COUNT.set()

    else:
        await state.finish()
        await message.answer('Возвращаюсь назад',reply_markup=bot_navigation.start_keyboard())

@dp.message_handler(state=GetActualRate.COUNTRY_GET)
async def country_get_handler(message: types.Message, state=FSMContext):
    if message.text != "Вернуться в меню":
        country = message.text
        async with state.proxy() as sp:
            sp['country_get'] = country
            try:
                avaliable_cities_to_value = sp['avaliable_cities_to_value']
                avaliable_cities = [list(av_city.keys())[0].title() for av_city in avaliable_cities_to_value]
            except:
                avaliable_cities = sp['avaliable_cities']
        cities = shortcuts.get_values_by_key_from_json('countries_and_cities', country)[0]
        banned_cities = []
        for city in cities:
            if city not in avaliable_cities:
                banned_cities.append(city)
        for city in banned_cities:
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
            count = float(message.text)
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
            
            country_give = sp['country_give']
          
        
        if to_value_type == 'crypto' and from_value_type == "crypto":
            city_get = None
            city_give = None 
        
        await message.answer('Идет обработка запроса...')
        first_city, usdt_given = await bc.get_data_from_city(
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
            get= True,
            usdt_given_count=usdt_given
            )

        
        course = await bc.get_course(
            from_value=from_value,
            to_value=to_value,
            to_card_or_cash=to_card_or_cash,
            from_card_or_cash=card_or_cash,
            from_value_type=from_value_type,
            to_value_type=to_value_type
            )
        if first_city != None and second_city != None:
            if city_get != None and city_give != None:
                await message.answer(
                    f"Перевод из {country_give} ({city_give}) {first_city} в {country_get} ({city_get}) {second_city}\n При курсе {course}",reply_markup=bot_navigation.start_keyboard()
                    )
                await state.finish()
            else:
                await message.answer(
                    f"Перевод {first_city} в {second_city}\n При курсе {course}", reply_markup=bot_navigation.start_keyboard()
                    )
                await state.finish()
        else:
            await message.answer("Данных по вашему запросу не найденно", reply_markup=bot_navigation.start_keyboard())
            await state.finish
        
    else:
        await state.finish()
        await message.answer('Возвращаюсь назад',reply_markup=bot_navigation.start_keyboard())


