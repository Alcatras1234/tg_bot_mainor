import datetime
import telebot
import json
import time
from telebot import types
from pymongo import MongoClient

cluster = MongoClient("mongodb://localhost:27017") # да прописано тут, мне так проще

db = cluster["db_tg_bot"]
collection = db["tg_bot"]



bot_api = telebot.TeleBot('6699558777:AAE0uFXq5M1jlQVBkCj3751EB6Ap0vEI5E8') # тут лежит т.к. ssh ключ от сервера лежит на компе
audio_clicks = 0
text_clicks = 0
buy_clicks = 0
name = ""

id = 0


data = {  # JSON'ка для сохранения значения кликов всхе пользователей
    "audio_click": audio_clicks,
    "text_click": text_clicks,
    "buy_click": buy_clicks
}  # dictionary

# Функция для отслеживания времени последнего нажатия кнопки "Выполнил" для каждого пользователя
last_done_action_time = {}

def check_time(message):
    collection.update_one({"_id": message.chat.id}, {"$set": {"time": message.text}})





@bot_api.message_handler(commands=['start'])
def start(message):
    global id
    id = message.chat.id

    if collection.find_one({"_id": id}):
        name = collection.find_one({"_id": id})["name"]
        bot_api.send_message(message.chat.id, f"Привет {name}!!!!")
    else:
        #date = datetime.date.today().isoformat()
        user = message.from_user.username
        collection.insert_one({ # запись в базу данных пользовательскую инфу
            "_id": id,
            "name": user,
            "time": 0,
            "date": 0,
            "numtask": 0,
            "task_review": {
                "task0": {
                    "review": "",
                    "grade": 0
                },
                "task1": {
                    "review": "",
                    "grade": 0
                },
                "task2": {
                    "review": "",
                    "grade": 0
                },
                "task3": {
                    "review": "",
                    "grade": 0
                },
                "task4": {
                    "review": "",
                    "grade": 0
                },
                "task5": {
                    "review": "",
                    "grade": 0
                },
                "task6": {
                    "review": "",
                    "grade": 0
                }
            }

        })
    text = ("Тут красуется сообщение о курсе.\n"
            "\n"
            "\n"
            "Жми /menu")
    bot_api.send_message(message.chat.id, text, parse_mode='html')
def check_daily_task(message):
    numtask = collection.find_one({"_id": message.chat.id})["numtask"]
    if numtask == 7:
        markup = types.InlineKeyboardMarkup()

        markup.add(types.InlineKeyboardButton('Купить', callback_data='buy'))
        bot_api.send_message(message.chat.id, "Вы завершили курс, спасибо! Еслхи хотите, купите курс",
                             reply_markup=markup)
    elif numtask == 1 or numtask == 4:

        markup = types.InlineKeyboardMarkup(row_width=2)
        btn = types.InlineKeyboardButton(text="Оставить отзыв", url="https://youtu.be/pwIZ4LChrt0?t=19")
        btnCancel = types.InlineKeyboardButton(text="Оставить отзыв без ответа", callback_data="cancel")
        markup.add(btn, btnCancel)
        bot_api.send_message(message.chat.id, "Прошлое задание было выполненно, если хотите, оставьте отзыв)", reply_markup=markup)
        day_task(message)

    else:
        last_time_date = collection.find_one({"_id": message.chat.id})["date"]

        current_date = datetime.date.today().isoformat()
        if collection.find_one({"_id": message.chat.id})["numtask"] == 0:
            day_task(message) ###

        else:
            if (current_date != last_time_date) :
                bot_api.send_message(message.chat.id, "Твое время не пришло, приходи завтра")
            else:

                day_task(message)


@bot_api.message_handler(commands=['show'])
def showall(message):
    print("Команда /showall обработана")
    all_users = collection.find()
    for i in all_users:
        bot_api.send_message(message.chat.id, f"{i}")

@bot_api.message_handler(commands=['stat'])
def stati(message):
    with open("Output.json", "r") as file:
        stat = json.load(file)
    for i, v in stat.items():
        bot_api.send_message(message.chat.id, f"{i}, {v}")

@bot_api.message_handler(commands=['menu'])
def menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1) # подраивание под нужной размер
    task_every_day = types.KeyboardButton("Ежедневное задание")
    info = types.KeyboardButton("О курсе")

    photo_menu = open(r"img\menu_bottum.png", 'rb')
    markup.add(task_every_day, info)  # добавляем наши кнопки
    bot_api.send_message(message.chat.id, 'Нажимай на эту кнопку', reply_markup=markup)
    bot_api.send_photo(message.chat.id, photo_menu)

@bot_api.message_handler(content_types=['text'])  # обрабатываем кнопки основного меню, высылаемые текстом
def func(message):
    if (message.text == "О курсе"):
        start(message)
    elif (message.text == "Ежедневное задание"):
        check_daily_task(message)




@bot_api.callback_query_handler(func = lambda callback: True) # для кнопок, которые выводятся после нажатия "Ежедневное задание"
def callback_message(callback):


    markup = types.InlineKeyboardMarkup(row_width=2)  # выводим кнопки в строчку по две штуки
    markup.add(types.InlineKeyboardButton('✅Выполнил', callback_data='done'),
               types.InlineKeyboardButton('❌Не выполнил', callback_data='not_done'))

    done_task = collection.find_one({"_id": callback.message.chat.id})["numtask"]
    with open(f"files/task{done_task + 1}.txt", "r", encoding='utf-8') as file:
        data1 = file.read()


    if callback.data == "audio":
        global audio_clicks
        audio_clicks += 1

        data["audio_click"] = audio_clicks  # меняет зачение в словаре
        with open("Output.json", "w") as file: # записывает клики
            json.dump(data, file)

        audio = open(fr'audio/task{done_task}.mp3', 'rb')
        bot_api.send_audio(callback.message.chat.id, audio, reply_markup=markup)
        audio.close()

    elif callback.data == "textt":
        global text_clicks
        text_clicks += 1
        data["text_click"] = text_clicks  # меняем значение в словаре
        with open("Output.json", "w") as file:  # записываем в json файл
            json.dump(data, file)

        bot_api.send_message(callback.message.chat.id, f"{data1}", reply_markup=markup)

    elif callback.data == "done":
        # Удаляем inline кнопку после нажатия
        bot_api.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id, reply_markup=None)

        #current_time = datetime.datetime.now()
        #a = (current_time - current_time.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
        #collection.update_one({"_id": callback.message.chat.id}, {"$set": {"coolldown": a}})
        collection.update_one({"_id": callback.message.chat.id}, {"$set": {"date": datetime.date.today().isoformat()}}) # задается дата в день выполнения задания

        ##########################
        markup = types.InlineKeyboardMarkup()

        markup.add(types.InlineKeyboardButton('1', callback_data='Плохо'))
        markup.add(types.InlineKeyboardButton("2", callback_data='Ниже среднего'))
        markup.add(types.InlineKeyboardButton('3', callback_data='Средне'))
        markup.add(types.InlineKeyboardButton("4", callback_data='Хорошо'))
        markup.add(types.InlineKeyboardButton('5', callback_data='Отлично'))



        bot_api.send_message(callback.message.chat.id, "Как вам задание? Оцените его по 5 - ти бальной шкале", reply_markup=markup)


    elif callback.data in ['Плохо', 'Ниже среднего', 'Средне', 'Хорошо', 'Отлично']:
        # Получаем номер задания, для которого пользователь оставил отзыв
        numtask = collection.find_one({"_id": callback.message.chat.id})["numtask"]

        if callback.message.text:
            # Обновляем базу данных с оценкой и отзывом
            collection.update_one({"_id": callback.message.chat.id},
                                  {"$set": {f"task_review.task{numtask}.grade": callback.data}})
        bot_api.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                          reply_markup=None)

        markup2 = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)  # подраивание под нужной размер
        task_every_day = types.KeyboardButton("Оставить Отзыв о задании")
        bot_api.send_message(callback.message.chat.id, 'Оставьте отзыв о задании', reply_markup=markup2)


        numtask = collection.find_one({"_id": callback.message.chat.id})["numtask"] #обновляем счетчик заданий
        numtask += 1
        collection.update_one({"_id": callback.message.chat.id}, {"$set": {"numtask": numtask}})
        if (numtask == 7):
            markup = types.InlineKeyboardMarkup()

            markup.add(types.InlineKeyboardButton('Купить', callback_data='buy'))
            bot_api.send_message(callback.message.chat.id, "Ты молодец, трали вали, курс купишь да?", reply_markup=markup)
        else:
            # Отправляем сообщение с благодарностью
            bot_api.send_message(callback.message.chat.id,
                                 "Спасибо за отзыв!")
           

    elif callback.data == "buy":
        bot_api.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                          reply_markup=None)
        global buy_clicks
        buy_clicks += 1

        data["buy_click"] = buy_clicks  # меняет зачение в словаре
        with open("Output.json", "w") as file:
            json.dump(data, file)
        bot_api.send_message(callback.message.chat.id, "Спасибо, с ваше карты списало 1.000.000.000 тенге, всего хорошего")

    elif callback.data == "cancel":
        bot_api.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                         reply_markup=None)
        bot_api.send_message(callback.message.chat.id, "Ладно, еще увидимся")


@bot_api.message_handler(commands=['daytask'])
def day_task(message):
    markup = types.InlineKeyboardMarkup()

    markup.add(types.InlineKeyboardButton('🔊 Аудио', callback_data='audio'))
    markup.add(types.InlineKeyboardButton("📖 Текст", callback_data='textt'))

    bot_api.send_message(message.chat.id, 'В каком формате вам будет удобнее просмотреть задание?\n'
                                          'В аудио или тестковом формате?', reply_markup=markup)



bot_api.polling(none_stop=True) # бот работает в нон стоп режиме