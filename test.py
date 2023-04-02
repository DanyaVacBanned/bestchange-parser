import requests
from bs4 import BeautifulSoup as b
# import json
# headers = ''
# params = {
#     "action":"getrates",
#     "page":"rates",
#     "from":"18",
#     "to":"91",
#     "city":"0",
#     "type":"give",
#     "give":"200",
#     "get":"",
#     "commission":"0",
#     "light":"0",
#     "sort":"",
#     "range":"",
#     "sortm":"0",
#     "tsid":"0",

    
#     }
# 
# import random
# from utils import shortcuts
# proxies_list = shortcuts.get_proxy_list()
# r = requests.get('https://whoer.net/ru', proxies={'https':proxies_list[random.randint(0, len(proxies_list)-1)]})
# print(r)
# soup = b(r.text, 'lxml')
# print(soup.find('div',class_='your-ip').text)

# test = [1,2,3,4,5]
# a = len(test)//2

# print(test[a:])
# print(test[:a])

# with open('cities.txt','r',encoding='utf-8') as f:
#     cities = f.readlines()
# cities_and_ids = [cit.strip().split() for cit in cities]

# print(cities_and_ids)
# to_value_id = '3'

# with open('values.txt','r',encoding='utf-8') as file:
#     for line in file.readlines():
#         print(line.split(';')[0])
#         if line.split(';')[0] == to_value_id:
#             to_value_name = line.split(';')[1]
#             break
# print(to_value_name)
# r = requests.get('https://bestchange.ru', params=params)
# with open("test.html",'w') as f:
#     f.write(r.text)


# with open('countries_and_cities.json', 'r',encoding='utf-8') as file:
#     data = json.load(file)

# with open('all values.txt','r', encoding='utf-8') as f:
#     data = f.readlines()

# with open('all_values.json', 'w', encoding='utf-8') as file:
#     json.dump(data, file, indent=4, ensure_ascii=False)

# with open("all values.txt",'r',encoding='utf-8') as f:
#     values = f.readlines()

# val = [val.split()[0] for val in values]
# value_names = [name.split("/")[3] for name in val]
# result = []

# for name in value_names:
#     value_name = []
#     tmp = name.split("-")
#     for i in tmp:
#         if i == "to":
#             break
#         else:
#             value_name.append(i)
#     if ("-".join(value_name) not in result) and ('cash' in value_name):
#         result.append('-'.join(value_name))

# for i in result:
#     print(f'https://www.bestchange.ru/{i}-to-dollar-cash.html')

