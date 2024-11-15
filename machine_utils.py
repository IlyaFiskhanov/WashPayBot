#machine_utils.py
from bot_handler import send_request
from config import URL_HOSTS
from aiogram import types
from bot_handler import bot,dp

@dp.callback_query_handler(lambda callback_query: callback_query.data == "turn_on")
async def turn_on(callback_query: types.CallbackQuery):
    status_code = await send_request(URL_HOSTS + "/CLOSE_MACHINE")
    await bot.answer_callback_query(callback_query.id, text="Стиральная машинка успешно включена!")


@dp.callback_query_handler(lambda callback_query: callback_query.data == "turn_off")
async def turn_off(callback_query: types.CallbackQuery):
    status_code = await send_request(URL_HOSTS + "/OPEN_MACHINE")
    await bot.answer_callback_query(callback_query.id, text="Стиральная машинка успешно выключена!")


