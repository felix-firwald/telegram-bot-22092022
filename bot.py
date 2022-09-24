import telebot
from telebot import types

import settings

bot = telebot.TeleBot(settings.TOKEN)
default_answer = 'Прости, но я тебя не понимаю.'
if_voice_send = 'Я не умею распознавать голосовые сообщения.'


@bot.message_handler(commands=['menu'])
def answer_to_menu(message):
    commands = {
        'Новая тренировка': '/newtraining',
        'Посмотреть свои тренировки': '/gettrainings',
        'Создать шаблон тренировки': '/createtemplate',
        'Очистить статистику': '/clear'
    }
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    for name, command in commands.items():
        markup.add(types.KeyboardButton(name))
    bot.send_message(
        message.chat.id,
        'Взгляни на <b>кнопки</b> меню.',
        parse_mode='html',
        reply_markup=markup
    )

# дефолтный ответ (то есть на тот случай, когда вопрос боту неизвестен)
@bot.message_handler(content_types=['text'])
def other_text(message):
    bot.send_message(message.chat.id, default_answer)
    answer_to_menu(message)



@bot.message_handler(content_types=['voice'])
def answer_to_voice(message):
    id = message.chat.id
    bot.send_message(id, if_voice_send)
    bot.send_chat_action(id, action='record_audio')


bot.polling(none_stop=True)
