import sqlite3
import telebot
import random
from telebot import types
from fuzzywuzzy import fuzz
from fluzzy import answer
from app import app
from itertools import count

bot = telebot.TeleBot("6620987116:AAGYKX-C3q2oMi-gY2oHc9yPVRlBRt5A1Xw")
conn = sqlite3.connect('db/database.db', check_same_thread=False)
cursor = conn.cursor()

def db_table_val(user_id: int, user_name: str, username: str):
    cursor.execute('INSERT OR REPLACE INTO user_info (user_id, user_name, username) VALUES (?, ?, ?)',
                   (user_id, user_name, username))
    conn.commit()

@bot.message_handler(commands=['panel'])
def handle_panel(message):
    if message.from_user.id == 1220363667:
        bot.reply_to(message, "Flask-приложение запущено по адресу: \nhttp://127.0.0.1:5000")
        app.run()
    else:
        bot.reply_to(message, "У вас нет прав для запуска")

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Добро пожаловать')
    us_id = message.from_user.id
    us_name = message.from_user.first_name
    username = message.from_user.username

    db_table_val(user_id=us_id, user_name=us_name, username=username)
    phone_added = False  # Флаг, указывающий, был ли номер телефона добавлен

    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_send = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
    button_skip = types.KeyboardButton(text="Не отправлять номер")
    keyboard.add(button_send, button_skip)
    bot.send_message(message.chat.id, "Пожалуйста, отправьте ваш номер телефона.", reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.contact is not None)
def handle_contact_result(message):
        global phone_added
        phone_added = True
        bot.send_message(message.chat.id, 'Номер телефона успешно добавлен.')

@bot.message_handler(commands=['newsletter'])
def newsletter_message(message):
    if message.from_user.id == 1220363667:
        bot.reply_to(message, "Введите текст рассылки:")
        bot.register_next_step_handler(message, confirm_newsletter_text)
    else:
        bot.reply_to(message, "У вас нет прав для рассылки")

def confirm_newsletter_text(message):
    text = message.text
    bot.reply_to(message, f"Текст рассылки:\n{text}\n\nПодтвердите отправку рассылки (да/нет):")
    bot.register_next_step_handler(message, handle_confirmation, text)

def handle_confirmation(message, text):
    confirmation = message.text.lower()
    if confirmation == "да":
        cursor.execute("SELECT user_id FROM user_info")
        users = cursor.fetchall()
        for user in users:
            try:
                bot.send_message(user[0], text)
            except Exception as e:
                print(e)
        bot.reply_to(message, "Рассылка выполнена")
    elif confirmation == "нет":
        bot.reply_to(message, "Отправка рассылки отменена")
    else:
        bot.reply_to(message, "Некорректный ответ. Пожалуйста, введите 'да' или 'нет'.")

question_count = count()


def get_next_question(message):
    global question_count

    cursor.execute('SELECT question FROM test_questions')
    questions = cursor.fetchall()

    try:
        if next(question_count) < 14:
            return questions[next(question_count)][0]
        else:
            cursor.execute("SELECT result_text, count FROM test")
            results = cursor.fetchall()
            if results:
                result_text, result_count = random.choice(results)
                if result_count is None:
                    result_count = 0
                bot.send_message(message.chat.id, "Ваша наиболее подходящая специальность:")
                bot.send_message(message.chat.id, result_text)

                # Увеличить счетчик для выбранного результата
                cursor.execute("UPDATE test SET count = ? WHERE result_text = ?", (result_count + 1, result_text))
                conn.commit()
                # После отправки результата, начать новый опрос
                question_count = count()
                if next(question_count) < 14:
                    return questions[next(question_count)][0]
    except IndexError:
        question_count = count()
        if next(question_count) < 14:
            return questions[next(question_count)][0]
        else:
            cursor.execute("SELECT result_text, count FROM test")
            results = cursor.fetchall()
            if results:
                result_text, result_count = random.choice(results)
                if result_count is None:
                    result_count = 0
                bot.send_message(message.chat.id, "Ваша наиболее подходящая специальность:")
                bot.send_message(message.chat.id, result_text)

                # Увеличить счетчик для выбранного результата
                cursor.execute("UPDATE test SET count = ? WHERE result_text = ?", (result_count + 1, result_text))
                conn.commit()
                # После отправки результата, начать новый опрос
                question_count = count()
                if next(question_count) < 14:
                    return questions[next(question_count)][0]

def process_answer(message, question):
    answer = message.text

    # Проверка, что ответ находится в диапазоне от 1 до 4
    if not answer.isdigit() or int(answer) < 1 or int(answer) > 4:
        bot.send_message(message.chat.id, "Пожалуйста, введите число от 1 до 4.")
        bot.register_next_step_handler(message, process_answer, question)
        return

    # Получить новый вопрос
    new_question = get_next_question(message)

    # Сохранить ответ
    cursor.execute("""
    INSERT INTO test_answers 
      (user_id, question, answer)
    VALUES 
      (?, ?, ?)
    """, (message.from_user.id, question, answer))
    conn.commit()

    if len(new_question) > 1:
        bot.send_message(message.chat.id, f"{new_question}")

        bot.register_next_step_handler(message, process_answer, new_question)

@bot.message_handler(commands=['menu'])
def website(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        btn1 = types.KeyboardButton('Наши соцсети')
        btn2 = types.KeyboardButton('Специальности')
        btn3 = types.KeyboardButton('Часто задаваемые вопросы')
        btn4 = types.KeyboardButton('Проходные баллы')
        btn5 = types.KeyboardButton('Тест на специальность')
        markup.add(btn1, btn2, btn3, btn4, btn5)
        first_mess = f'Привет, {message.from_user.first_name}'
        sent_message = bot.send_message(message.chat.id, first_mess, parse_mode="html", reply_markup=markup)

@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    phone_number = message.contact.phone_number
    user_id = message.from_user.id

    # Сохранение номера телефона в базу данных
    cursor.execute('INSERT OR REPLACE INTO contacts (user_id, phone_number) VALUES (?, ?)', (user_id, phone_number))
    conn.commit()

    bot.send_message(message.chat.id, "Номер телефона успешно добавлен.")

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text.lower() == 'привет':
        bot.send_message(message.chat.id, 'Привет! Я постараюсь ответить на твои вопросы!')

    elif message.text.lower() == 'тест на специальность':
        chat_id = message.chat.id
        question = get_next_question(message)

        bot.send_message(chat_id, f"Отвечайте пожалуйста на вопросы численно, где 4 - полностью согласен, а 1 - совсем не согласен")
        bot.send_message(chat_id, f"{question}")

        bot.register_next_step_handler(message, process_answer, question)

    elif message.text.lower() == "наши соцсети":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Посетите наш сайт", url="http://ief.bru.by/"))
        markup.add(types.InlineKeyboardButton("Посетите наш TikTok", url="https://www.tiktok.com/@iefbru?_t=8c2lAB9mfNW&_r=1"))
        markup.add(types.InlineKeyboardButton("Посетите наш Instagram", url="https://www.instagram.com/ief_bru/?igshid=YmMyMTA2M2Y%3D"))
        markup.add(types.InlineKeyboardButton("Посетите наш Telegram", url="https://t.me/iefbru"))

        bot.send_message(message.chat.id, 'Следи за нами в соцсетях', parse_mode="html", reply_markup=markup)

    elif message.text.lower() == "проходные баллы":
        doc = open('ball_2022_1.pdf', 'rb')
        markup = types.InlineKeyboardMarkup()
        bot.send_message(message.chat.id, "В файле предоставлена актуальная информация о проходных баллах:")
        bot.send_document(message.chat.id, doc)

    elif message.text.lower() == "специальности":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton('Инноватика')
        btn2 = types.KeyboardButton('Зарубежное регионоведение')
        btn3 = types.KeyboardButton('Программная инженерия')
        btn4 = types.KeyboardButton('Информатика и вычислительная техника')
        btn5 = types.KeyboardButton('Прикладная механика')
        next = types.KeyboardButton('Далее')
        menu = types.KeyboardButton('Главное меню')

        markup.add(btn1, btn2, btn3, btn4, btn5, next, menu)
        bot.send_message(message.chat.id, "Выбери специальность, чтобы узнать немного больше о ней:", parse_mode="html", reply_markup=markup)

    elif message.text.lower() == "далее":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn6 = types.KeyboardButton('Мехатроника и робототехника')
        btn7 = types.KeyboardButton('Биотехнические системы и технологии')
        btn8 = types.KeyboardButton('Прикладная математика')
        btn9 = types.KeyboardButton('Машиностроение')
        btn10 = types.KeyboardButton('Электроэнергетика и электротехника')
        btn11 = types.KeyboardButton('Нефтегазовое дело')
        btn12 = types.KeyboardButton('Бизнес-информатика')
        back = types.KeyboardButton('Назад')

        markup.add(btn6, btn7, btn8, btn9, btn10, btn11, btn12, back)
        bot.send_message(message.chat.id, "Выбери специальность, чтобы узнать немного больше о ней:", parse_mode="html", reply_markup=markup)

    elif message.text.lower() == "назад":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton('Инноватика')
        btn2 = types.KeyboardButton('Зарубежное регионоведение')
        btn3 = types.KeyboardButton('Программная инженерия')
        btn4 = types.KeyboardButton('Информатика и вычислительная техника')
        btn5 = types.KeyboardButton('Прикладная механика')
        next = types.KeyboardButton('Далее')
        menu = types.KeyboardButton('Главное меню')

        markup.add(btn1, btn2, btn3, btn4, btn5, next, menu)
        bot.send_message(message.chat.id, "Выбери специальность, чтобы узнать немного больше о ней:", parse_mode="html", reply_markup=markup)

    elif message.text.lower() == "часто задаваемые вопросы":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton('Какой я получу диплом?')
        btn2 = types.KeyboardButton('Предоставляется ли общежитие?')
        btn3 = types.KeyboardButton('Какой срок обучения?')
        btn4 = types.KeyboardButton('Какой размер стипендии?')
        btn5 = types.KeyboardButton('Какая стоимость обучения?')
        btn6 = types.KeyboardButton('Схема расположения корпусов')
        btn7 = types.KeyboardButton('Другой вопрос')

        markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
        bot.send_message(message.chat.id, "Выбери интересующий тебя вопрос:", parse_mode="html", reply_markup=markup)

    elif message.text.lower() == "какой размер стипендии?":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton('Часто задаваемые вопросы')
        menu = types.KeyboardButton('Главное меню')
        markup.add(btn1, menu)
        grant = open('images/grant.png', 'rb')
        bot.send_message(message.chat.id, "Размеры стипендий для студентов, обучающихся по образовательным программам Российской Федерации (российских рублей):", reply_markup=markup)
        bot.send_document(message.chat.id, grant)

    elif message.text.lower() == "какая стоимость обучения?":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton('Часто задаваемые вопросы')
        menu = types.KeyboardButton('Главное меню')
        markup.add(btn1, menu)
        tuition_fees = open('images/tuition_fees.png', 'rb')
        bot.send_message(message.chat.id, 'Дополнительная информация об оплате обучения по телефону +375222713976', reply_markup=markup)
        bot.send_document(message.chat.id, tuition_fees)

    elif message.text.lower() == "схема расположения корпусов":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton('Часто задаваемые вопросы')
        menu = types.KeyboardButton('Главное меню')
        markup.add(btn1, menu)
        bot.send_message(message.chat.id, 'В настоящее время в состав Белорусско-Российский университета входят лицей, архитектурно-строительный колледж, 7 учебно-лабораторных корпуса и 4 общежития:', reply_markup=markup)
        bot.send_document(message.chat.id, 'http://cdn.bru.by/cache/university/sheme/map_big_2019_2.jpg')

    elif message.text.lower() == "главное меню":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        btn1 = types.KeyboardButton('Наши соцсети')
        btn2 = types.KeyboardButton('Специальности')
        btn3 = types.KeyboardButton('Часто задаваемые вопросы')
        btn4 = types.KeyboardButton('Проходные баллы')

        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(message.chat.id, "Ты вернулся в главное меню", parse_mode="html", reply_markup=markup)

    # Отправка ответов на вопросы в соответствии с вопросами пользователя
    else:
        user_input = message.text
        reply = answer(message.text)
        bot.send_message(message.chat.id, reply)

        cursor.execute('SELECT * FROM info WHERE user_input=?', (message.text,))
        rows = cursor.fetchall()
        # if rows:
        #     result = '\n'.join([f'{row[2]}' for row in rows])
        #     bot.send_message(message.chat.id, result)
        # else:
        #     pass

bot.polling(none_stop=True)