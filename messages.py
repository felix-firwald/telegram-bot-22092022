from datetime import datetime

from telebot import types
from peewee import SqliteDatabase, IntegrityError

from database import (
    save_template_training,
    save_template_exercise,
    save_training,
    save_end_of_training
)
from settings import bot

db = SqliteDatabase('data.db')

messages_for_delete = []
g_ex = 'Теперь укажи названия упражнений — по одному на каждое сообщение.'


def template_generating(message):
    try:
        training = save_template_training(message)  # запрос в базу
    except IntegrityError:
        error = bot.send_message(
            message.chat.id,
            'Ошибка!'
        )
        bot.register_next_step_handler(error, template_generating)
    else:
        gen_ex = bot.send_message(
            message.chat.id,
            g_ex
        )
        bot.register_next_step_handler(
            gen_ex, exercise_generating, training
        )


def exercise_generating(message, training):
    if messages_for_delete:
        print(messages_for_delete)
        bot.delete_message(message.chat.id, messages_for_delete.pop(0))

    if message.text.lower() == 'да, это всё':
        bot.send_message(
            message.chat.id,
            'Шаблон создан!',
            reply_markup=types.ReplyKeyboardRemove()
        )
        bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    else:
        save_template_exercise(message, training)  # запрос в базу
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(types.KeyboardButton("Да, это всё"))
        question = bot.send_message(
            message.chat.id,
            '''
            Укажи название следующего упражнения или нажми на кнопку''',
            reply_markup=markup,
        )
        messages_for_delete.append(question.id)
        bot.register_next_step_handler(
            question,
            exercise_generating,
            training
        )


def create_a_new_training(message, data, message_id):
    training = save_training(message, data)
    while messages_for_delete:
        bot.delete_message(
            message.chat.id,
            messages_for_delete.pop(0)
        )
    bot.pin_chat_message(chat_id=message.chat.id, message_id=message_id)
    buttons = (
        'Записать упражнение',
        'Закончить тренировку'
    )
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    for button in buttons:
        markup.add(types.KeyboardButton(button))
    what_to_do = bot.send_message(
        message.chat.id,
        'Что будем делать?',
        reply_markup=markup
    )
    bot.register_next_step_handler(what_to_do, switch, training, data)


def switch(message, training, data):
    if message.text == 'Записать упражнение':
        give_number = bot.send_message(
            message.chat.id,
            'Укажи номер упражнения для записи',
        )
        bot.register_next_step_handler(
            give_number,
            get_number_of_ex,
            training,
            data
        )
    elif message.text == 'Закончить тренировку':
        bot.send_message(
            message.chat.id,
            'Тренировка окончена!',
        )
        training_complete(message, training)


def get_number_of_ex(message, training, data):
    try:
        number = int(message.text) - 1
        exercise = data[1][number]
        print(exercise)
    except Exception:
        unsuccess = bot.send_message(
            message.chat.id,
            'Ошибка!',
        )
        bot.register_next_step_handler(
            unsuccess, get_number_of_ex, training, data
        )


def training_complete(message, training):
    save_end_of_training(training)
