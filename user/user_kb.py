from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


# user_done_kb
def user_q_done_kb():
    button_hi = KeyboardButton('👉 Следующий вопрос')
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add(button_hi)
    return kb


# user_done_kb
def user_day_done_kb():
    button_hi = KeyboardButton('👍 Завершить на сегодня')
    kb = ReplyKeyboardMarkup(resize_keyboard=True).add(button_hi)
    return kb


# Кнопка дальше Регистрация пользователя
def user_reg_1_kb():

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Далее', callback_data=f'user_reg_1')
            ]
        ]
    )
    return kb


# Кнопка Отлично дальше Регистрация пользователя
def user_reg_2_kb():

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Отлично, дальше', callback_data=f'user_reg_2')
            ]
        ]
    )
    return kb


# Кнопка Отлично дальше Регистрация пользователя
def user_reg_3_kb():

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Отлично, дальше', callback_data=f'user_reg_3')
            ]
        ]
    )
    return kb


# Кнопка Отлично дальше Регистрация пользователя
def user_reg_4_kb():

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Отлично, дальше', callback_data=f'user_reg_4')
            ]
        ]
    )
    return kb


# Кнопка Отлично дальше Регистрация пользователя
def user_reg_5_kb():

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Отлично, дальше', callback_data=f'user_reg_5')
            ]
        ]
    )
    return kb


# Кнопка Отлично дальше Регистрация пользователя
def user_reg_6_kb():

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Отлично, дальше', callback_data=f'user_reg_6')
            ]
        ]
    )
    return kb

