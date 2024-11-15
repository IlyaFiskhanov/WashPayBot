#main.py
from aiogram import executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton,LabeledPrice
from info import *
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from calendar_utils import *
from bot_handler import *
from machine_utils import *
# Словарь для отслеживания пользователей, которые запросили ключ
waiting_for_code = {}

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer(start_message, reply_markup=inline_keyboard)

# Обработчик для команды /help
@dp.message_handler(commands=['help'])
@dp.callback_query_handler(lambda c: c.data == 'help')
async def help_handler(event):
    if isinstance(event, types.Message):
        username = event.from_user.username
        await bot.send_sticker(event.from_user.id, "CAACAgIAAxkBAAEL-yxmKPvAO_Dt_m38TjLfXW7RVXMMawAC6igAAvQSkEohphYRHkGKxzQE", reply_markup=support_keyboard)
    elif isinstance(event, types.CallbackQuery):
        username = event.from_user.username
        await event.answer()
        await bot.send_sticker(event.from_user.id, "CAACAgIAAxkBAAEL-yxmKPvAO_Dt_m38TjLfXW7RVXMMawAC6igAAvQSkEohphYRHkGKxzQE", reply_markup=support_keyboard)
    await send_notification_to_admin(f"У пользователя {username} проблемы надо решить!")

# Обработчик для команды /pay
@dp.message_handler(commands=['pay'])
@dp.callback_query_handler(lambda c: c.data == 'pay')
async def pay_handler(event):
    if isinstance(event, types.Message):
        await event.reply("Выберите день недели:", reply_markup=keyboard_days)
    elif isinstance(event, types.CallbackQuery):
        await event.answer()
        await event.message.reply("Выберите день недели:", reply_markup=keyboard_days)


# Обработчик для команды /key
@dp.message_handler(commands=['key'])
@dp.callback_query_handler(lambda c: c.data == 'key')
async def key_handler(event):
    if isinstance(event, types.Message):
        user_id = event.from_user.id
        waiting_for_code[user_id] = True
        # Отправляем сообщение с запросом кода
        await bot.send_message(
            event.chat.id,
            "Введите полученный код для подтверждения бронирования:"
        )
    elif isinstance(event, types.CallbackQuery):
        user_id = event.from_user.id
        waiting_for_code[user_id] = True
        await event.answer()
        # Отправляем сообщение с запросом кода
        await bot.send_message(
            event.message.chat.id,
            "Введите полученный код для подтверждения бронирования:"
        )

# Обработчик запроса /key
@dp.message_handler(lambda message: waiting_for_code.get(message.from_user.id))
async def confirm_booking_with_code(message: types.Message):
    user_id = message.from_user.id
    user_input_code = message.text
    current_date = now_date()
    current_time = getting_time_now()
    # Проверяем, существует ли пользователь с введенным кодом
    for booking_info in bookings_data:
        if booking_info["user_id"] == user_id:
            if (booking_info.get("key") == user_input_code 
                and booking_info.get("day") == current_date):
                if is_within_time_interval(current_time,booking_info.get("time")):
                    time_machine = round(get_time_difference(current_time,booking_info.get("time")))
                    # Пользователь существует, ключ совпадает, день совпадает, время совпадает
                    await bot.send_message(
                        user_id,
                        f"Ваш код принят."
                    )
                    # Вызываем функцию для удаления кнопок через минуту
                    await send_message_with_buttons(user_id,time_machine)
                    # Удаляем ключ из информации о бронировании
                    booking_info.pop("key")
                    # Удаляем информацию о бронировании из списка ожидающих
                    bookings_data.remove(booking_info)
                    save_data(bookings_data, JSON_FILE)
                    return
                # Пользователь существует, ключ совпадает, день совпадает, время еще не наступило
                else:
                    await bot.send_message(
                        user_id,
                        f"Время бронирования еше не подошло,подождите. Ваша запись: {booking_info.get('day')}, {booking_info.get('time')}. Попробуйте позже."
                    )
                    return
            # Пользователь существует, но ключ совпадает, день не совпадает
            elif booking_info.get("key") == user_input_code:
                
                await bot.send_message(
                    user_id,
                    f"Сегодня не ваш день. Ваш день в записи: {booking_info.get('day')}, {booking_info.get('time')}. Подождите или обратитесь к администратору."
                )
                return
    # Пользователь существует, но ключ не совпадает
    await bot.send_message(
        user_id,
        "Введенный код недействителен. Пожалуйста, попробуйте еще раз или свяжитесь с администратором."
    )

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
