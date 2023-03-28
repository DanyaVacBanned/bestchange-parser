import requests
import asyncio

from config.auth import token
from aiogram import types, Bot

from fake_useragent import UserAgent
from bs4 import BeautifulSoup as b




ua = UserAgent()
bot = Bot(token)




class BestchangeUserAction:
    
    def get_html_code(self, url) -> b:
        headers = {
        "user-agent":ua.random
        }

        r = requests.get(url, headers=headers)
        
        soup = b(r.text, 'lxml')
        return soup
    

 
    def get_values_names(self):
        headers = {
        "user-agent":ua.random
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

    def get_countries(self, value1, value2) -> list:
        url = f'https://www.bestchange.ru/{value1}-to-{value2}.html'
        soup = self.get_html_code(url)
        big_text = soup.find('div', {'id':'big_text'})
        links = big_text.find_all('a')
        result = [{link.text.lower():link.get('href')} for link in links]
        return result[2:]
    

    

    def sort_value_names(self) -> list:
        all_code_names = list()
        all_names = list()
        values = list()
        try:
            with open('all values.txt', 'r', encoding='utf-8') as f:
                links = f.readlines()

        except FileNotFoundError:
            print('Файл еще не создан')
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


    async def get_rate(self, url):
        soup = self.get_html_code(url)
        table = soup.find('table', {'id':'content_table'})
        tbody = table.find('tbody')
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
    

    async def get_rate_for_post(self, channel_id, message: types.Message):
        all_cities = self.get_countries('tether-trc20', 'dollar-cash')
        all_cities_names = [list(city.keys())[0] for city in all_cities]
        capitals = self.get_capitals()

        while True:
            for city in all_cities_names:
                if city in capitals:
                    for dick in all_cities:
                        if list(dick.keys())[0] == city:
                            capital_href = list(dick.values())[0]
                            break
                    rates = await self.get_rate(capital_href)
                    if len(rates) != 1:
                        give_number = float(rates[1]["Отдаете"].split()[0])
                        give_number += give_number * 0.01
                        try:
                            await bot.send_message(
                                channel_id,
                                f"""
                                Город: {city.title()}
                            Обменник: {rates[1]['Обменник'].title()}\n
                            Отдаете: {give_number} {' '.join(rates[1]['Отдаете'].split()[1:])}\n
                            Получаете: {rates[1]['Получаете'].title()}\n

                                """
                                )
                        except:
                            await message.answer("Возможно вы ввели неверное id канала")
                            return
                        await asyncio.sleep(0.5)
                    else:
                        try:
                            await bot.send_message(
                                channel_id,
                                f"""
                                Город: {city.title()}
                            Обменник: {rates[0]['Обменник'].title()}\n
                            Отдаете: {rates[0]['Отдаете'].title()}\n
                            Получаете: {rates[0]['Получаете'].title()}\n

                                """
                                )
                        except:
                            await message.answer("Возможно вы ввели неверное id канала")
                            return
                        await asyncio.sleep(0.5)
            await asyncio.sleep(24*60*60)



    def get_capitals(self):
        soup = self.get_html_code('https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_%D1%81%D1%82%D0%BE%D0%BB%D0%B8%D1%86_%D0%B3%D0%BE%D1%81%D1%83%D0%B4%D0%B0%D1%80%D1%81%D1%82%D0%B2')
        result = []
        tables = soup.find_all('table', {'class':'wikitable'})
        for table in tables:
            tbody = table.find("tbody")
            
            trows = tbody.find_all('tr')
            for tr in trows[1:]:
                td = tr.find_all('td')
                result.append(td[2].text.lower().strip())
        return result


