from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


# user_done_kb
from functions import bd_get_many, bd_get_one


# Список сообщений для новых пользователей
def admin_new_user_kb():
    check = bd_get_many(f"SELECT mes_id FROM user_start_mes")

    kb = InlineKeyboardMarkup()
    for i in check:
        text = bd_get_one(f"SELECT caption FROM user_start_mes WHERE mes_id == '{i}'")
        file = bd_get_one(f"SELECT file FROM user_start_mes WHERE mes_id == '{i}'")
        if text == 'None' and file == 'None':
            text = "[ПУСТО]"
        else:
            text = f"[Сообщение {i}]"
        kb.add(InlineKeyboardButton(text=text, callback_data=f'admin_new_user_mes:{i}'))
    return kb


# Список сообщений для новых пользователей
def admin_new_user_actions_kb(mes_id):
    text = bd_get_one(f"SELECT caption FROM user_start_mes WHERE mes_id == '{mes_id}'")
    file = bd_get_one(f"SELECT file FROM user_start_mes WHERE mes_id == '{mes_id}'")
    if text == 'None' and file == 'None':
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton(text='Добавить', callback_data=f'admin_new_user_add_mes:{mes_id}'))

    else:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Редактировать текст', callback_data=f'admin_new_user_edit_text:{mes_id}')
                ],
                [
                    InlineKeyboardButton(text='Редактировать приложение', callback_data=f'admin_new_user_edit_file:{mes_id}')
                ],
                [
                    InlineKeyboardButton(text='Редактировать кнопки', callback_data=f'admin_new_user_edit_button:{mes_id}')
                ],
                [
                    InlineKeyboardButton(text='Удалить сообщение', callback_data=f'admin_new_user_del_mes:{mes_id}')
                ]

            ]
        )
    return kb


# Клавиатура стартовых сообщений
def start_message_kb(mes_id):
    kb = InlineKeyboardMarkup()
    reply = str(bd_get_one(f"SELECT button FROM user_start_mes WHERE mes_id = '{mes_id}'")) + "\n"
    if reply != 'None':
        for i in range(reply.count(" : ")):
            text = reply[0: reply.find(" : ")]
            url = reply[reply.find(" : ") + 3: reply.find("\n")]
            reply = reply[reply.find("\n") + 1::]

            kb.add(types.InlineKeyboardButton(text, url=url))
    return kb


# Изменить число вопросов в день
def admin_daily_question_edit_kb():

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Изменить', callback_data=f'admin_edit_daily_question')
            ]

        ]
    )
    return kb


# Выбрать день
def admin_edit_daily_q_day_kb():
    kb = InlineKeyboardMarkup()
    days_id = bd_get_many(f"SELECT week_day_id FROM admin_week_day")
    for day_id in days_id:
        week_day = bd_get_one(f"SELECT week_day FROM admin_week_day WHERE week_day_id = '{day_id}'")
        text = week_day
        callback_data = f"admin_edit_daily_q_day:{day_id}"

        kb.add(types.InlineKeyboardButton(text, callback_data=callback_data))

    kb.add(types.InlineKeyboardButton("Назад", callback_data=f'admin_back_daily_question'))
    return kb


# Выюрать число вопросов
# Изменить число вопросов в день
def admin_count_daily_question_kb(day_id):

    question_daily = bd_get_one(f"SELECT question_daily FROM admin_week_day WHERE week_day_id = '{day_id}'")
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='-', callback_data=f'admin_do_edit_daily_question:m:{day_id}'),
                InlineKeyboardButton(text=f'{question_daily}', callback_data=f'pass'),
                InlineKeyboardButton(text='+', callback_data=f'admin_do_edit_daily_question:p:{day_id}')
            ],
            [
                InlineKeyboardButton(text='Готово', callback_data=f'admin_edit_daily_question')
            ]

        ]
    )
    return kb

