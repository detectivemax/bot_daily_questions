from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


# admin_main_kb
def admin_main_kb():
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Стартовые сообщения', callback_data='admin_start_mes'),
            ],
            [
                InlineKeyboardButton(text='Актуальный список вопросов', callback_data='admin_main_kb_actual_q'),
            ],
            [
                InlineKeyboardButton(text='Изменить список вопросов', callback_data='admin_main_kb_new_q')
            ],
            [
                InlineKeyboardButton(text='Вопросов в день', callback_data='admin_daily_questions')
            ],
            [
                InlineKeyboardButton(text='Тестовый запуск', callback_data='admin_test_run')
            ],
            [
                InlineKeyboardButton(text='Проверка оплаты', callback_data='admin_pay_run')
            ]
        ]
    )
    return kb


# user_ready_kb
def user_ready_kb():
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Начать', callback_data='user_ready'),
            ]
        ]
    )
    return kb


# user_ready_kb
def user_set_time_kb(x):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='-', callback_data='user_set_time:minus'),
                InlineKeyboardButton(text=x, callback_data='user_set_time:pass'),
                InlineKeyboardButton(text='+', callback_data='user_set_time:plus'),
            ],
            [
                InlineKeyboardButton(text="Подтвердить", callback_data='user_set_time:done'),
            ]
        ]
    )
    return kb


# user_ready_kb
def user_set_work_start_kb(hour, minute):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='-', callback_data=f'user_set_work_start:h:{hour}:{minute}:minus'),
                InlineKeyboardButton(text=hour, callback_data=f'user_set_work_start:{hour}:{minute}:pass'),
                InlineKeyboardButton(text='+', callback_data=f'user_set_work_start:h:{hour}:{minute}:plus'),
            ],
            [
                InlineKeyboardButton(text='-', callback_data=f'user_set_work_start:m:{hour}:{minute}:minus'),
                InlineKeyboardButton(text=minute, callback_data=f'user_set_work_start:{hour}:{minute}:pass'),
                InlineKeyboardButton(text='+', callback_data=f'user_set_work_start:m:{hour}:{minute}:plus'),
            ],
            [
                InlineKeyboardButton(text="Подтвердить", callback_data=f'user_set_work_start:{hour}:{minute}done'),
            ]
        ]
    )
    return kb


# user_ready_kb
def user_start_work_kb():
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Начать', callback_data='user_start_work'),
            ]
        ]
    )
    return kb