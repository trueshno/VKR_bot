import telebot
from fuzzywuzzy import fuzz
import sqlite3

bot = telebot.TeleBot('6620987116:AAGYKX-C3q2oMi-gY2oHc9yPVRlBRt5A1Xw')
conn = sqlite3.connect('db/database.db', check_same_thread=False)
cursor = conn.cursor()

mas = []

# С помощью fuzzywuzzy вычисляем наиболее похожую фразу и выдаем в качестве ответа следующий элемент списка
def answer(text):
    cursor.execute("SELECT user_input, text FROM info")
    rows = cursor.fetchall()

    max_score = 0
    best_match = None

    for row in rows:
        user_input = row[0]
        question_text = row[1]

        score = fuzz.ratio(text, user_input)
        if score > max_score:
            max_score = score
            best_match = question_text

    if max_score > 80:
        return best_match
    else:
        return "Ответ не найден"
