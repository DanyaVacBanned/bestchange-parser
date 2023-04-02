import json


def get_keys_from_json(name) -> list:
    with open(f'{name}.json','r',encoding='utf-8') as file:
        result = json.load(file)
    return [''.join(list(key.keys())) for key in result]



def get_values_by_key_from_json(json_name, key) -> list:
    key = key.lower()
    with open(f"{json_name}.json",'r',encoding='utf-8') as file:
        data = json.load(file)
    for unit in data:
        if "".join(list(unit.keys())).lower() == key:
            return list(unit.values())
        

def get_capitals_from_file() -> list:
    with open('capitals.txt','r',encoding='utf-8') as file:
        data = file.read().strip().split()
    return data

def get_key_by_one_of_values(json_name, name):
    with open(f'{json_name}.json', 'r',encoding='utf-8') as file:
        data = json.load(file)
    for value in data:
        if name in list(value.values())[0]:
            return list(value.keys())[0]


def get_cities_and_ids_from_file() -> list:
    with open("cities.txt",'r',encoding='utf-8') as f:
        data = f.readlines()
    return [line.strip().split() for line in data]


def get_proxy_list():
    with open('proxy.txt','r',encoding='utf-8') as f:
        proxies = f.read().strip().split()
    return proxies

    






