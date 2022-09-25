from telebot import types
from peewee import SqliteDatabase

from database import (
    clear,
    get_user_or_create
)
from settings import (
    bot,
    DEFAULT_ANSWER,
    MENU_COMMANDS
)
from messages import template_generating

db = SqliteDatabase('data.db')


@bot.message_handler(commands=["menu"])
def answer_to_menu(message):
    get_user_or_create(message)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    for command in MENU_COMMANDS:
        markup.add(types.KeyboardButton(command))
    bot.send_message(
        message.chat.id,
        'Взгляни на <b>кнопки меню</b>',
        parse_mode='html',
        reply_markup=markup
    )


@bot.message_handler(commands=["clear", "clean"])
def clear_database(message):
    clear()
    bot.send_message(
        message.chat.id,
        'База данных очищена',
    )


@bot.message_handler(content_types=["text"])
def other_text(message):
    text = message.text
    chat_id = message.chat.id
    # Новая тренировка
    if text == MENU_COMMANDS[0]:
        mesg = bot.send_message(chat_id, 'Выберите шаблон тренировки:')
        bot.register_next_step_handler(mesg, new_training)
    # Посмотреть свои тренировки
    elif text == MENU_COMMANDS[1]:
        pass
    # Создать шаблон тренировки
    elif text == MENU_COMMANDS[2]:
        get_name = bot.send_message(
            chat_id,
            'Введите название шаблона:',
            reply_markup=types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(get_name, template_generating)
    else:
        bot.send_message(chat_id, DEFAULT_ANSWER)
        answer_to_menu(message)


def new_training(message):
    bot.send_message(message.chat.id, 'You send me message')


bot.polling(none_stop=True)
