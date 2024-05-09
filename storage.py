import os
import telebot
from telebot import types
import PyPDF2
import pandas as pd
import datetime
import time
import base64
import requests
from collections import Counter

gain_cnt = 23000

username = 'k@brandandface'
password = 'bisfip-9dontA-sanqot'

own_credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
import magic


def get_file_format(file_path):
    # Создаем объект magic
    mime = magic.Magic(mime=True)

    # Определяем MIME-тип файла
    file_type = mime.from_file(file_path)

    # Проверяем MIME-тип и возвращаем соответствующее значение
    print(file_type)
    if "application/pdf" in file_type:
        return "PDF"
    elif "application/octet-stream" in file_type or 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in file_type:
        return "XLSX"
    else:
        return "Неизвестный формат"
def get_positions(items):
    url = 'https://api.moysklad.ru/api/remap/1.2/entity/product'

    headers = {
        "Authorization": f"Basic {own_credentials}",
        "Accept-Encoding": "gzip",
    }

    response = requests.get(url, headers=headers)
    result = response.json()
    products = []
    arr = []

    for j in result["rows"]:
        data = {
            "code": int(j["code"]),
            "href": j["meta"]["href"]
        }
        arr.append(data)
    for i in items:
        for j in arr:
            try:
                if int(i["code"]) == j["code"]:
                    data = {
                        "code": int(i["code"]),
                        "count": i["count"],
                        "href": j["href"]
                    }
                    products.append(data)
                    break
            except:
                print('NUN')
    positions = []
    for i in products:
        position_item = {
            "quantity": i["count"],
            "assortment": {
                "meta": {
                    "href": i["href"],
                    "type": "product",
                    "mediaType": "application/json"
                }
            }
        }
        positions.append(position_item)
    return (positions)
def create_gain_xlsx(file_name):
    # FINAL CODE
    df = pd.read_excel(file_name)
    cnt = 1
    global gain_cnt
    gain_cnt += 1
    print('Hey')
    result_df = pd.read_excel('/root/bot/Товары Мой склад.xlsx')
    print('Hey')
    items = []
    organization_href = "https://api.moysklad.ru/api/remap/1.2/entity/organization/46238336-ab20-11ea-0a80-06aa000b1087"
    wb_agent_href = "https://api.moysklad.ru/api/remap/1.2/entity/counterparty/00ffc40e-ec94-11ee-0a80-09b70002b51f"
    sber_agent_href = "https://api.moysklad.ru/api/remap/1.2/entity/counterparty/edc658a5-ec93-11ee-0a80-081a0002a353"
    yandex_agent_href = "https://api.moysklad.ru/api/remap/1.2/entity/counterparty/d709434f-ec93-11ee-0a80-081a0002a0e1"

    shipment_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    store_href = "https://api.moysklad.ru/api/remap/1.2/entity/store/323e29a3-300c-11ec-0a80-02da00343fa6"
    print('Hey')

    if df.columns.tolist()[0] == '№ задания':
        df['Артикул Wildberries'] = df['Артикул Wildberries'].fillna(100000000000).astype(int)
        result_df['артикул вб'] = result_df['артикул вб'].fillna(100000000000).astype(int)
        for i in df['Артикул Wildberries']:
            for j in result_df['артикул вб']:
                if int(i) == int(j):
                    index = result_df[result_df['артикул вб'] == i].index[0]
                    item = result_df.loc[index, 'код товара']
                    items.append(item)
                    cnt += 1
        items = Counter(items)
        items = [{"code": key, "count": value} for key, value in items.items()]
        positions = get_positions(items)
        data = {
            "name": f'{gain_cnt}',
            "organization": {
                "meta": {
                    "href": organization_href,
                    "type": "organization",
                    "mediaType": "application/json"
                }
            },
            "agent": {
                "meta": {
                    "href": wb_agent_href,
                    "type": "counterparty",
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
            "code": f'{gain_cnt}',
            "moment": shipment_date,
            "applicable": False,
            "vatEnabled": True,
            "vatIncluded": True,
            "positions": positions,
            "overhead": {
                "sum": 60,
                "distribution": "price"
            }
        }

        url = "https://api.moysklad.ru/api/remap/1.2/entity/demand"

        headers = {
            "Authorization": f"Basic {own_credentials}",
            "Accept-Encoding": "gzip"
        }

        response = requests.post(url, json=data, headers=headers)
        gain_cnt += 1
        if response.status_code == 200:
            print("Отгрузка успешно создана.")
        else:
            print("Ошибка при создании отгрузки:", response.status_code)
            print("Текст ошибки:", response.text)

    if df.columns.tolist()[0] == 'Информация о заказе':
        print('Hey')
        df = df.drop(0)
        print(df)
        result_df['артикул яндекс'] = result_df['артикул яндекс'].fillna(0).astype(int)
        df['Unnamed: 3'] = df['Unnamed: 3'].fillna(0).astype(int)
        for i in df['Unnamed: 3']:
            for j in result_df['артикул яндекс']:
                if int(i) == int(j):
                    index = result_df[result_df['артикул яндекс'] == i].index[0]
                    items.append(result_df.loc[index, 'код товара'])
                    cnt += 1
        items = Counter(items)
        items = [{"code": key, "count": value} for key, value in items.items()]
        positions = get_positions(items)
        data = {
            "name": f'{gain_cnt}',
            "organization": {
                "meta": {
                    "href": organization_href,
                    "type": "organization",
                    "mediaType": "application/json"
                }
            },
            "agent": {
                "meta": {
                    "href": yandex_agent_href,
                    "type": "counterparty",
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
            "code": f'{gain_cnt}',
            "moment": shipment_date,
            "applicable": False,
            "vatEnabled": True,
            "vatIncluded": True,
            "positions": positions,
            "overhead": {
                "sum": 60,
                "distribution": "price"
            }
        }

        url = "https://api.moysklad.ru/api/remap/1.2/entity/demand"

        headers = {
            "Authorization": f"Basic {own_credentials}",
            "Accept-Encoding": "gzip"
        }

        response = requests.post(url, json=data, headers=headers)
        gain_cnt += 1
        if response.status_code == 200:
            print("Отгрузка успешно создана.")
        else:
            print("Ошибка при создании отгрузки:", response.status_code)
            print("Текст ошибки:", response.text)

    if df.columns.tolist()[0] == '# Заказа Мегармаркет':
        result_df['Артикуо сбер'] = result_df['Артикуо сбер'].fillna(100000000000).astype(int)
        df['Артикул'] = df['Артикул'].fillna(100000000000).astype(int)
        for i in df['Артикул']:
            for j in result_df['Артикуо сбер']:
                if int(i) == int(j):
                    index = result_df[result_df['Артикуо сбер'] == i].index[0]
                    item = result_df.loc[index, 'код товара']
                    items.append(item)
                    cnt += 1
        items = Counter(items)
        items = [{"code": key, "count": value} for key, value in items.items()]
        positions = get_positions(items)
        data = {
            "name": f'{gain_cnt}',
            "organization": {
                "meta": {
                    "href": organization_href,
                    "type": "organization",
                    "mediaType": "application/json"
                }
            },
            "agent": {
                "meta": {
                    "href": sber_agent_href,
                    "type": "counterparty",
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
            "code": f'{gain_cnt}',
            "moment": shipment_date,
            "applicable": False,
            "vatEnabled": True,
            "vatIncluded": True,
            "positions": positions,
            "overhead": {
                "sum": 60,
                "distribution": "price"
            }
        }

        url = "https://api.moysklad.ru/api/remap/1.2/entity/demand"

        headers = {
            "Authorization": f"Basic {own_credentials}",
            "Accept-Encoding": "gzip"
        }

        response = requests.post(url, json=data, headers=headers)
        gain_cnt += 1
        if response.status_code == 200:
            print("Отгрузка успешно создана.")
        else:
            print("Ошибка при создании отгрузки:", response.status_code)
            print("Текст ошибки:", response.text)

def create_gain_pdf(file_name):
    import fitz
    global gain_cnt
    gain_cnt += 1
    organization_href = "https://api.moysklad.ru/api/remap/1.2/entity/organization/46238336-ab20-11ea-0a80-06aa000b1087"
    ozon_agent_href = "https://api.moysklad.ru/api/remap/1.2/entity/counterparty/cadee956-ec93-11ee-0a80-010a00027386"
    store_href = "https://api.moysklad.ru/api/remap/1.2/entity/store/323e29a3-300c-11ec-0a80-02da00343fa6"
    shipment_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    doc = fitz.open(file_name)
    text = ""
    text_array = []
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text_array.append(page.get_text("text"))
    numbers_list = []
    result_df = pd.read_excel('/root/bot/Товары Мой склад.xlsx')
    import re
    for i in text_array:
        numbers = re.findall(r'\d+', i)
        for j in range(len(numbers) - 1):
            if j % 8 == 0 and j != 0:
                for k in range(len(numbers) - 3 - j):
                    if (int(numbers[k + j]) / 1000 > 1):
                        numbers_list.append(numbers[k + j])
    result_df['Артикул озон'] = result_df['Артикул озон'].fillna(100000000000).astype(int)
    items = []
    for i in numbers_list:
        for j in result_df['Артикул озон']:
            if int(i) == int(j):
                print(i, j)
                index = result_df[result_df['Артикул озон'] == int(i)].index[0]
                item = result_df.loc[index, 'код товара']
                items.append(item)
    items = Counter(items)
    items = [{"code": key, "count": value} for key, value in items.items()]
    doc.close()
    positions = get_positions(items)
    data = {
        "name": f'{gain_cnt}',
        "organization": {
            "meta": {
                "href": organization_href,
                "type": "organization",
                "mediaType": "application/json"
            }
        },
        "agent": {
            "meta": {
                "href": ozon_agent_href,
                "type": "counterparty",
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
        "code": f'{gain_cnt}',
        "moment": shipment_date,
        "applicable": False,
        "vatEnabled": True,
        "vatIncluded": True,
        "positions": positions,
        "overhead": {
            "sum": 60,
            "distribution": "price"
        }
    }

    url = "https://api.moysklad.ru/api/remap/1.2/entity/demand"

    headers = {
        "Authorization": f"Basic {own_credentials}",
        "Accept-Encoding": "gzip"
    }

    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        print("Отгрузка успешно создана.")
    else:
        print("Ошибка при создании отгрузки:", response.status_code)
        print("Текст ошибки:", response.text)

def remove_every_other_page(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        writer = PyPDF2.PdfWriter()

        num_pages = len(reader.pages)
        for page_number in range(num_pages):
            if page_number % 2 == 1:
                writer.add_page(reader.pages[page_number])

        with open('/root/bot/output.pdf', 'wb') as output_file:
            writer.write(output_file)
while True:
    try:
        def detect_file_type(file_path):
            mime = magic.Magic(mime=True)
            file_type = mime.from_file(file_path)
            return file_type

        bot = telebot.TeleBot('BOT_TOKEN')
        name = None
        chat_id = ""
        cnt = 0

        @bot.message_handler(commands=['start'])
        def start(message):
            markup = types.InlineKeyboardMarkup(row_width = 1)
            btn1 = types.InlineKeyboardButton('Загрузить таблицу соответсвия', callback_data='temp')
            btn2 = types.InlineKeyboardButton('Получить текущую таблицу соответствия', callback_data='humidity')
            btn3 = types.InlineKeyboardButton('Форматирование в "Мой склад"', callback_data='pressure')
            markup.add(btn1, btn2, btn3)
            bot.send_message(message.chat.id, f'Добрый день!',
                             reply_markup=markup)

        @bot.callback_query_handler(func=lambda call: True)
        def answer(call):
            if (call.data == 'temp'):
                message = bot.send_message(call.message.chat.id, 'Отправьте новую таблицу')
                bot.register_next_step_handler(message, new_table)
            elif (call.data == 'humidity'):
                with open ('/root/bot/Товары Мой склад.xlsx', 'rb') as file:
                    bot.send_document(call.message.chat.id, file)
            elif (call.data == 'pressure'):
                message = bot.send_message(call.message.chat.id, 'Отправьте файл')
                bot.register_next_step_handler(message, handle_document)
        def new_table(message):

            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            with open('/root/bot/Товары Мой склад.xlsx', 'wb') as new_file:
                new_file.write(downloaded_file)
            message = bot.send_message(message.chat.id, 'Таблица обновлена!')
            markup = types.InlineKeyboardMarkup(row_width=1)
            btn1 = types.InlineKeyboardButton('Загрузить таблицу соответсвия', callback_data='temp')
            btn2 = types.InlineKeyboardButton('Получить текущую таблицу соответствия', callback_data='humidity')
            btn3 = types.InlineKeyboardButton('Форматирование в "Мой склад"', callback_data='pressure')
            markup.add(btn1, btn2, btn3)
            bot.send_message(message.chat.id, f'Ваше действие далее?',
                             reply_markup=markup)

        def handle_document(message):
            global gain_cnt
            gain_cnt += 1
            print(gain_cnt)
            file_info = bot.get_file(message.document.file_id)
            print('Hey')
            downloaded_file = bot.download_file(file_info.file_path)
            print('Hey')
            file_name = os.path.join("/root/bot/", message.document.file_name)
            print('Hey')
            with open(file_name, 'wb') as new_file:
                new_file.write(downloaded_file)
            if (get_file_format(file_name) == 'XLSX'):
                print('Hey')
                create_gain_xlsx(file_name)
            else:
                remove_every_other_page(file_name)
                create_gain_pdf(file_name)
            os.remove(file_name)
            message = bot.send_message(message.chat.id, 'Отгрузка создана!')
            markup = types.InlineKeyboardMarkup(row_width=1)
            btn1 = types.InlineKeyboardButton('Загрузить таблицу соответсвия', callback_data='temp')
            btn2 = types.InlineKeyboardButton('Получить текущую таблицу соответствия', callback_data='humidity')
            btn3 = types.InlineKeyboardButton('Форматирование в "Мой склад"', callback_data='pressure')
            markup.add(btn1, btn2, btn3)
            bot.send_message(message.chat.id, f'Ваше действие далее?{message.document.file_name}',
                             reply_markup=markup)

        bot.polling(none_stop=True)
    except:
        print('Connecting...')
        time.sleep(1)
