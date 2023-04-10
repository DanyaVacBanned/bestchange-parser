
import requests
import asyncio


import undetected_chromedriver as uc

from time import sleep

from aiogram import Bot
from aiogram.utils.exceptions import MessageIsTooLong

from config.auth import token
from config.exhandler import logs_writer

from utils import shortcuts

from fake_useragent import UserAgent
from bs4 import BeautifulSoup as b

from selenium import webdriver
from selenium.webdriver.common.by import By


ua = UserAgent()
bot = Bot(token)




class BestchangeUserAction:
    
    async def get_html_code(self, url, data = None) -> b:
        max_tries = 3
        while True:
            headers = {
            "user-agent":ua.random,
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
                }

            if data is None:        
                r = requests.get(url, headers=headers)
            else:
                r = requests.post(url, headers=headers, data=data)
            print(r.status_code)
            # with open('index.html','w') as file:
            #     file.write(r.text)
            if r.status_code == 200:
                return b(r.text, 'lxml')
            elif r.status_code == 429:
                try:
                    options = uc.ChromeOptions()
                    options.headless = True
                    driver = uc.Chrome(options=options, version_main=109)
                    
                    driver.get('https://www.bestchange.ru/')
                    await asyncio.sleep(15)
                    driver.quit()
                except Exception as ex:
                    print(ex)
                    logs_writer(ex)
                    continue
            elif r.status_code == 404:
                logs_writer('404 page not found')
                return None
            
            else:
                max_tries -= 1
                if max_tries == 0:
                    logs_writer('another exception during request')
                    return None
                continue
                
            
                
 
    def get_values_names(self):
        headers = {
        "user-agent":ua.random,
        'accept': '*/*'
        }

        hrefs = []
        r = requests.get('https://www.bestchange.ru/', headers=headers)
        soup = b(r.text, 'lxml')
        table = soup.find('div', {'id': 'curr_tab'})
        tags = table.find_all('a')
        for a in tags:
            hrefs.append(f"{a.get('href')} {a.text}" )
        return hrefs

    
    def write_value_names_in_file(self):
        names = self.get_values_names()

        with open('all values.txt', 'a', encoding='utf-8') as f:
            for name in names[:len(names)-1]:
                f.write(f'{name}\n')

    async def get_countries(self, value1, value2, one_city = False) -> list:
        url = f'https://www.bestchange.ru/{value1}-to-{value2}.html'
        soup = await self.get_html_code(url)
        big_text = soup.find('div', {'id':'big_text'})
        
        if one_city:
            try:
                city = big_text.find('b', class_='gray').text
            except AttributeError:
                return None
            return city

        links = big_text.find_all('a')
        result = [{link.text.lower():link.get('href')} for link in links]
        if result[2:] == []:
            return None
        return result[2:]
    



    async def get_trade_status(self, value1, value2) -> bool:
        url = f"https://www.bestchange.ru/{value1}-to-{value2}.html"
        soup = await self.get_html_code(url)
        span = soup.find('span', class_='bt').text.lower()
        if span == "отсутствуют":
            return False
        else:
            return True
        


    def sort_value_names(self) -> list:
        all_code_names = list()
        all_names = list()
        values = list()
        try:
            with open('all values.txt', 'r', encoding='utf-8') as f:
                links = f.readlines()

        except FileNotFoundError as ex:
            logs_writer(f"{ex} - файл еще не создан")
            return None
        for link in links:
            name = []
            code_name = []
            name.append(' '.join(link.split()[1:]))
            for sym in link.split('/')[3].split('-'):
                if sym == 'to':
                    break
                else:
                    code_name.append(sym)
            code_name = '-'.join(code_name)
            if code_name not in all_code_names and name not in all_names:
                all_code_names.append(code_name)
                all_names.append(name)
                values.append({' '.join(name):code_name})

        return values, all_names


    async def get_rate(self, url, data = None):
        soup = await self.get_html_code(url, data)
        if soup == None:
            return None
        table = soup.find('table', {'id':'content_table'})
        try:
            tbody = table.find('tbody')
        except AttributeError as ex:
            logs_writer(ex)
            return None
        trow = tbody.find_all('tr')
        result = []
        for row in trow:
            td = row.find_all('td')

            transfer = td[1].find('div',class_='ca').text if td[1].find('div',class_='ca') is not None else None
            give = f"{td[2].find('div',class_='fs').text if td[2].find('div',class_='fs') is not None else None} {td[2].find('div',class_='fm').text if td[2].find('div',class_='fm') is not None else None}"
            get = td[3].text if td[3] is not None else None
            
            if transfer != None and give != f'{None} {None}' and get != None:
                result.append(
                    {
                    'Обменник': transfer,
                    'Отдаете': give,
                    'Получаете': get
                    }
                    )
        return result
    

    async def get_rate_for_post(self, channel_id):
        capitals = shortcuts.get_capitals_from_file()
        cities = shortcuts.get_cities_and_ids_from_file()
        while True:
            result = []
            data = {
                        "action":"getrates",
                        "page":"rates",
                        "from":"105",
                        "to":"10",
                        "city":"0",
                        "type":"give",
                        "give":"0",
                        "get":"",
                        "commission":"0",
                        "light":"0",
                        "sort":"",
                        "range":"",
                        "sortm":"0",
                        "tsid":"0",
                    }
            tinkoff_to_usdt = await self.get_rate('https://www.bestchange.ru/action.php', data) # Первый курс для рассчета
          
            usdt_price_in_rubbles = tinkoff_to_usdt[1 if len(tinkoff_to_usdt) > 1 else 0]["Отдаете"].split()[0]
            for city in cities:
                if city[1] in capitals:
                    city_id = str(city[0])
                    country = shortcuts.get_key_by_one_of_values('countries_and_cities',city[1])
                    data2 = {
                        "action":"getrates",
                        "page":"rates",
                        "from":"10",
                        "to":"89",
                        "city":city_id,
                        "type":"",
                        "give":"",
                        "get":"",
                        "commission":"0",
                        "light":"0",
                        "sort":"from",
                        "range":"asc",
                        "sortm":"1",
                        "tsid":"0",
                    }
                    usdt_to_cashusd = await self.get_rate('https://www.bestchange.ru/action.php',data2)
                    if usdt_to_cashusd is None:
                        continue
                    # with open('logs.txt','a',encoding='utf-8') as f:
                    #     f.write(f'{city[1]} - {float(usdt_to_cashusd[1 if len(usdt_to_cashusd) > 1 else 0]["Получаете"].split()[0]) % 1}')
                    if float(usdt_to_cashusd[1 if len(usdt_to_cashusd) > 1 else 0]["Отдаете"].split()[0]) % 1 != 0:
                        # tinkoff_to_cashusd_percent = float(usdt_to_cashusd[1 if len(usdt_to_cashusd) > 1 else 0]['Отдаете'].split()[0]) * (1 + float(usdt_to_cashusd[1 if len(usdt_to_cashusd) > 1 else 0]["Отдаете"].split()[0]) % 1)
                        if float(usdt_to_cashusd[1 if len(usdt_to_cashusd) > 1 else 0]['Отдаете'].split()[0]) > 1:
                            tinkoff_to_cashusd_percent = round((float(usdt_price_in_rubbles) * (1 + float(usdt_to_cashusd[1 if len(usdt_to_cashusd) > 1 else 0]['Отдаете'].split()[0]) % 1)) * 1.01,2)
                        else:
                            tinkoff_to_cashusd_percent = round((float(usdt_price_in_rubbles) * (float(usdt_to_cashusd[1 if len(usdt_to_cashusd) > 1 else 0]['Отдаете'].split()[0]) % 1)) * 1.01,2)
                        
                        usdt_to_cashusd[1 if len(usdt_to_cashusd) > 1 else 0]['Отдаете'] = str(tinkoff_to_cashusd_percent) + " руб"
                    else:
                        usdt_to_cashusd[1 if len(usdt_to_cashusd) > 1 else 0]['Отдаете'] = str(round(float(usdt_price_in_rubbles), 2)) + ' руб'
                    
                    result.append(f'Россия (Москва) - {country} ({city[1]}) отдаете {usdt_to_cashusd[1 if len(usdt_to_cashusd) > 1 else 0]["Отдаете"]} = получаете 1 $')
            try:
                await bot.send_message(channel_id, "\n\n".join(sorted(result)))
            except MessageIsTooLong:
                new_len = len(result) / 2
                await bot.send_message(channel_id, "\n\n".join(sorted(result[:new_len])))
                await bot.send_message(channel_id, "\n\n".join(sorted(result[new_len:])))


        # print(usdt_price_in_rubbles)
            delay = 24*3600*3
            await asyncio.sleep(delay)


    async def get_capitals(self):
        soup = await self.get_html_code('https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_%D1%81%D1%82%D0%BE%D0%BB%D0%B8%D1%86_%D0%B3%D0%BE%D1%81%D1%83%D0%B4%D0%B0%D1%80%D1%81%D1%82%D0%B2')
        result = []
        tables = soup.find_all('table', {'class':'wikitable'})
        for table in tables:
            tbody = table.find("tbody")
            
            trows = tbody.find_all('tr')
            for tr in trows[1:]:
                td = tr.find_all('td')
                result.append(td[2].text.lower().strip())
        



    def get_countries_using_selenium(self):
        driver = webdriver.Chrome()
        driver.get('https://www.bestchange.ru/bitcoin-to-dollar-cash.html')
        sleep(5)
        country_list = driver.find_element(By.ID, 'countrylist')
        countries = country_list.find_elements(By.TAG_NAME, 'a')
        result = []
        for country in countries[1:]:
            country.click()
            city_list = driver.find_element(By.ID, 'citylist')
            collection = {
                country.text.strip(): [
                    city.text.strip() for city in city_list.find_elements(By.TAG_NAME, 'a')
                ]
                }
            result.append(collection)
        return result


    async def get_course(self, 
                         from_value, 
                         to_value, 
                         to_card_or_cash, 
                         from_card_or_cash,
                         from_value_type,
                         to_value_type
                         ):
        if from_value_type in ['other', 'rubles']:
            if from_card_or_cash == "cash":
                from_value_id = list(shortcuts.get_values_by_key_from_json('values', from_value)[0].values())[0]
                
            elif from_card_or_cash == "card":
                from_value_id = list(shortcuts.get_values_by_key_from_json('values-card', from_value)[0].values())[0]
        elif from_value_type == 'crypto':
            from_value_id = list(shortcuts.get_values_by_key_from_json('crypto-values', from_value)[0].values())[0]


        if to_value_type in ['other', 'rubles']:
            if to_card_or_cash == "cash":
                to_value_id = list(shortcuts.get_values_by_key_from_json('values', to_value)[0].values())[0]
            elif to_card_or_cash == "card":
                to_value_id = list(shortcuts.get_values_by_key_from_json('values-card', to_value)[0].values())[0]

        elif to_value_type == "crypto":
            to_value_id = list(shortcuts.get_values_by_key_from_json('crypto-values', to_value)[0].values())[0]

        data = {
                "action":"getrates",
                "page":"rates",
                "from":"10",
                "to":str(from_value_id),
                "city":"0",
                "type":"give",
                "give":"1",
                "get":"",
                "commission":"0",
                "light":"0",
                "sort":"",
                "range":"",
                "sortm":"0",
                "tsid":"0",
            }
        
       
        from_value_rate_req = await self.get_rate('https://www.bestchange.ru/action.php', data=data)
        from_value_rate = from_value_rate_req[0]["Получаете"]
        fv_join = []
        for fv in from_value_rate.split():
            try:
                float(fv)
                fv_join.append(fv)
            except ValueError:
                break
        from_value_count = float("".join(fv_join))
        to_data = {
            "action":"getrates",
            "page":"rates",
            "from":"10",
            "to":str(to_value_id),
            "city":"0",
            "type":"get",
            "give":"",
            "get":"1",
            "commission":"0",
            "light":"0",
            "sort":"",
            "range":"",
            "sortm":"0",
            "tsid":"0",
            }

        to_value_rate_req = await self.get_rate('https://www.bestchange.ru/action.php', data=to_data)
        to_value_rate = to_value_rate_req[1 if len(to_value_rate_req) > 1 else 0]["Отдаете"]
        sv_join = []
        for sv in to_value_rate.split():
            try:
                float(sv)
                sv_join.append(sv)
            except ValueError:
                break
        to_value_count = float("".join(sv_join))
        course = to_value_count * from_value_count
        if course <= 1:
            from_value_course = 1 / course
            return f"1 {from_value} = {from_value_course} {to_value}"
        else:
            
            return f"1 {to_value} = {course} {from_value}"


    async def get_data_from_city(
            self, 
            from_value, 
            to_value, 
            city, 
            from_value_type, 
            to_value_type, 
            card_or_cash,
            to_card_or_cash,
            count,
            give = False,
            get = False,
            usdt_given_count = None
            ):
        print(from_value)
        print(to_value)
        print(city)
        if city is not None:
            with open('cities.txt','r',encoding='utf-8') as f:
                cities = f.readlines()
            cities_and_ids = [cit.strip().split() for cit in cities]
            for collection in cities_and_ids:
                if collection[1].lower() == city.lower():
                    city_id = collection[0]
                    break
        else:
            city_id = "0"
        if from_value_type in ["other", "rubles"] :
            if card_or_cash == 'card':
                from_values = shortcuts.get_values_by_key_from_json('values-card',from_value)
                
            elif card_or_cash == "cash":
                if from_value_type == 'rubles':
                    from_value_id = '91'
                else:
                    from_values = shortcuts.get_values_by_key_from_json('values', from_value)

        elif from_value_type == "crypto":
            from_values = shortcuts.get_values_by_key_from_json('crypto-values', from_value)
        try:
            from_value_id = str("".join(list(from_values[0].values())))
        except UnboundLocalError:
            pass
        with open('values.txt','r',encoding='utf-8') as file:
            for line in file.readlines():
                if str(line.split(';')[0]) == from_value_id:
                    from_value_name = line.split(';')[1]
        if to_value_type == "other":
            if to_card_or_cash == "cash":
                to_values = shortcuts.get_values_by_key_from_json('values', to_value)
            elif to_card_or_cash == "card":
                to_values = shortcuts.get_values_by_key_from_json('values-card', to_value)
        elif to_value_type == "crypto":
            to_values = shortcuts.get_values_by_key_from_json('crypto-values', to_value)
        
        to_value_id = str("".join(list(to_values[0].values())))
        with open('values.txt','r',encoding='utf-8') as file:
            for line in file.readlines():
                if line.split(';')[0] == to_value_id:
                    to_value_name = line.split(';')[1]
        if give:
            if card_or_cash == "cash":
                data = {
                "action":"getrates",
                "page":"rates",
                "from":"10",
                "to":str(from_value_id),
                "city":str(city_id),
                "type":"get",
                "give":"",
                "get":str(count),
                "commission":"0",
                "light":"0",
                "sort":"",
                "range":"",
                "sortm":"0",
                "tsid":"0",
                }
            else:
                data = {
                    "action":"getrates",
                    "page":"rates",
                    "from":"10",
                    "to":str(from_value_id),
                    "city":"0",
                    "type":"get",
                    "give":"",
                    "get":str(count),
                    "commission":"0",
                    "light":"0",
                    "sort":"",
                    "range":"",
                    "sortm":"0",
                    "tsid":"0",
                }

            usdt_to_from_value = await self.get_rate('https://www.bestchange.ru/action.php',data=data)
            fv_join = []
            
            for fv in usdt_to_from_value[1 if len(usdt_to_from_value) > 1 else 0]['Отдаете'].split():
                try:
                    float(fv)
                    fv_join.append(fv)
                except ValueError:
                    break
            first_value_count_for_join = []
            first_value_count = usdt_to_from_value[1 if len(usdt_to_from_value) > 1 else 0]['Получаете'].split()
            for fvc in first_value_count:
                try:
                    float(fvc)
                    first_value_count_for_join.append(fvc)
                except ValueError:
                    break
            first_value_count = float(''.join(first_value_count_for_join))
            usdt_given = str(''.join(fv_join))
            rate_in_first_city = f"{str(count)} {from_value_name}"

        if get: 
            if to_card_or_cash == "cash":
                data_result = {
                "action":"getrates",
                "page":"rates",
                "from":"10",
                "to":str(to_value_id),
                "city":str(city_id),
                "type":"give",
                "give":str(usdt_given_count),
                "get":"",
                "commission":"0",
                "light":"0",
                "sort":"",
                "range":"",
                "sortm":"0",
                "tsid":"0",
                }
            else:

                data_result = {
                    "action":"getrates",
                    "page":"rates",
                    "from":"10",
                    "to":str(to_value_id),
                    "city":"0",
                    "type":"give",
                    "give":str(usdt_given_count),
                    "get":"",
                    "commission":"0",
                    "light":"0",
                    "sort":"",
                    "range":"",
                    "sortm":"0",
                    "tsid":"0",
                    }

            with open('requests.txt','w') as f:
                f.write(str(data_result))
            
            usdt_to_to_value = await self.get_rate('https://www.bestchange.ru/action.php',data=data_result)
            
        
            sv_join = []
            
            for sv in usdt_to_to_value[1 if len(usdt_to_to_value) > 1 else 0]['Получаете'].split():
                try:
                    float(sv)
                    sv_join.append(sv)
                except ValueError:
                    break
        
            one_usdt_in_to_value = float(''.join(sv_join))
            rate_in_second_city = f"{one_usdt_in_to_value * 1.01} {to_value_name}"
        


        

        if give:
            return rate_in_first_city, usdt_given
        elif get:
            return rate_in_second_city

        

