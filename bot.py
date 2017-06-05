#!/usr/bin/env python
# -*- coding: utf-8 -*-
import parser
import telebot
import requests
from datetime import datetime, date
from flask import Flask, request
import statistic
import os
import psycopg2
from urllib.parse import urlparse
from flask_sqlalchemy import SQLAlchemy

bot = telebot.TeleBot("349791719:AAGz3KaZsc3OPuj1D4rtxIVWtVZr9azAqG0")
url = 'https://api.telegram.org/bot349791719:AAGz3KaZsc3OPuj1D4rtxIVWtVZr9azAqG0/'
server = Flask(__name__)
server.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(server)
print(db)
#будем писать логи или нет
is_logging = True
print('JUST STARTED')
#логгер
def log(message, answer):
    print(datetime.now())
    print("Сообщение от {0} {1}. (id = {2}) \nЗапрос: '{3}' \nОтвет: '{4}'".format(message.from_user.first_name,
                                                                                  message.from_user.last_name,
                                                                                  str(message.from_user.id),
                                                                                  message.text,
                                                                                     answer))
    print("\n-------")

class Prepod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    def __init__(self, name):
        self.name = name

class Stats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    prepod_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)

    def __init__(self, prepod_id, user_id):
        self.date = datetime.now()
        self.prepod_id = prepod_id;
        self.user_id = user_id;

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет, ' + message.from_user.first_name)
#функция обработки входящих сообщений
@bot.message_handler(func=lambda message: True, content_types=['text'])
def telemipt(message):
        if message.text:
            result = parser.finalSearch(message.text)
            summary_rate = 0
            if (type(result) == list):
                if (len(result)>=5):
                    answer = 'Формулируй запрос чётче. Результатов слишком много: ' + str(len(result));
                    bot.send_message(message.chat.id, answer)
                    if (is_logging):
                        log(message, answer)
                else:
                    for item in result:
                        #чтобы ссылка красиво выглядела
                        message_url = url + 'sendMessage' + '?chat_id=' + str(message.chat.id) + \
                                      '&text=<a href="' + item['href'] + '">' + item['name'] + '</a>&parse_mode=HTML'
                        requests.get(message_url)
                        answer = item['name']
                        if (is_logging):
                            log(message, answer)
            elif (type(result) == dict):
                for key in result:
                    if (type(result[key]) == list):
                        rateList = ''
                        for item in result[key]:
                            summary_rate += num(item['value'])
                            rateList += categories_prettify(item)
                        bot.send_message(message.chat.id, rateList)
                    elif (key == 'image'):
                            bot.send_photo(message.chat.id, 'http://wikimipt.org/' + result[key] )
                    else:
                        if (key == 'name'):
                            answer = result[key]
                            bot.send_message( message.chat.id, result[key] )
                if (is_logging):
                    log(message, answer)
                if (summary_rate != 0):
                    bot.send_message( message.chat.id, make_bot_prediction( summary_rate / 5 ))
                else:
                     bot.send_message( message.chat.id, 'Here be dragons later')
                prep = session.query(Prepod).filter_by(name=result['name']).first()
                if ( not prepod ):
                    prep = Prepod(result['name'])
                    db.session.add(prep)
                    print(prep.id)
                db.session.add(Stats(prep.id, message.chat.id));
                db.session.commit()
            else:
                bot.send_message(message.chat.id, 'Ничего не найдено')
                answer = 'Ничего не найдено'
                if (is_logging):
                    log(message, answer)





#берет значение рейтинга(число) по данному полю
def num(line):
    words = line.split(' ')
    num = words[0]
    if (not num.isalpha() and num != '('):
        return float(num)
    else:
        return 0.0
#делаем предсказание исходя из суммарного рейтинга
def make_bot_prediction(rate):
    if (rate >= 4.5) :
        return 'Бот считает, что этот препод бог'
    elif (rate >= 4 and rate < 4.5):
        return 'Бот считает, что этот препод классный'
    elif (rate >= 3 and rate < 4):
            return 'Бот считает, что этот препод среднячок'
    elif (rate >= 2 and rate < 3):
        return 'Бот считает, что этот препод так себе'
    else:
        return 'Бот считает, что это опасность'

#инсайт : телеграм сжимает пробелы и нижние подчеркивания и черт знает что еще - записи,
#         в которых одинаковое число символов могут иметь разную длину, поэтому число пробелов нельзя
#         рассчитать исходя из длины строки
def categories_prettify(item):
    if(item['skill'] == u'Знания'):
        return item['skill'] + '                                ' + \
        emoji_prettify(item['value']) + '\n'
    elif (item['skill'] == u'В общении'):
        return item['skill'] + '                         ' + \
        emoji_prettify(item['value']) + '\n'
    elif (item['skill'] == u'Халявность'):
        return item['skill'] +  '                        ' + \
        emoji_prettify(item['value']) + '\n'
    elif (item['skill'] == u'Общая оценка'):
        return item['skill'] + '                  ' + \
        emoji_prettify(item['value']) + '\n'
    else:
        return item['skill'] + '      ' + \
        emoji_prettify(item['value']) + '\n'

#печатает звездочки для рейтинга
def emoji_prettify(line):
    return round(num(line)) * u'★' + (5 - round(num(line))) * u'☆' + '   ' + line

@server.route("/bot", methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url="https://mipttelegram.herokuapp.com/bot")
    return "!", 200
@server.route("/stop")
def webhook_stop():
    bot.remove_webhook()


server.run(host="0.0.0.0", port=os.environ.get('PORT', 5000))
server = Flask(__name__)
