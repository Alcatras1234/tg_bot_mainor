from datetime import datetime

from main import bot_api
from telebot import types
import datetime


def check_daily_task(message):
    from main import collection
    numtask = collection.find_one({"_id": message.chat.id})["numtask"]
    if numtask == 7:
        markup = types.InlineKeyboardMarkup()

        markup.add(types.InlineKeyboardButton('Купить', callback_data='buy'))

        bot_api.send_message(message.chat.id, "Вы завершили курс, спасибо! Еслхи хотите, купите курс",
                             reply_markup=markup)
    elif numtask == 1:
        bot_api.send_message(message.chat.id, "Первое задание было выполненно, введите время, в которое вы бы хотели получать новое задание в формате HH:MM")
        bot_api.register_next_step_handler(message, check_time)
    else:
        last_time_date = collection.find_one({"_id": message.chat.id})["date"]

        current_time2 = datetime.date.today().isoformat()
        if collection.find_one({"_id": message.chat.id})["numtask"] == 0:

            day_task(message) ###
        else:
            if current_time2 != last_time_date:
                collection.update_one({"_id": message.chat.id}, {"$set": {"coolldown": 0}})

                day_task(message) ###
            else:  # тестим сегодня

                if True:
                    bot_api.send_message(message.chat.id, "Gbgbgbg")
                else:
                    bot_api.send_message(message.chat.id, "Приходите завтра")
