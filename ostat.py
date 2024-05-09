# Final code
import time
import pandas as pd
import requests
import datetime
import base64
import telebot
from telebot import types
import json
username = 'MOYSKLAD_LOGIN'
password = 'MOYSKLAD_PASSWORD'
own_credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
code = 13080
headers = {
    "Authorization": f"Basic {own_credentials}",
    "Accept-Encoding": "gzip"
}
bot = telebot.TeleBot('BOT_TOKEN')

def get_products():
    url = 'https://api.moysklad.ru/api/remap/1.2/entity/product'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['rows']
    else:
        print(f"Ошибка при получении списка товаров: {response.text}")
        return []


def get_reserve():
    url = 'https://api.moysklad.ru/api/remap/1.2/report/stock/all'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['rows']
    else:
        print(f"Ошибка при получении списка товаров: {response.text}")
        return []


def get_orders():
    result_array = []
    states_to_minus = []
    url = 'https://api.moysklad.ru/api/remap/1.2/entity/purchaseorder'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        all_orders = response.json()['rows']
    else:
        print(f"Ошибка при получении списка товаров: {response.text}")
        return []
    url = 'https://api.moysklad.ru/api/remap/1.2/entity/purchaseorder/metadata'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        meta_orders = response.json()
    else:
        print(f"Ошибка при получении списка товаров: {response.text}")
        return []
    cnt = 0
    for i in meta_orders['states']:
        if i['name'] != 'Принят':
            states_to_minus.append(i['meta']['href'])
    for i in all_orders:
        for j in states_to_minus:
            try:
                if (i['state']['meta']['href'] == j):
                    result_array.append(i)
                    cnt += 1
                    break
            except:
                continue
    return result_array


def get_orders_positions(order_positions_hrefs):
    result = []
    for i in order_positions_hrefs:
        url = i
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result += response.json()['rows']
        else:
            print(f"Ошибка при получении списка товаров: {response.text}")
            return []
    return result


def to_crat(result_arr):
    fin_arr = []
    for i in result_arr:
        url = i[0]
        response = requests.get(url, headers=headers)
        tovar = response.json()
        try:
            pack_quanity = tovar['packs'][0]['quantity']
            if (i[1] != pack_quanity) and pack_quanity != 1:
                fin_arr.append((i[0], pack_quanity - (i[1] % pack_quanity) + i[1]))
            elif (i[1] != pack_quanity) and pack_quanity == 1:
                fin_arr.append((i[0], i[1]))
        except:
            fin_arr.append((i[0], i[1]))
    return fin_arr


def make_order(element):
    url = f'{element["assortment"]["meta"]["href"]}'
    headers = {
        "Authorization": f"Basic {own_credentials}",
        "Accept-Encoding": "gzip"
    }
    response = requests.get(url, headers=headers)
    global code
    try:
        code += 1
        post = response.json()['supplier']['meta']['href']
        url = 'https://api.moysklad.ru/api/remap/1.2/entity/purchaseorder'
        organization_href = "https://api.moysklad.ru/api/remap/1.2/entity/organization/46238336-ab20-11ea-0a80-06aa000b1087"
        shipment_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        store_href = "https://api.moysklad.ru/api/remap/1.2/entity/store/323e29a3-300c-11ec-0a80-02da00343fa6"
        headers = {
            "Authorization": f"Basic {own_credentials}",
            "Accept-Encoding": "gzip",
            "Content-Type": "application/json"
        }
        data = {
            "name": f'{code}',
            "moment": shipment_date,
            "organization": {
                "meta": {
                    "href": organization_href,
                    "type": "organization",
                    "mediaType": "application/json"
                }
            },
            "store": {
                "meta": {
                    "href": store_href,
                    "type": "store",
                    "mediaType": "application/json"
                }
            },
            "agent": {
                "meta": {
                    "href": post,
                    "metadataHref": "https://api.moysklad.ru/api/remap/1.2/entity/counterparty/metadata",
                    "type": "counterparty",
                    "mediaType": "application/json"
                }
            },
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            url = result['positions']['meta']['href']
            headers = {
                "Authorization": f"Basic {own_credentials}",
                "Accept-Encoding": "gzip",
                "Content-Type": "application/json"
            }
            data = element
            response = requests.post(url, headers=headers, json=data)
            result = response.json()
        else:
            print(f"Ошибка при получении списка товаров: {response.text}")
    except:
        code += 1
        url = 'https://api.moysklad.ru/api/remap/1.2/entity/purchaseorder'
        organization_href = "https://api.moysklad.ru/api/remap/1.2/entity/organization/46238336-ab20-11ea-0a80-06aa000b1087"
        shipment_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        store_href = "https://api.moysklad.ru/api/remap/1.2/entity/store/323e29a3-300c-11ec-0a80-02da00343fa6"
        headers = {
            "Authorization": f"Basic {own_credentials}",
            "Accept-Encoding": "gzip",
            "Content-Type": "application/json"
        }
        data = {
            "name": f'{code}',
            "moment": shipment_date,
            "organization": {
                "meta": {
                    "href": organization_href,
                    "type": "organization",
                    "mediaType": "application/json"
                }
            },
            "store": {
                "meta": {
                    "href": store_href,
                    "type": "store",
                    "mediaType": "application/json"
                }
            },
            "agent": {
                "meta": {
                    "href": 'https://api.moysklad.ru/api/remap/1.2/entity/counterparty/ac09af39-43a4-11ec-0a80-055a000cb7a0',
                    "metadataHref": "https://api.moysklad.ru/api/remap/1.2/entity/counterparty/metadata",
                    "type": "counterparty",
                    "mediaType": "application/json"
                }
            },
            "positions": element
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            url = result['positions']['meta']['href']
            headers = {
                "Authorization": f"Basic {own_credentials}",
                "Accept-Encoding": "gzip",
                "Content-Type": "application/json"
            }
            data = element
            response = requests.post(url, headers=headers, json=data)
            result = response.json()
        else:
            print(f"Ошибка при получении списка товаров: {response.text}")


def main():
    stocks = get_reserve()
    stocks_hrefs = []
    for i in stocks:
        string = i['meta']['href']
        string = string[:-16]
        stocks_hrefs.append((string, i['stock']))
    products = get_products()
    orders = get_orders()
    order_positions_hrefs = []
    for i in orders:
        order_positions_hrefs.append(i['positions']['meta']['href'])
    items_orders = {}
    orders_positions = get_orders_positions(order_positions_hrefs)
    for i in range(len(orders_positions)):
        items_orders[f"{orders_positions[i]['assortment']['meta']['href']}"] = 0
    for i in range(len(orders_positions)):
        items_orders[f"{orders_positions[i]['assortment']['meta']['href']}"] += orders_positions[i]['quantity']
    cnt = 0
    result_arr = []
    products_with_ost = []
    for i in products:
        for j in stocks_hrefs:
            if (i['meta']['href'] == j[0]):
                try:
                    elem = i['minimumBalance']
                    quantity = j[1]
                    if (elem - quantity) > 0:
                        products_with_ost.append((i['meta']['href'], elem - quantity))
                except:
                    break
    for i in products_with_ost:
        try:
            if items_orders[f"{i[0]}"] != -1:
                if (i[1] - items_orders[f"{i[0]}"]) > 0:
                    result_arr.append((i[0], abs(i[1]) - items_orders[f"{i[0]}"]))
                    cnt += 1
                else:
                    continue
        except:
            result_arr.append((i[0], abs(i[1])))
    final_order_positions = []
    result_arr = to_crat(result_arr)
    for i in result_arr:
        if (int(i[1]) > 0):
            position_item = {
                "quantity": int(i[1]),
                "assortment": {
                    "meta": {
                        "href": i[0],
                        "type": "product",
                        "mediaType": "application/json"
                    }
                }
            }
            final_order_positions.append(position_item)
        else:
            continue
    if final_order_positions == []:
        return ('0')
    else:
        for i in final_order_positions:
            make_order(i)
        return('1')
while(True):
    try:
        @bot.message_handler(commands=['start'])
        def start(message):
                    markup = types.InlineKeyboardMarkup(row_width = 1)
                    btn1 = types.InlineKeyboardButton('Запустить скрипт', callback_data='temp')
                    markup.add(btn1)
                    bot.send_message(message.chat.id, f'Добрый день!',
                                    reply_markup=markup)

        @bot.callback_query_handler(func=lambda call: True)
        def answer(call):
                    if (call.data == 'temp'):
                        global code
                        message = bot.send_message(call.message.chat.id, 'Запуск...')
                        while (True):
                            print('here')
                            result = main()
                            if result == '0':
                                markup = types.InlineKeyboardMarkup(row_width=1)
                                btn1 = types.InlineKeyboardButton('Запустить скрипт', callback_data='temp')
                                markup.add(btn1)
                                bot.send_message(message.chat.id, f'Нет товаров для пополнения!',
                                                reply_markup=markup)
                                break
                            else:
                                markup = types.InlineKeyboardMarkup(row_width=1)
                                btn1 = types.InlineKeyboardButton('Запустить скрипт', callback_data='temp')
                                markup.add(btn1)
                                bot.send_message(message.chat.id, f'Заказ успешно создан!',
                                                reply_markup=markup)
                                break
                            code += 1


        bot.polling(none_stop=True)
    except:
        time.sleep(1)
