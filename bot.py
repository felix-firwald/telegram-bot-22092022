from telebot import types
from peewee import SqliteDatabase

from settings import bot, DEFAULT_ANSWER
from messages import template_generating
from models import (
    User,
    TemplateExercise,
    Exercise,
    TemplateTraining,
    Training
)

DATA = SqliteDatabase('data.db')
with DATA:
    DATA.create_tables([
        User,
        TemplateExercise,
        Exercise,
        TemplateTraining,
        Training
    ])

# bot = telebot.TeleBot(settings.TOKEN)

MENU_COMMANDS = (
    'Новая тренировка',
    'Посмотреть свои тренировки',
    'Создать шаблон тренировки'
)


if_voice_send = 'Я не умею распознавать голосовые сообщения.'


@bot.message_handler(commands=['menu'])
def answer_to_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    for command in MENU_COMMANDS:
        markup.add(types.KeyboardButton(command))
    bot.send_message(
        message.chat.id,
        'Взгляни на <b>кнопки</b> меню.',
        parse_mode='html',
        reply_markup=markup
    )


@bot.message_handler(commands=['clear', 'erase'])
def clear_database(message):
    bot.send_message(
        message.chat.id,
        'База данных очищена.',
    )

@bot.message_handler(content_types=['text'])
def other_text(message):
    text = message.text
    if text == MENU_COMMANDS[0]:  # Новая тренировка
        pass
    elif text == MENU_COMMANDS[1]:  # Посмотреть свои тренировки
        pass
    elif text == MENU_COMMANDS[2]:  # Создать шаблон тренировки
        get_name = bot.message_handler(
            message.chat.id,
            'Введите название шаблона:'
        )
        bot.register_next_step_handler(get_name, template_generating(message))
    else:
        bot.send_message(message.chat.id, DEFAULT_ANSWER)
        answer_to_menu(message)


bot.polling(none_stop=True)
