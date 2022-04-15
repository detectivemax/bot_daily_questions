from admin.admin_start_mes import send_all
from comands_handler_kb import admin_main_kb, user_ready_kb, user_set_time_kb, user_set_work_start_kb, \
    user_start_work_kb
from config.config import ADMIN_ID, ADMIN_2_ID
from functions import bd_get_one, bd_set, get_time, get_date
from main import bot, dp, types


# Обработчик команды 'Start'
from user.user_handler import user_daily_q


@dp.message_handler(commands=['start'])
async def send_welcome(message):
    user_id = message.from_user.id

    check = bd_get_one(f"SELECT user_id FROM user_stage WHERE user_id = '{user_id}' AND time_to_get_mes != '{0}'")
    if check is None:
        check = bd_get_one(f"SELECT user_id FROM user_stage WHERE user_id = '{user_id}'")
        if check is None:
            await send_all(user_id)
            bd_set(f"INSERT INTO user_stage VALUES('{user_id}', 'user_start_q:0', '{0}', '{1}', '{0}', '{0}')")
            bd_set(f"INSERT INTO user_last_q VALUES('{user_id}', '{1}', '{0}')")
            bd_set(f"INSERT INTO user_register_date VALUES('{user_id}', '{get_date()}')")

    else:
        # Проверка на наличие дней недели
        check = bd_get_one(f"SELECT week_day_id FROM admin_week_day WHERE week_day_id = '{6}'")
        if check is None:
            bd_set(f"INSERT INTO admin_week_day VALUES('{0}', 'Понедельник', '{6}')")
            bd_set(f"INSERT INTO admin_week_day VALUES('{1}', 'Вторник', '{6}')")
            bd_set(f"INSERT INTO admin_week_day VALUES('{2}', 'Среда', '{6}')")
            bd_set(f"INSERT INTO admin_week_day VALUES('{3}', 'Четверг', '{6}')")
            bd_set(f"INSERT INTO admin_week_day VALUES('{4}', 'Пятница', '{6}')")
            bd_set(f"INSERT INTO admin_week_day VALUES('{5}', 'Суббота', '{6}')")
            bd_set(f"INSERT INTO admin_week_day VALUES('{6}', 'Воскресенье', '{6}')")

        # Проверка на администратора
        if str(user_id) == ADMIN_ID or str(user_id) == ADMIN_2_ID:
            await bot.send_message(user_id, 'Открыта панель администратора', reply_markup=admin_main_kb())


async def register_time(user_id):
    text = f"*Выберите часовой пояс:*\n\n" \
           f"Время в Москве: {get_time()}\n" \
           f"Ваше время: {get_time()} "

    await bot.send_message(user_id, text, reply_markup=user_set_time_kb(0), parse_mode=types.ParseMode.MARKDOWN)


# Выбор времени
@dp.callback_query_handler(text_contains='user_set_time:')
async def user_set_time(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    user_id = callback.from_user.id
    data = str(callback.data).replace('user_set_time:', '')

    # Текущая разница во вреени
    time_delta_msk = bd_get_one(f"SELECT time_delta_msk FROM user_stage WHERE user_id = '{user_id}'")

    if data == 'minus':
        time_delta_msk -= 1

    elif data == 'plus':
        time_delta_msk += 1

    else:
        pass

    if data != "done":
        text = f"*Выберите часовой пояс:*\n\n" \
               f"Время в Москве: {get_time()}\n" \
               f"Ваше время: {get_time(time_delta_msk)} "

        bd_set(f"UPDATE user_stage SET time_delta_msk = '{time_delta_msk}' WHERE user_id = '{user_id}'")

        await bot.edit_message_text(text, user_id, callback.message.message_id,
                                    reply_markup=user_set_time_kb(time_delta_msk),
                                    parse_mode=types.ParseMode.MARKDOWN)

    elif data == "done":
        text = f"В какое время вам будет удобно получать сообщения?"

        await bot.edit_message_text(text, user_id, callback.message.message_id,
                                    reply_markup=user_set_work_start_kb(10, 30),
                                    parse_mode=types.ParseMode.MARKDOWN)


# Выбор времени начала работы
@dp.callback_query_handler(text_contains='user_set_work_start:')
async def user_set_time(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    user_id = callback.from_user.id
    data = str(callback.data).replace('user_set_work_start:', '')

    # Нажате на Подтвердить
    if data.find("done") > -1:
        hour = data[0:2]
        print(hour)
        data = data[3::]
        minute = data[0:2]
        print(minute)
        bd_set(f"UPDATE user_stage SET time_to_get_mes = '{hour}:{minute}' WHERE user_id = '{user_id}'")
        await bot.edit_message_text("Отлично! Мы начинаем завтра!",
                                    user_id, callback.message.message_id,
                                    parse_mode=types.ParseMode.MARKDOWN)

    # Нажадие на цифру
    elif data.find("pass") > -1:
        pass

    # Нажатие на +-
    else:
        group = data[0]
        data = data[2::]
        hour = int(data[0:2])
        data = data[3::]
        minute = int(data[0:2])
        sign = data[3::]

        # Редактирование часов
        if group == 'h':
            if sign == 'plus':
                hour = hour + 1

            elif sign == "minus":
                hour = hour - 1

            if hour == 24:
                hour = 0

            hour = str(hour)
            if len(hour) == 1:
                hour = f"0{hour}"

        # Редактирование минут
        if group == 'm':
            if sign == 'plus':
                minute = minute + 10

            elif sign == "minus":
                minute = minute - 10

            if minute == 60:
                minute = 0

            minute = str(minute)
            if len(minute) == 1:
                minute = f"0{minute}"

        text = f"В какое время вам будет удобно получать сообщения?"
        await bot.edit_message_text(text, user_id, callback.message.message_id,
                                    reply_markup=user_set_work_start_kb(hour, minute),
                                    parse_mode=types.ParseMode.MARKDOWN)


# Pass
@dp.callback_query_handler(text_contains='pass')
async def admin_main_kb_new_q(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)