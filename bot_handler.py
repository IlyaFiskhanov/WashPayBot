#bot_handler.py
import asyncio
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher
from config import TOKEN,YOUR_TELEGRAM_USER_ID
import logging
import requests
import secrets
import string
import json
import time
from info import control_keyboard_machine,control_machine

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
JSON_FILE = "booked_slots.json"

# Функция для отправки сообщения админу
async def send_notification_to_admin(message):
    try:
        await bot.send_message(YOUR_TELEGRAM_USER_ID, message)
    except Exception as e:
        logging.error(f"Error sending notification: {str(e)}")

# Отправка запроса на ESP
async def send_request(url):
    try:  
        r = requests.get(url)
        return r.status_code
    except requests.exceptions.ConnectionError as e:
        return None

# Функция для генерации случайного ключа
def generate_random_key():
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(10))

# Функция для загрузки данных из JSON файла
def load_data(filename):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        return []

# Функция для сохранения данных в JSON файл
def save_data(data, filename):
    if len(data) >= 100:
        # Если количество записей достигло 100, удаляем первые 20 записей
        del data[:20]
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

#Получение текущего времени
def getting_time_now():
    current_time = datetime.now()
    formatted_time = current_time.strftime('%H:%M')
    return formatted_time

#Получение текущей даты
def now_date():
    now = datetime.now()
    weekday_names = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    weekday_name = weekday_names[now.weekday()]
    now_date = now.strftime(f"{weekday_name} (%d.%m)")
    return now_date

# Функция для удаления кнопок через минуту
async def remove_buttons(chat_id, message_id,time_machine):
    end_time = time.strftime("%H:%M:%S", time.localtime(time.time() + time_machine))
    await bot.send_message(chat_id, f"Время исчезновения кнопок: {end_time}")
    await asyncio.sleep(time_machine) 
    # Удалите кнопки из сообщения
    await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=None)

# Функция, которая отправляет сообщение с кнопками и запускает задачу на удаление кнопок через минуту
async def send_message_with_buttons(chat_id,time_machine):
    global button_task
    message = await bot.send_message(chat_id, control_machine, reply_markup=control_keyboard_machine)
    button_task = asyncio.create_task(remove_buttons(chat_id, message.message_id,time_machine))

#Проверка на интервал времени
def is_within_time_interval(time_now_d, recording_time_d, interval=2):
    recording_time_d = datetime.strptime(recording_time_d , '%H:%M')
    time_now_d = datetime.strptime(time_now_d, '%H:%M')
    end_time = recording_time_d  + timedelta(hours=interval)
    return recording_time_d  <= time_now_d <= end_time

#Получение количество секунд из времени работы
def get_time_difference(time_now_d, recording_time_d, interval=2):
    if is_within_time_interval(time_now_d, recording_time_d, interval):
        recording_time_d = datetime.strptime(recording_time_d , '%H:%M')
        time_now_d = datetime.strptime(time_now_d, '%H:%M')
        end_time = recording_time_d  + timedelta(hours=interval)
        difference = end_time - time_now_d
        print(difference)
        return difference.total_seconds()
    else:
        return 0
    


