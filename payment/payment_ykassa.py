import asyncio
from aiogram.types import ContentTypes

from config.config import ADMIN_ID
from functions import bd_set, bd_get_one, bd_get_many, get_time
from main import bot, dp, types

YOO_TOKEN = "381764678:TEST:31525"


# Выбор времени
@dp.callback_query_handler(text_contains='admin_pay_run')
async def user_set_time(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    user_id = callback.from_user.id

    await user_set_time_mes(user_id)


# Выбор времени
async def user_set_time_mes(user_id):
    await bot.send_invoice(chat_id=user_id, title="Подписка на месяц",
                           description="Для продолжения работы бота необходимо оплатить подписку",
                           payload="month_sub",
                           provider_token=YOO_TOKEN, currency="RUB", start_parameter="test_bot",
                           prices=[{"label": "Руб", "amount": 19900}])


@dp.pre_checkout_query_handler()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query_id=pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=ContentTypes.SUCCESSFUL_PAYMENT)
async def process_pay(message: types.Message):
    user_id = message.from_user.id
    if message.successful_payment.invoice_payload == "month_sub":
        await bot.send_message(user_id, "Успешный платёж")
