import asyncio

from aiogram.types import ContentTypes, InlineKeyboardMarkup, InlineKeyboardButton

from config.config import ADMIN_ID
from data.data import cursor
from functions import bd_set, bd_get_one, bd_get_many, get_time, get_date
from main import bot, dp, types
from pyqiwip2p import QiwiP2P


QIWI_TOKEN = "eyJ2ZXJzaW9uIjoiUDJQIiwiZGF0YSI6eyJwYXlpbl9tZXJjaGFudF9zaXRlX3VpZCI6IjRid3MyMS0wMCIsInVzZXJfaWQiOiI3OTUxODk5Njc1MyIsInNlY3JldCI6ImViNTM4MmU2NWJiZTM2ZDI2MDYxNmRiYjM2M2I4MmNlMDM3YjY4ZTYzY2VmMWM2NTE3NDk2OThiNTA0MzY1MWUifX0="
p2p = QiwiP2P(auth_key=QIWI_TOKEN)

# user_paid
cursor.execute("""CREATE TABLE IF NOT EXISTS user_paid(
        user_id INTEGER,
        paid TEXT,
        date TEXT,
        time TEXT
    )""")


# Выставление счёта
@dp.callback_query_handler(text_contains='admin_pay_run')
async def user_set_time(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    user_id = callback.from_user.id

    text = f"Для продолжения работы бота необходимо оплатить подписку"
    await bot.send_message(user_id, text, reply_markup=payment_kb(user_id), parse_mode=types.ParseMode.MARKDOWN)


async def user_send_pay(user_id):
    text = f"Для продолжения работы бота необходимо оплатить подписку"
    await bot.send_message(user_id, text, reply_markup=payment_kb(user_id), parse_mode=types.ParseMode.MARKDOWN)


# Проверка оплаты
@dp.callback_query_handler(text_contains='check_pay:')
async def user_set_time(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    user_id = callback.from_user.id
    data = str(callback.data).replace("check_pay:", "")
    paid_before = bd_get_one(f"SELECT paid FROM user_paid WHERE user_id = '{user_id}'")

    check = p2p.check(bill_id=data).status
    print(check)
    if check == "PAID" or paid_before == "true":
        if paid_before is None:
            bd_set(f"INSERT INTO user_paid VALUES('{user_id}', 'true', '{get_date()}', '{get_time()}')")

        await bot.send_message(user_id, "Оплата прошла успешно", parse_mode=types.ParseMode.MARKDOWN)

        from user.user_handler import user_daily_q
        await user_daily_q(user_id)

    elif check == "WAITING":
        text = "Днаных об оплате не поступало"
        await bot.send_message(user_id, text, parse_mode=types.ParseMode.MARKDOWN)


def payment_kb(user_id):
    comment = f"{user_id}"
    bill = p2p.bill(amount=196, lifetime=30, comment=comment, )
    url = bill.pay_url

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Оплатить", url=url)
            ],
            [
                InlineKeyboardButton(text="Проверить оплату", callback_data=f'check_pay:{bill.bill_id}')
            ]
        ]
    )
    return kb