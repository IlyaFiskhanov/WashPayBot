#info.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Создание инлайн клавиатуры /start
inline_keyboard = InlineKeyboardMarkup(row_width=1)
inline_keyboard.add(
    InlineKeyboardButton("🔄 Оплатить стирку", callback_data="pay"),
    InlineKeyboardButton("❓ Помощь / FAQ", callback_data="help"),
    InlineKeyboardButton("🔑 Ввести ключ оплаты", callback_data="key")
)
# Приветственное сообщение для команды .start
start_message = """
Добро пожаловать в наш сервис оплаты стиральных машинок! 🧺💳
Чтобы начать, пожалуйста, выберите один из вариантов ниже:
"""

 # Создаем инлайн клавиатуру для связи с технической поддержкой
support_keyboard = InlineKeyboardMarkup()
support_keyboard.add(InlineKeyboardButton("Связаться с технической поддержкой", url="https://t.me/ilya_fisk"))

control_machine ="""Во время использования машинки у вас есть возможность включать и выключать стиральную машинку"""


control_keyboard_machine = InlineKeyboardMarkup()
control_keyboard_machine.row(InlineKeyboardButton("Включить Машинку", callback_data="turn_on"),
                    InlineKeyboardButton("Выключить Машинку", callback_data="turn_off"))

message_pay = """
Вы успешно записаны
День: {day}
Время: {time}
Номер машинки: {car}
Ключ: <code>{key}</code>.
Сохраните его для доступа к бронированию.
"""
    
