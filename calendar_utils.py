#calendar_utils.py
from datetime import datetime, timedelta
from aiogram import types
from aiogram.types import LabeledPrice
from config import PAYMENTS_TOKEN
from bot_handler import load_data,generate_random_key,bot,save_data,dp,JSON_FILE
from info import message_pay

bookings_data = load_data(JSON_FILE)

class Booking:
    def __init__(self, user_id, day, time):
        self.user_id = user_id
        self.day = day
        self.time = time
        self.car = None

#Для клавиатуры
def update_days():
    current_date = datetime.now()
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    updated_days = []
    updated_days.append(current_date.strftime(f"{days[current_date.weekday()]} (%d.%m)"))
    for i in range(1, 7):
        next_date = current_date + timedelta(days=i)
        updated_days.append(next_date.strftime(f"{days[next_date.weekday()]} (%d.%m)"))
    return updated_days

days = update_days()
times = ["10:00", "12:00", "14:00", "16:00", "18:00", "20:00"]
machine = ["1", "2", "3"]
available_machine = {day: {time: machine.copy() for time in times} for day in days}

keyboard_days = types.ReplyKeyboardMarkup(resize_keyboard=True).add(*days)
keyboard_times = types.ReplyKeyboardMarkup(resize_keyboard=True).add(*times)
bookings = {}

# Загрузим существующие данные из файла (если они есть)
bookings_data = load_data(JSON_FILE)

@dp.message_handler(lambda message: any(day in message.text for day in days))
async def choose_time(message: types.Message):
    day = next((day for day in days if day in message.text), None)
    if all(not available_machine[day][time] for time in times):
        await message.answer("Извините, все время на этот день уже занято. Пожалуйста, выберите другой день.")
        return
    await message.answer("Отлично! Теперь выберите время:", reply_markup=keyboard_times)
    bookings[message.from_user.id] = Booking(message.from_user.id, day, None)

@dp.message_handler(lambda message: message.text in times)
async def choose_car(message: types.Message):
    user_id = message.from_user.id
    time = message.text
    booking = bookings[user_id]
    if available_machine[booking.day][time]:
        booking.time = time
        keyboard_machine = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard_machine.add(*available_machine[booking.day][booking.time])
        await message.answer("Отлично! Теперь выберите стиральную машинку:", reply_markup=keyboard_machine)
    else:
        await message.answer("Извините, все машинки на это время уже заняты. Пожалуйста, выберите другое время.")

#Собщение на оплату
@dp.message_handler(lambda message: message.text.isdigit())
async def request_payment(message: types.Message):
    user_id = message.from_user.id
    booking = bookings[user_id]
    selected_car = message.text
    if selected_car in available_machine[booking.day][booking.time]:
        booking.car = selected_car
        available_machine[booking.day][booking.time].remove(selected_car)
        await message.answer("Ваша заявка принята. Оплата времени происходит через банковскую карту.")
        title = f"Оплата стиральной машинки №{selected_car}"
        description = f"Оплата стиральной машинки №{selected_car} на {booking.day} в {booking.time} ."
        PRICE = LabeledPrice(label=f"Оплата", amount=1000 * 100)
        await bot.send_invoice(
            chat_id=message.chat.id,
            title=title,
            description=description,
            provider_token=PAYMENTS_TOKEN,
            currency="RUB",
            is_flexible=False,
            prices=[PRICE],
            start_parameter="machine",
            payload="machine"
        )
        # Добавляем информацию о бронировании в список
        booking_info = {
            "user_id": user_id,
            "username": message.from_user.username,
            "time": booking.time,
            "day": booking.day,
            "paid": False,  # Пока пользователь не оплатил
            "car_number": selected_car
        }
        bookings_data.append(booking_info)
        # Сохраняем данные в файл
        save_data(bookings_data, JSON_FILE)
    else:
        await message.answer("Выбранная машинка уже занята. Пожалуйста, выберите другую.")

#Используются для обработки предварительных запросов на оформление заказа в боте.
@dp.pre_checkout_query_handler()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

#Вывод после успешной оплаты 
@dp.message_handler(content_types=['successful_payment'])
async def successful_payment_handler(message: types.Message):
    user_id = message.from_user.id
    booking = bookings[user_id]
    key = generate_random_key()  # Генерируем ключ
    # Найдем соответствующее бронирование в списке
    for booking_info in bookings_data:
        if booking_info["user_id"] == user_id and booking_info["day"] == booking.day and booking_info["time"] == booking.time and booking_info["car_number"] == booking.car:
            booking_info["paid"] = True
            booking_info["key"] = key  
            # Обновим данные в файле
            save_data(bookings_data, JSON_FILE)
            break
    await message.answer("Спасибо за оплату!")
    await bot.send_message(
        message.chat.id,
        message_pay.format(
            day=booking.day,
            time=booking.time,
            car=booking.car,
            key=key
        ),
        parse_mode='HTML'
    )
