import json
import telebot
import sys
import random as rd
from telebot import types

bot = telebot.TeleBot('TOKEN')

count_of_address = 3


def jsoon(act, users_info=''):
    if act == 'r':
        with open('users.json', 'r') as users_file:
            users_info = json.load(users_file)
        return users_info
    elif act == 'w':
        if users_info != '':
            with open('users.json', 'w') as users_file:
                json.dump(users_info, users_file)
        else:
            bot.send_message('143369414', 'Try to write empty file')


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'hmp. ' + str(message.from_user.first_name) + '.\n\nwelcome.')
    users_info = jsoon('r')
    if str(message.from_user.id) not in list(users_info.keys()):
        users_info[str(message.from_user.id)] = {}
        jsoon('w', users_info)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if str(message.text).lower() == "привет":
        bot.send_message(message.from_user.id, str('Привет ' + message.from_user.first_name))
    elif str(message.text).lower() in ['hi', 'hello']:
        bot.send_message(message.from_user.id, str('hi, ' + message.from_user.first_name))
    # TODO открывание индексов из json
    elif str(message.text).lower() == "обновление" and str(message.chat.id) == '143369414':
        with open('indexes.txt', 'r') as w:
            ind = w.read().split()
        with open('updates_text.txt', 'r') as u:
            upd = u.read()
        for i in ind:
            bot.send_message(i, upd)
    else:
        message_send(message)


@bot.message_handler(content_types=["photo", "voice", "video", "document", "audio", "video_note"])
def get_all_types_messages(message):
    message_send(message)


@bot.message_handler(content_types=["location", "contact", "animation"])
def get_location_message(message):
    bot.send_message(message.from_user.id, 'Я пока не умею работать с таким типом данных')


def message_send(message):
    # читаем всех пользователей
    users_info = jsoon('r')
    users_list = list(users_info.keys())
    # исключаем себя из их списка
    users_list.remove(str(message.from_user.id))
    # если количество пользователей позволяет
    if len(users_list) >= count_of_address:
        # фиксируем количество потенциальных получателей
        # добавляем кнопку на сообщение
        keyboard = types.InlineKeyboardMarkup()
        # добавляем в нее контенту
        key_replay = types.InlineKeyboardButton(text='Ответить',
                                                callback_data=str(str(message.chat.id)
                                                                  + '|'
                                                                  + str(message.message_id)))
        # фигачим ее к сообщению
        keyboard.add(key_replay)
        # фиксируем успешные отправки сообщений
        success = 0
        # пока отправок меньше чем получателей и количество оставшихся позволяет
        while success < count_of_address and len(users_list) >= (count_of_address - success):
            # выбираем рандомного
            dx = rd.choice(users_list)
            # удаляем из списка потенциальных получателей
            users_list.remove(dx)
            # пытаемся отослать сообщение
            try:
                if message.content_type == 'text':
                    bot.send_message(dx, str(message.text), reply_markup=keyboard)
                elif message.content_type == 'photo':
                    # bot.send_photo('-1001560882887', message.photo[0].file_id)
                    bot.send_photo(dx, message.photo[0].file_id, reply_markup=keyboard)
                elif message.content_type == 'voice':
                    bot.send_voice(dx, message.voice.file_id, reply_markup=keyboard)
                elif message.content_type == 'video':
                    bot.send_video(dx, message.video.file_id, reply_markup=keyboard)
                elif message.content_type == 'document':
                    bot.send_document(dx, message.document.file_id, reply_markup=keyboard)
                elif message.content_type == 'location':
                    bot.send_location(dx, message.location.latitude, message.location.longitude, reply_markup=keyboard)
                elif message.content_type == 'audio':
                    bot.send_audio(dx, message.audio.file_id, reply_markup=keyboard)
                elif message.content_type == 'video_note':
                    bot.send_message(message.from_user.id, str(message))
                    bot.send_video_note(dx, message.video_note.file_id, reply_markup=keyboard)
                success += 1
            # если не выходит
            # TODO
            except:
                # убираем пользователя из списка активных
                del users_info[dx]
                # фиксируем изменения в населении
                bot.send_message('143369414', str("Unexpected error with " + str(dx) + '--->' + str(sys.exc_info()[0])))
                jsoon('w', users_info)
        # оповещаем счастливого пользователя об отправке сообщения
        bot.send_message(message.from_user.id, str('Отправил ' + str(success) + ' людям'))
    # если количество пользователей не позволяет
    else:
        bot.send_message(message.from_user.id, str('Недостаточно пользователей'))


@bot.callback_query_handler(func=lambda call: True)
def reply(call):
    # если пользователь еще не нажимал на кнопку ответа
    if call.data != '1':
        x = str(call.data)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup='')
        keyboard = types.InlineKeyboardMarkup()
        key_replay = types.InlineKeyboardButton(text='Введи свой ответ:', callback_data='1')
        keyboard.add(key_replay)
        if call.message.content_type == 'text':
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=call.message.text, reply_markup=keyboard)
        elif call.message.content_type == 'video_note':
            bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                   media=call.message.video_note.file_id, reply_markup=keyboard)
        elif call.message.content_type in ['photo', 'voice', 'video', 'document', 'audio']: # , 'video_note']:
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                     caption=call.message.caption, reply_markup=keyboard)
        y = [call.message.message_id, call.message.chat.id, call.message]
        bot.register_next_step_handler(call.message, distribution_center, x, y)
    # если уже нажимал на кнопку ответа – игнорируем повторные нажатия
    else:
        pass


def distribution_center(message, x, y):
    if message.content_type == 'text':
        print('text')
        resend(message, x, y, bot.send_message, message.text)
    elif message.content_type == 'photo':
        print('photo')
        resend(message, x, y, bot.send_photo, message.photo[0].file_id)
    elif message.content_type == 'voice':
        print('voice')
        resend(message, x, y, bot.send_voice, message.voice.file_id)
    elif message.content_type == 'video':
        print('video')
        resend(message, x, y, bot.send_video, message.video.file_id)
    elif message.content_type == 'document':
        print('document')
        resend(message, x, y, bot.send_document, message.document.file_id)
    elif message.content_type == 'audio':
        print('audio')
        resend(message, x, y, bot.send_audio, message.audio.file_id)
    elif message.content_type == 'video_note':
        print('video_note')
        resend(message, x, y, bot.send_video_note, message.video_note.file_id)
    elif message.content_type == 'location':
        print('location')
        resend_location(message, x, y)
    else:
        print('check сработал')
        bot.send_message(message.from_user.id, 'Такой тип данных не поддерживается')
        edit_message(y)


def resend(message, x, y, sendler, content):
    if message.content_type not in ["photo", "voice", "video", "document", "audio", "text", "video_note"]:
        bot.send_message(message.from_user.id, 'Извини, но я пока не понимаю такой тип ответа')
        # bot.register_next_step_handler(msg, resend, x, y)
        edit_message(y)
    else:
        sendler(x.split('|')[0], content, reply_to_message_id=x.split('|')[1])
        edit_message(y)
        # Force-Reply на отвеченное сообщение
        sendler(message.from_user.id, content, reply_to_message_id=y[0])
        bot.delete_message(message.chat.id, message.message_id)


def resend_location(message, x, y):
    if message.content_type != 'location':
        bot.send_message(message.from_user.id, 'Извини, но я пока не понимаю такой тип ответа')
    else:
        bot.send_location(x.split('|')[0],
                          message.location.latitude,
                          message.location.longitude,
                          reply_to_message_id=x.split('|')[1])
        edit_message(y)
        # Force-Reply на отвеченное сообщение
        bot.send_location(message.from_user.id,
                          message.location.latitude,
                          message.location.longitude,
                          reply_to_message_id=y[0])
        bot.delete_message(message.chat.id, message.message_id)


def edit_message(y):
    if y[2].content_type == 'text':
        bot.edit_message_text(chat_id=y[1], message_id=y[0], text=y[2].text, reply_markup='')
    elif y[2].content_type == 'video_note':
        bot.edit_message_media(chat_id=y[1], message_id=y[0], media=y[2].media, reply_markup='')
    elif y[2].content_type in ["photo", "voice", "video", "document", "audio", "video_note"]:
        bot.edit_message_caption(chat_id=y[1], message_id=y[0], caption=y[2].caption, reply_markup='')
#     elif y[2].content_type == 'location':
#         bot.edit_message_caption(chat_id=y[1], message_id=y[0],
#                                  caption=y[2].caption, reply_markup='')


bot.polling(none_stop=True, interval=0)
