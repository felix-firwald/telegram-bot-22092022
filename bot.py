import telebot
# from telebot import types
from random import choice

import settings

bot = telebot.TeleBot(settings.TOKEN)
text = ' — это твой текст.'
if_voice_send = 'Я не умею распознавать голосовые сообщения.'


@bot.message_handler(content_types=['text'])
def bot_message(message):
    bot.send_message(message.chat.id, message.text)


@bot.message_handler(content_types=['voice'])
def bot_message(message):
    id = message.chat.id
    bot.send_message(id, if_voice_send)
    bot.send_chat_action(id, action='record_audio')


bot.polling(none_stop=True)
