from admin.admin_handler import admin_main_kb_new_q_get
from admin.admin_start_mes import admin_new_user_save_mes, admin_new_user_edit_text_save, admin_new_user_edit_file_save, \
    admin_new_user_edit_button_save
from functions import bd_get_one
from main import bot, dp, types
from user.user_handler import user_question_ans, user_start_question


@dp.message_handler(content_types=['text', 'photo', 'document'])
async def send_text(message):
    user_id = message.from_user.id
    stage_one = str(bd_get_one(f"SELECT stage_one FROM user_stage WHERE user_id = '{user_id}'"))

    if stage_one == '1':
        await admin_main_kb_new_q_get(message)

    # Отправка стартовогго сообщения
    elif str(stage_one).find("admin_start_mes") != -1:
        stage_one = str(stage_one).replace('admin_start_mes:', "")
        await admin_new_user_save_mes(message, stage_one)

    # Редактирование текста стартового сообщения
    elif str(stage_one).find("admin_new_user_edit_text") != -1:
        stage_one = str(stage_one).replace('admin_new_user_edit_text:', "")
        await admin_new_user_edit_text_save(message, stage_one)

    # редактирование приложения стартового сообщения
    elif str(stage_one).find("admin_new_user_edit_file") != -1:
        stage_one = str(stage_one).replace('admin_new_user_edit_text:', "")
        await admin_new_user_edit_file_save(message, stage_one)

    # редактирование кнопок стартового сообщения
    elif str(stage_one).find("admin_new_user_edit_button") != -1:
        stage_one = str(stage_one).replace('admin_new_user_edit_button:', "")
        await admin_new_user_edit_button_save(message, stage_one)

    elif stage_one.find("user_start_q") != -1:
        await user_start_question(user_id, stage_one)

    # Имя пользователя
    elif 10 <= int(stage_one) <= 25:
        await user_question_ans(message)



