from datetime import datetime

from telebot import types
from peewee import SqliteDatabase

from models import (
    TemplateTraining,
    TemplateExercise,
    Training
)
from settings import bot

db = SqliteDatabase('data.db')

messages_for_delete = []


def template_generating(message):
    with db:
        training = TemplateTraining.create(
            name=message.text.capitalize(),
            author=message.from_user.id
        )
        training.save()
    gen_ex = bot.send_message(
        message.chat.id,
        'Теперь укажи названия упражнений — по одному на каждое сообщение.'
    )
    bot.register_next_step_handler(
        gen_ex, exercise_generating, training
    )


def exercise_generating(message, training):
    if messages_for_delete:
        print(messages_for_delete)
        bot.delete_message(message.chat.id, messages_for_delete.pop(0))

    if message.text.lower() == 'да, это всё':  # если это всё
        bot.send_message(
            message.chat.id,
            'Шаблон создан!',
            reply_markup=types.ReplyKeyboardRemove()
        )
        bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    else:
        with db:
            exercise = TemplateExercise.create(
                template=training,
                name=message.text.capitalize()
            )
            exercise.save()
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
    with db:
        training = Training.create(
            start=datetime.now(),
            template=data[0],
            user=message.from_user.id
        )
        training.save()
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
    with db:
        training.end = datetime.now()
        training.save()
    
