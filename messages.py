from telebot import types
from peewee import SqliteDatabase

from models import (
    TemplateTraining,
    TemplateExercise
)
from settings import bot

db = SqliteDatabase('data.db')


def template_generating(message):
    with db:
        training = TemplateTraining.create(
            name=message.text,
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
                name=message.text
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
        bot.register_next_step_handler(
            question,
            exercise_generating,
            training
        )
