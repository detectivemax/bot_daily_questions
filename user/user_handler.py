import asyncio
import datetime

from config.config import ADMIN_ID
from functions import bd_set, bd_get_one, bd_get_many, get_time, get_date
from main import bot, dp, types
from payment.payment import user_send_pay
from user.questions import QUESTIONS, ARTICLES, DAILY_PLAN

from user.user_kb import user_q_done_kb, user_reg_1_kb, user_reg_2_kb, user_reg_3_kb, user_reg_4_kb, user_reg_5_kb, \
    user_reg_6_kb, user_day_done_kb


# Выбор времени начала работы
@dp.callback_query_handler(text_contains='user_start_work')
async def user_set_time(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    user_id = callback.from_user.id
    data = str(callback.data).replace('user_start_work', '')

    stage = bd_get_one(f"SELECT stage_three FROM user_stage WHERE user_id == '{user_id}'")
    if stage == '1':
        question = get_question_text(user_id)

        check_trigger(user_id)
        bd_set(f"UPDATE user_stage SET stage_one = '{11}' WHERE user_id = '{user_id}'")
        await bot.send_message(user_id, question)


async def user_question_ans(message):
    user_id = message.from_user.id
    check_trigger(user_id)
    stage_one = int(bd_get_one(f"SELECT stage_one FROM user_stage WHERE user_id = '{user_id}'"))
    stage_two = int(bd_get_one(f"SELECT stage_two FROM user_stage WHERE user_id == '{user_id}'"))
    stage_three = int(bd_get_one(f"SELECT stage_three FROM user_stage WHERE user_id = '{user_id}'"))
    question = bd_get_one(f"SELECT plan FROM user_last_q WHERE user_id = '{user_id}'")
    question = stage_one - 10 + question

    if message.text == "👉 Следующий вопрос" and stage_two >= 5:
        bd_set(f"UPDATE user_stage SET stage_two = '{0}' WHERE user_id = '{user_id}'")
        bd_set(f"UPDATE user_stage SET stage_one = '{stage_one + 1}' WHERE user_id = '{user_id}'")

        question = QUESTIONS[str(question)]
        await bot.send_message(user_id, question, reply_markup=types.ReplyKeyboardRemove())

    else:
        bd_set(f"UPDATE user_stage SET stage_two = '{stage_two + 1}' WHERE user_id = '{user_id}'")
        daily_plan = DAILY_PLAN[str(stage_three % 7)]
        print(daily_plan)
        print(stage_two, stage_one, 10 + daily_plan)

        if stage_two + 1 >= 5 and stage_one < 10 + daily_plan:
            await bot.send_message(user_id, "Для следующего вопроса нажмите 'Следующий вопрос'",
                                   reply_markup=user_q_done_kb())

        elif stage_two + 1 >= 5 and stage_one >= 10 + daily_plan\
                and message.text == "👍 Завершить на сегодня":
            bd_set(f"UPDATE user_stage SET stage_three = '{int(stage_three) + 1}' WHERE user_id = '{user_id}'")
            bd_set(f"UPDATE user_stage SET stage_one = '{0}' WHERE user_id = '{user_id}'")
            bd_set(f"UPDATE user_stage SET stage_two = '{0}' WHERE user_id = '{user_id}'")
            bd_set(f"UPDATE user_last_q SET plan = '{question}' WHERE user_id = '{user_id}'")
            bd_set(f"UPDATE user_last_q SET time = '{0}' WHERE user_id = '{user_id}'")

            await bot.send_message(user_id, f"Ты закончил {stage_three} день из 200! Поздравляю!", reply_markup=types.ReplyKeyboardRemove())
            if int(stage_three) % 6 == 0:
                text = 'Ура неделя завершена мой командир! Цель все ближе!'
                await bot.send_message(user_id, text)

            user_paid = bd_get_one(f"SELECT paid FROM user_paid WHERE user_id == '{user_id}'")
            if stage_three == 10 and user_paid != 'true':
                await user_send_pay(user_id)

        elif stage_two + 1 >= 5 and stage_one >= 10 + daily_plan:
            await bot.send_message(user_id, "Вы ответили на все вопросы, нажмите "
                                            "'Завершить на сегодня' чтобы закончить день",
                                   reply_markup=user_day_done_kb())


# Ежедневные вопросы
async def user_daily_q(user_id):

    stage_three = int(bd_get_one(f"SELECT stage_three FROM user_stage WHERE user_id == '{user_id}'"))
    user_paid = bd_get_one(f"SELECT paid FROM user_paid WHERE user_id == '{user_id}'")

    if stage_three == 10 and user_paid != 'true':
        await user_send_pay(user_id)

    else:
        stage_three = int(bd_get_one(f"SELECT stage_three FROM user_stage WHERE user_id = '{user_id}'"))
        if stage_three % 7 == 0:
            article = ARTICLES[stage_three/7]
            bd_set(f"UPDATE user_stage SET stage_three = '{stage_three + 1}'")
            await bot.send_message(user_id, article)

        else:
            question = get_question_text(user_id)
            check_trigger(user_id)
            bd_set(f"UPDATE user_stage SET stage_one = '{11}' WHERE user_id = '{user_id}'")
            await bot.send_message(user_id, question)


def get_question_text(user_id):
    plan = str(bd_get_one(f"SELECT plan FROM user_last_q WHERE user_id = '{user_id}'"))
    return QUESTIONS[plan]


# Ежеминутная проверка
async def one_min_check():
    # Определение времени сейчас
    time_now = get_time()
    time_now_h = time_now[0:2]
    time_now_m = time_now[3:5]

    # Перебор всех пльзователей
    users = bd_get_many(f"SELECT user_id FROM user_stage")
    for user_id in users:

        user_reg_date = bd_get_one(f"SELECT date FROM user_register_date WHERE user_id = '{user_id}'")
        if user_reg_date != get_date():

            await afk_check(user_id)
            # Проверпка на время прохождения теста
            time = bd_get_one(f"SELECT time_to_get_mes FROM user_stage WHERE user_id = '{user_id}'")
            delta_time = bd_get_one(f"SELECT time_delta_msk FROM user_stage WHERE user_id = '{user_id}'")

            time_h = time[0:2]
            time_m = time[3:5]

            if int(time_h) + int(delta_time) == int(time_now_h) and time_m == time_now_m:
                await user_daily_q(user_id)

            # Проверка на последнюю активность

    when_to_call = loop.time() + delay  # delay -- промежуток времени в секундах.
    loop.call_at(when_to_call, my_callback)


def my_callback():
    asyncio.ensure_future(one_min_check())


delay = 60.0
loop = asyncio.get_event_loop()
my_callback()


# Trigger
def check_trigger(user_id):
    time_now = get_time()
    bd_set(f"UPDATE user_last_q SET time = '{time_now}' WHERE user_id = '{user_id}'")


# AFK check
async def afk_check(user_id):
    # 15 min check
    time = bd_get_one(f"SELECT time FROM user_last_q WHERE user_id = '{user_id}'")
    time_now = get_time()

    if str(time).find("first") != -1:
        time = str(time).replace("first:", "")
        time = datetime.timedelta(hours=int(time[0:2]), minutes=int(time[3:5]))
        time_now = datetime.timedelta(hours=int(time_now[0:2]), minutes=int(time_now[3:5]))

        if time_now - time >= datetime.timedelta(hours=2):
            await bot.send_message(user_id, "Вы не закончили отвечать на вопросы\n")
            bd_set(f"UPDATE user_last_q SET time = '{0}' WHERE user_id = '{user_id}'")

    elif time == "0":
        pass

    else:
        time = datetime.timedelta(hours=int(time[0:2]), minutes=int(time[3:5]))
        time_now = datetime.timedelta(hours=int(time_now[0:2]), minutes=int(time_now[3:5]))

        if time_now - time >= datetime.timedelta(minutes=15):
            await bot.send_message(user_id, "Вы не закончили отвечать на вопросы\n")
            bd_set(f"UPDATE user_last_q SET time = 'first:{time_now}' WHERE user_id = '{user_id}'")


# Обработчик стартового вопроса
async def user_start_question(user_id, data):
    data = data.split(":")
    q_number = data[1]

    if q_number == '5':
        # Сообщение 1
        text = "Отлично! Ты молодец, первый шаг на пути к самооценке бога уже сделан!" \
               " Теперь я подробнее объясню про метод и как с ним работать."
        await bot.send_message(user_id, text)

        # Аудио запись с описанием бота

        # Сообщение 2
        text_2 = "В основе метода незаконченных предложений, который используется в боте, лежат 6 основ," \
                 " 6 столпов, которые являются, фундаментом твоей самооценки." \
                 " А как мы знаем фундамент он всегда должен быть надежным, что бы и стены стояли и крыша не ехала)"
        await bot.send_message(user_id, text_2, reply_markup=user_reg_1_kb())

    bd_set(f"UPDATE user_stage SET stage_one = 'user_start_q:{int(q_number) + 1}' WHERE user_id = '{user_id}'")


# Обработка "Далее" после 1 сообщения
@dp.callback_query_handler(text_contains='user_reg_1')
async def user_set_time(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    user_id = callback.from_user.id
    bd_set(f"UPDATE user_stage SET stage_one = '0' WHERE user_id = '{user_id}'")

    text = "Теперь подробнее про эти 6 основ:\n" \
           "*Осознанность* - это жизнь с ответственностью по отношению к реальности." \
           " Принятие реальности такой какая она есть. Нам не обязательно нравится," \
           " то что мы видим или то, что с нами происходи, но мы признаем что это есть и не додумываем того чего нет." \
           " Наши страхи, отрицания или додумывания не меняют фактов." \
           " Осознанность нужна для того что бы понимать свое поведение и жизнь в целом." \
           " Что бы знать какие действия приносят результат, а какие его отдаляют." \
           " Какое поведение, отношения или люди нас заряжают, а какие истощают." \
           " Осознанность помогает лучше разбираться в людях в их мотивах и действиях." \
           " Практика осознанной жизни является первым столпом самооценки."

    await bot.send_message_text(user_id, text,
                                parse_mode=types.ParseMode.MARKDOWN, reply_markup=user_reg_2_kb())


# Обработка "Далее" после 2 сообщения
@dp.callback_query_handler(text_contains='user_reg_2')
async def user_set_time(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    user_id = callback.from_user.id

    text = 'Идем дальше, *Самопринятиe* - это отказ вступать в конфронтацию с собой.' \
           ' Самопринятие - это готовность о любых чувствах,' \
           ' эмоциях или поведении "Это выражение меня, не обязательно то выражение которое мне нравится,' \
           ' но это выражение меня в этот конкретный момент". Самое страшное,' \
           ' что мы можем убегать не только от наших темных проявлений,' \
           ' но так же и от нашего внутреннего величия, гениальности или амбиций.' \
           ' Самопринятие является необходимым условием для роста и развития.' \
           ' Практика самопринятия это второй столп самооценки'

    await bot.send_message_text(user_id, text,
                                parse_mode=types.ParseMode.MARKDOWN, reply_markup=user_reg_3_kb())


# Обработка "Далее" после 3 сообщения
@dp.callback_query_handler(text_contains='user_reg_3')
async def user_set_time(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    user_id = callback.from_user.id

    text = 'Дальше у нас идет *Самоответственность. Самоответсвенность означает то*' \
           ' что ты несешь ответственность за все,' \
           ' что происходит в твоей жизни.' \
           ' Несешь ответственность за результат своих действий, за свои ошибки, за свое счастье.' \
           ' Никто не обязан выполнять твои желания.' \
           ' Самоответственность всегда выражается в активной жизненной позиции и независимости мышления.' \
           ' Ты всегда живешь своим умом. Практика самоответственности является третим столпом самооценки.'

    await bot.send_message_text(user_id, text,
                                parse_mode=types.ParseMode.MARKDOWN, reply_markup=user_reg_4_kb())


# Обработка "Далее" после 4 сообщения
@dp.callback_query_handler(text_contains='user_reg_4')
async def user_set_time(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    user_id = callback.from_user.id

    text = '*Cамооутверждение* - это признание своих и уважение своих желаний,' \
           ' потребностей и ценностей и умение выражать их в подходящей форме.' \
           ' Самоутверждение это готовность постоять за себя, открыто быть собой настоящим,' \
           ' не притворяясь кем то другим, ради того что бы тебя одобряли или любили.' \
           ' Задавать вопросы докапываясь до сути, бросать вызов устоям,' \
           ' всегда думать за себя и стоять на том что думаешь это все акты самоутверждения!' \
           ' А пренебрегать всем этим - наносить ущерб самооценке на самом базовом уровне.' \
           ' Практика самоутверждения - четвертый столп самооценки.'

    await bot.send_message_text(user_id, text,
                                parse_mode=types.ParseMode.MARKDOWN, reply_markup=user_reg_5_kb())


# Обработка "Далее" после 5 сообщения
@dp.callback_query_handler(text_contains='user_reg_5')
async def user_set_time(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    user_id = callback.from_user.id

    text = '*Целенаправленная жизнь* - означает жить продуктивно, ставить адекватные,' \
           ' достижимы на данный момент цели и достигать их, попутно повышая свою самооценку.' \
           ' Но важно всегда осознанно подходить к целям и их постановке,' \
           ' не стоит полагаться на навязанные обществом стереотипы мышления, лучше слушать себя.' \
           ' Так жизнь станет увлекательнее и ярче. Не забывай вносить корректировки на пути к цели,' \
           ' не всегда изначальный план бывает идеальным. ' \
           'Практика целенаправленной жизни является пятым столпом самооценки.'

    await bot.send_message_text(user_id, text,
                                parse_mode=types.ParseMode.MARKDOWN, reply_markup=user_reg_6_kb())


# Обработка "Далее" после 6 сообщения
@dp.callback_query_handler(text_contains='user_reg_6')
async def user_set_time(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    user_id = callback.from_user.id

    text = '*Личная целостность*\n' \
           'Это жить согласованно со своими убеждениями, ценностями, принципами и моделями поведения.' \
           ' Когда мы поступаем так, что это противоречит нашим моральным устоям и убеждениям,' \
           ' мы начинаем меньше себя уважать. Если поступаем так часто, то это входит в привычку.' \
           ' Когда мы исследуем свою жизнь мы часто находим такие несоответствия,' \
           ' обычно мы их просто пропускаем по привычке. В программе мы как раз займемся таким исследование)\n' \
           'Практика целостности - это шестой столп самооценки.\n\n' \
           'Фуух выдохнули.\n\n' \
           'В боте мы постепенно раскрываем и прокачиваем каждый столп самооценки.' \
           ' Уже через пару недель ты узнаешь о себе много нового, появятся новые мысли,' \
           ' улучшится концентрация, и осознанность. И это всего за 7 минут в день!'

    await bot.send_message_text(user_id, text, parse_mode=types.ParseMode.MARKDOWN)

    text_2 = "Важно закачивать предложения быстро! Не надо сидеть размышлять или гуглить (да да бывает и так)." \
             " Пиши первое что приходит в голову, главное что бы подходило по смыслу." \
             " Нужно написать от 6 до 10 ответов на предложение и переходить к следующему вопросу."
    await bot.send_message(user_id, text_2)

    text_3 = 'P.S. Все твои ответы защищены специальным шифрованием их видишь только ты,' \
             ' поэтому пиши честно, все что идет изнутри.   Желаю удачи, мира и любви тебе! Еще увидимся)'
    await bot.send_message(user_id, text_3)

    text_4 = "Выбери время когда тебе, будет удобно работать с ботом!" \
             " Он будет отправлять тебе сообщения каждый день в одно и то же время."
    await bot.send_message(user_id, text_4)
    from comands_handlers import register_time
    await register_time(user_id)


