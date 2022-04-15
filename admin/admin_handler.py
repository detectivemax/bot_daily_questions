import openpyxl
import xlrd
import xlsxwriter
import requests as requests

from admin.admin_kb import admin_new_user_kb, admin_daily_question_edit_kb, admin_edit_daily_q_day_kb, \
    admin_count_daily_question_kb
from comands_handler_kb import admin_main_kb
from config.config import ADMIN_ID, BOT_TOKEN
from functions import bd_set, max_task_id, bd_get_many, bd_get_one
from main import bot, dp, types


# admin_main_kb_new_q
from user.user_handler import user_daily_q


@dp.callback_query_handler(text_contains='admin_main_kb_new_q')
async def admin_main_kb_new_q(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    user_id = callback.from_user.id

    bd_set(f"UPDATE user_stage SET stage_one = '{1}' WHERE user_id = '{user_id}'")
    await bot.send_message(user_id, "Отправьте таблицу с новым списком вопросов:")


# Сохранение новых адресов в excel
async def admin_main_kb_new_q_get(message):
    user_id = message.from_user.id

    file = await bot.get_file(message.document.file_id)
    link = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"
    file_name = f"questions.{link.split('.')[-1]}"
    r = requests.get(link, allow_redirects=True)
    open(file_name, "wb").write(r.content)

    bd_set(f"UPDATE user_stage SET stage_one = '{0}' WHERE user_id = '{user_id}'")
    get_questions()
    await bot.send_message(user_id, "Новые вопросы сохранены")


def get_questions():
    # Словарь
    wb = openpyxl.load_workbook(filename="questions.xlsx")
    sheet = wb.active
    bd_set("DELETE FROM question")

    for row in range(2, sheet.max_row + 1):
        if sheet[row][0].value is not None:
            bd_set(f"INSERT INTO question VALUES('{max_task_id('SELECT q_id FROM question') + 1}', '{sheet[row][0].value}')")
            print(sheet[row][0].value)


# admin_main_kb_actual_q
@dp.callback_query_handler(text_contains='admin_main_kb_actual_q')
async def admin_main_kb_new_q(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    user_id = callback.from_user.id

    bd_set(f"UPDATE user_stage SET stage_one = '{1}' WHERE user_id = '{user_id}'")
    await bot.send_document(user_id, open(r'questions.xlsx', 'rb'))


# Тестовый запуск
@dp.callback_query_handler(text_contains='admin_test_run')
async def admin_main_kb_new_q(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    user_id = callback.from_user.id

    await user_daily_q(user_id)


# Вопросов в день
@dp.callback_query_handler(text_contains='admin_daily_questions')
async def admin_main_kb_new_q(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    user_id = callback.from_user.id

    text = ""
    days_id = bd_get_many(f"SELECT week_day_id FROM admin_week_day")
    for day_id in days_id:
        week_day = bd_get_one(f"SELECT week_day FROM admin_week_day WHERE week_day_id = '{day_id}'")
        question_daily = bd_get_one(f"SELECT question_daily FROM admin_week_day WHERE week_day_id = '{day_id}'")
        text += f"{week_day}: {question_daily}\n"

    await bot.send_message(user_id, text, reply_markup=admin_daily_question_edit_kb())


# Изменить числов опросов в день: выбор дня
@dp.callback_query_handler(text_contains='admin_edit_daily_question')
async def admin_main_kb_new_q(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    user_id = callback.from_user.id

    text = "Для какого дня изменить число вопросов?"
    await bot.edit_message_text(text, user_id, callback.message.message_id, reply_markup=admin_edit_daily_q_day_kb())


# Назад
@dp.callback_query_handler(text_contains='admin_back_daily_question')
async def admin_main_kb_new_q(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    user_id = callback.from_user.id

    text = ""
    days_id = bd_get_many(f"SELECT week_day_id FROM admin_week_day")
    for day_id in days_id:
        week_day = bd_get_one(f"SELECT week_day FROM admin_week_day WHERE week_day_id = '{day_id}'")
        question_daily = bd_get_one(f"SELECT question_daily FROM admin_week_day WHERE week_day_id = '{day_id}'")
        text += f"{week_day}: {question_daily}\n"

    await bot.edit_message_text(text, user_id, callback.message.message_id, reply_markup=admin_daily_question_edit_kb())


# Изменить вопросов в день
@dp.callback_query_handler(text_contains='admin_edit_daily_q_day:')
async def admin_main_kb_new_q(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    user_id = callback.from_user.id
    data = str(callback.data).replace("admin_edit_daily_q_day:", "")

    text = bd_get_one(f"SELECT week_day FROM admin_week_day WHERE week_day_id = '{data}'")
    await bot.edit_message_text(text, user_id, callback.message.message_id,
                                reply_markup=admin_count_daily_question_kb(data))


# Изменить вопросов в день обработчик нажатия знака
@dp.callback_query_handler(text_contains='admin_do_edit_daily_question')
async def admin_main_kb_new_q(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    user_id = callback.from_user.id

    # Обработчик callback
    data = str(callback.data).replace("admin_do_edit_daily_question:", "")
    sign = data[0]
    day_id = data[2]

    # Изменение значения
    question_daily = bd_get_one(f"SELECT question_daily FROM admin_week_day WHERE week_day_id = '{day_id}'")
    if sign == 'm':
        bd_set(f"UPDATE admin_week_day SET question_daily = '{question_daily - 1}' WHERE week_day_id = '{day_id}'")
    elif sign == "p":
        bd_set(f"UPDATE admin_week_day SET question_daily = '{question_daily + 1}' WHERE week_day_id = '{day_id}'")

    text = bd_get_one(f"SELECT week_day FROM admin_week_day WHERE week_day_id = '{day_id}'")
    await bot.edit_message_text(text, user_id, callback.message.message_id,
                                reply_markup=admin_count_daily_question_kb(day_id))


