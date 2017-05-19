#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telebot
import parser
import requests
bot = telebot.TeleBot("349791719:AAGz3KaZsc3OPuj1D4rtxIVWtVZr9azAqG0")
url = 'https://api.telegram.org/bot349791719:AAGz3KaZsc3OPuj1D4rtxIVWtVZr9azAqG0/sendPhoto'
#print(bot.get_me())

def log(message, answer):
    print("\n-------")
    from datetime import datetime
    print(datetime.now())
    print("Сообщение от {0} {1}. (id = {2}) \nТекст: '{3}' \nОтвет: '{4}'".format(message.from_user.first_name,
                                                                                  message.from_user.last_name,
                                                                                  str(message.from_user.id),
                                                                                  message.text,
                                                                                  answer))



@bot.message_handler(content_types=['text'])
def handle_text(message):
        if message.text:
            result = parser.finalSearch(message.text)
            if (type(result) == list):
                for item in result:
                    bot.send_message(message.chat.id, item['name'] + ' - ' + item['href'])
            elif (type(result) == dict):
                for key in result:
                    if (type(result[key]) == list):
                        rateList = '';
                        for item in result[key]:
                            if(item['skill'] == u'Знания'):
                                rateList= rateList + item['skill'] + '                                ' + emojiPrettify(item['value']) + '\n'
                            elif (item['skill'] == u'В общении'):
                                rateList= rateList + item['skill'] + '                         ' + emojiPrettify(item['value']) + '\n'
                            elif (item['skill'] == u'Халявность'):
                               rateList= rateList + item['skill'] + '                        ' + emojiPrettify(item['value']) + '\n'
                            elif (item['skill'] == u'Общая оценка'):
                                rateList= rateList + item['skill'] + '                  ' + emojiPrettify(item['value']) + '\n'
                            else:
                                rateList= rateList + item['skill'] + '      ' + emojiPrettify(item['value']) + '\n'
                        bot.send_message(message.chat.id, rateList)
                    elif (key == 'image'):
                            #bot.send_message(message.chat.id, key + ' - http://wikimipt.org/' + result[key])
                            requests.get(url + '?chat_id=' + str(message.chat.id) + '&photo=http://wikimipt.org/' + result[key] )
                    else:
                        if (key == 'name'):
                            bot.send_message(message.chat.id, result[key])
            else:
                bot.send_message(message.chat.id, 'Ничего не найдено')


def emojiPrettify(line):
    for i in range(0, 8):
        if(line[i] == '('):
            num = line[:i].strip()
    print(float(num))
    return emojify(float(num)) + '   ' + line
def emojify(num):
    if(num >= 4.5):
        return u'❤️❤️❤️❤️❤️'
    if num // 1 == 4 :
        return u'⭐️⭐️⭐️⭐️'
    elif num//1 == 3 : 
        return u'⭐️⭐️⭐️'
    elif num//1 == 2 :
        return u'🍆🍆'
    return u'🆘'
#log(message,answer)

# @bot.message_handler(content_types=['text'])
# def handle_text(message):
#    if message.text == "mipt":
#        answer = "idi botamy"
#        bot.send_message(message.chat.id, "idi botay")
#        log(message,answer)

# @bot.message_handler(commands=['start'])
# def keyboard(message):
#     user_markup = telebot.types.ReplyKeyboardMarkup(True)
#     user_markup.row('/start')
#     bot.send_message(message.from_user.id, 'здрасте', reply_markup=user_markup)

bot.polling(none_stop=True, interval=0)

