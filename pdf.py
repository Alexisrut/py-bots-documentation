import time
import telebot
from PIL import Image
import os
from reportlab.pdfgen import canvas
from pdf2image import convert_from_path
bot = telebot.TeleBot('BOT_TOKEN')
def pdf_to_jpeg(pdf_path):

            # Создаем массив для хранения названий файлов
            file_names = []

            # Извлекаем изображения из PDF
            images = convert_from_path(pdf_path)

            # Сохраняем извлеченные изображения как JPEG
            for i, image in enumerate(images):
                file_name = f"/root/bot/page_{i + 1}.jpeg"
                image.save(file_name, "JPEG")
                file_names.append(file_name)

            return file_names
def create_pdf_with_image(images):
            c = canvas.Canvas("/root/bot/output.pdf", pagesize=(820, 712))
            width, height = (820, 712)
            for image_path in images:
                c.drawImage(image_path, 0, 0, width=width, height=height)
                c.showPage()
            c.save()
def main(file):
            pdf_path = file
            created_files = pdf_to_jpeg(pdf_path)
            all_images = []
            j = 0
            for file_name in created_files:
                image_path = file_name
                page = Image.open(image_path)
                cropped_img = page.crop((27, 27, 1668, 2160))
                cropped_img.save(image_path)
                width = 820
                height = 712
                rows = 3
                cols = 2
                total_images = rows * cols

                # Загрузим изображение с помощью Pillow
                img = Image.open(image_path)

                for i in range(total_images):
                    x = (i % cols) * width
                    y = (i // cols) * height
                    cropped_image = img.crop((x, y, x + width, y + height))
                    save_path = f"/root/bot/image_{i + 1 + j}.jpg"
                    cropped_image.save(save_path)
                    all_images.append(save_path)
                j += 6
            create_pdf_with_image(all_images)  # Установка размера страницы 75x120

            for image_path in all_images:
                os.remove(image_path)
            for image_path in created_files:
                os.remove(image_path)

# Функция для разбиения PDF файла на блоки
name = None
chat_id = ""
cnt = 0

@bot.message_handler(commands=['start'])
def start(message):
            bot.send_message(message.chat.id, "Добрый день! Отправьте файл.")
            bot.register_next_step_handler(message, handle_document)

def handle_document(message):
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            with open('/root/bot/example.pdf', 'wb') as new_file:
                new_file.write(downloaded_file)
            main('/root/bot/example.pdf')
            with open('/root/bot/output.pdf', 'rb') as pdf_file:
                bot.send_document(message.chat.id, pdf_file)
            bot.register_next_step_handler(message, handle_document)

bot.polling(none_stop=True)
