from aiogram.utils.exceptions import TypeOfFileMismatch

from admin.admin_kb import admin_new_user_kb, admin_new_user_actions_kb, start_message_kb
from comands_handler_kb import admin_main_kb
from config.config import ADMIN_ID, BOT_TOKEN
from functions import bd_set, max_task_id, bd_get_many, bd_get_one
from main import bot, dp, types


# Настройка стартовых сообщений
@dp.callback_query_handler(text_contains='admin_start_mes')
async def admin_main_kb_new_q(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    user_id = callback.from_user.id

    check = bd_get_many(f"SELECT mes_id FROM user_start_mes")

    if not check:
        for i in range(10):
            bd_set(f"INSERT INTO user_start_mes VALUES('{i}', 'None', 'None', 'None')")

    await bot.send_message(user_id, 'Сообщения для новых пользователей:', reply_markup=admin_new_user_kb())


# Просмотр сообщения
@dp.callback_query_handler(text_contains='admin_new_user_mes:')
async def admin_main_kb_new_q(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    user_id = callback.from_user.id
    data = str(callback.data).replace("admin_new_user_mes:", "")

    # Получение данных о сообщении
    caption = bd_get_one(f"SELECT caption FROM user_start_mes WHERE mes_id == '{data}'")
    file = bd_get_one(f"SELECT file FROM user_start_mes WHERE mes_id == '{data}'")

    # [ПУСТО]
    if caption == 'None' and file == 'None':
        await bot.send_message(user_id, 'Сообщение отсутствует')

    # Текстовое сообщение
    elif file == 'None':
        await bot.send_message(user_id, caption, reply_markup=start_message_kb(data))

    # Только файл
    elif caption == 'None':
        try:
            await bot.send_document(user_id, file, reply_markup=start_message_kb(data))
        except TypeOfFileMismatch:
            await bot.send_photo(user_id, file, reply_markup=start_message_kb(data))

    # И файл и текст
    else:
        try:
            await bot.send_document(user_id, file, caption=caption, reply_markup=start_message_kb(data))

        except TypeOfFileMismatch:
            print(file)
            print(caption)
            await bot.send_photo(user_id, file, caption=caption, reply_markup=start_message_kb(data))

    await bot.send_message(user_id, 'Возможные действия:', reply_markup=admin_new_user_actions_kb(data))


# Добавить сообщение
@dp.callback_query_handler(text_contains='admin_new_user_add_mes:')
async def admin_new_user_add_mes(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    user_id = callback.from_user.id
    data = str(callback.data).replace("admin_new_user_add_mes:", "")

    bd_set(f"UPDATE user_stage SET stage_one = 'admin_start_mes:{data}' WHERE user_id = '{user_id}'")
    await bot.send_message(user_id, "Отправьте сообщение:")


# Сохранение сообщения:
async def admin_new_user_save_mes(message, mes_id):
    user_id = message.from_user.id

    try:
        await bot.send_document(user_id, message.document.file_id,
                                caption=message.caption)
        bd_set(f"UPDATE user_start_mes SET file = '{message.document.file_id}' WHERE mes_id = '{mes_id}'")
        if message.caption != "":
            bd_set(f"UPDATE user_start_mes SET caption = '{message.caption}' WHERE mes_id = '{mes_id}'")

    except AttributeError:
        try:
            await bot.send_photo(user_id, message.photo[-1].file_id,
                                 caption=message.caption)
            bd_set(f"UPDATE user_start_mes SET file = '{message.photo[-1].file_id}' WHERE mes_id = '{mes_id}'")
            if message.caption != "":
                bd_set(f"UPDATE user_start_mes SET caption = '{message.caption}' WHERE mes_id = '{mes_id}'")

        except IndexError:
            await bot.send_message(user_id, message.text)
            bd_set(f"UPDATE user_start_mes SET caption = '{message.text}' WHERE mes_id = '{mes_id}'")

    bd_set(f"UPDATE user_stage SET stage_one = '{0}' WHERE user_id = '{user_id}'")

    text = "Сообщение сохранено\n" \
           "Возможные действия:"
    await bot.send_message(message.from_user.id, text, reply_markup=admin_new_user_actions_kb(mes_id))


# Удалить сообщение
@dp.callback_query_handler(text_contains='admin_new_user_del_mes:')
async def admin_new_user_add_mes(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    user_id = callback.from_user.id
    data = str(callback.data).replace("admin_new_user_del_mes:", "")

    bd_set(f"UPDATE user_start_mes SET caption = 'None' WHERE mes_id = '{data}'")
    bd_set(f"UPDATE user_start_mes SET file = 'None' WHERE mes_id = '{data}'")
    bd_set(f"UPDATE user_start_mes SET button = 'None' WHERE mes_id = '{data}'")

    await bot.send_message(user_id, 'Сообщение удалено')


# admin_new_user_edit_text
@dp.callback_query_handler(text_contains='admin_new_user_edit_text:')
async def admin_new_user_edit_text(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    user_id = callback.from_user.id
    data = str(callback.data).replace("admin_new_user_edit_text:", "")

    bd_set(f"UPDATE user_stage SET stage_one = 'admin_new_user_edit_text:{data}' WHERE user_id = '{user_id}'")
    await bot.send_message(user_id, "Отправьте новый текст:")


# Сохранить новый текст
async def admin_new_user_edit_text_save(message, data):
    user_id = message.from_user.id
    bd_set(f"UPDATE user_start_mes SET caption = '{message.text}' WHERE mes_id = '{data}'")

    bd_set(f"UPDATE user_stage SET stage_one = '{0}' WHERE user_id = '{user_id}'")
    await bot.send_message(user_id, "Новый тест сохранён")


# admin_new_user_edit_file
@dp.callback_query_handler(text_contains='admin_new_user_edit_file:')
async def admin_new_user_edit_file(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    user_id = callback.from_user.id
    data = str(callback.data).replace("admin_new_user_edit_file:", "")

    bd_set(f"UPDATE user_stage SET stage_one = 'admin_new_user_edit_file:{data}' WHERE user_id = '{user_id}'")
    await bot.send_message(user_id, "Отправьте новое приложение:")


# Сохранить новый текст
async def admin_new_user_edit_file_save(message, data):
    user_id = message.from_user.id
    data = str(data).replace("admin_new_user_edit_file:", "")

    try:
        bd_set(f"UPDATE user_start_mes SET file = '{message.document.file_id}' WHERE mes_id = '{data}'")
    except AttributeError:
        bd_set(f"UPDATE user_start_mes SET file = '{message.photo[-1].file_id}' WHERE mes_id = '{data}'")

    bd_set(f"UPDATE user_stage SET stage_one = '{0}' WHERE user_id = '{user_id}'")
    await bot.send_message(user_id, "Новое приложение сохранено")


# Редактировать кнопки
@dp.callback_query_handler(text_contains='admin_new_user_edit_button:')
async def admin_new_user_edit_button(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    user_id = callback.from_user.id
    data = str(callback.data).replace("admin_new_user_edit_button:", "")

    bd_set(f"UPDATE user_stage SET stage_one = 'admin_new_user_edit_button:{data}' WHERE user_id = '{user_id}'")
    await bot.send_message(user_id, "Отправьте содержимое кнопок в формате:\n"
                                    "Текст кнопки : ссылка")


# Сохранить новые кнопки
async def admin_new_user_edit_button_save(message, data):
    user_id = message.from_user.id
    data = str(data).replace("admin_new_user_edit_file:", "")

    bd_set(f"UPDATE user_start_mes SET button = '{message.text}' WHERE mes_id = '{data}'")

    bd_set(f"UPDATE user_stage SET stage_one = '{0}' WHERE user_id = '{user_id}'")
    await bot.send_message(user_id, "Новая клавиатура сохранена")


# Отправить все стартовые сообщения
async def send_all(user_id):
    mes_list = bd_get_many(f"SELECT mes_id FROM user_start_mes")
    for mes_id in mes_list:
        caption = bd_get_one(f"SELECT caption FROM user_start_mes WHERE mes_id == '{mes_id}'")
        file = bd_get_one(f"SELECT file FROM user_start_mes WHERE mes_id == '{mes_id}'")

        if caption != "None" or file != "None":

            data = mes_id

            # Получение данных о сообщении
            caption = bd_get_one(f"SELECT caption FROM user_start_mes WHERE mes_id == '{data}'")
            file = bd_get_one(f"SELECT file FROM user_start_mes WHERE mes_id == '{data}'")

            # [ПУСТО]
            if caption == 'None' and file == 'None':
                await bot.send_message(user_id, 'Сообщение отсутствует')

            # Текстовое сообщение
            elif file == 'None':
                await bot.send_message(user_id, caption, reply_markup=start_message_kb(data))

            # Только файл
            elif caption == 'None':
                try:
                    await bot.send_document(user_id, file, reply_markup=start_message_kb(data))
                except TypeOfFileMismatch:
                    await bot.send_photo(user_id, file, reply_markup=start_message_kb(data))

            # И файл и текст
            else:
                try:
                    await bot.send_document(user_id, file, caption=caption, reply_markup=start_message_kb(data))

                except TypeOfFileMismatch:
                    await bot.send_photo(user_id, file, caption=caption, reply_markup=start_message_kb(data))
