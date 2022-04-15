import sqlite3
import openpyxl


connect = sqlite3.connect('data_2.db')
cursor = connect.cursor()


# question
cursor.execute("""CREATE TABLE IF NOT EXISTS question(
        q_id INTEGER,
        question TEXT
    )""")


# User_stage
cursor.execute("""CREATE TABLE IF NOT EXISTS user_stage(
        user_id INTEGER,
        stage_one TEXT,
        stage_two TEXT,
        stage_three TEXT,
        time_delta_msk INTEGER,
        time_to_get_mes TEXT
    )""")


# user_register_date
cursor.execute("""CREATE TABLE IF NOT EXISTS user_register_date(
        user_id INTEGER,
        date TEXT
    )""")


# question
cursor.execute("""CREATE TABLE IF NOT EXISTS user_last_q(
        user_id INTEGER,
        plan INTEGER,
        time TEXT
    )""")


# star question
cursor.execute("""CREATE TABLE IF NOT EXISTS user_start_mes(
        mes_id INTEGER,
        caption TEXT,
        file TEXT,
        button TEXT
    )""")


# week day
cursor.execute("""CREATE TABLE IF NOT EXISTS admin_week_day(
        week_day_id INTEGER,
        week_day TEXT,
        question_daily INTEGER
    )""")