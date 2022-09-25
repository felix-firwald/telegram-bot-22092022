from telebot import types
from peewee import SqliteDatabase

from database import (
    clear,
    get_user_or_create
)
from settings import bot, DEFAULT_ANSWER
from models import (
    TemplateExercise,
    TemplateTraining
)

db = SqliteDatabase('data.db')

MENU_COMMANDS = (
    'Новая тренировка',
    'Посмотреть свои тренировки',
    'Создать шаблон тренировки',
    'Настройки'
)


if_voice_send = 'Я не умею распознавать голосовые сообщения.'


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
            'Введите название шаблона:'
        )
        bot.register_next_step_handler(get_name, template_generating)
    else:
        bot.send_message(chat_id, DEFAULT_ANSWER)
        answer_to_menu(message)


# генерация шаблона тренировки
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
        gen_ex, exercise_generating
    )


def exercise_generating(message, training):
    with db:
        exercise = TemplateExercise.create(
            template=training,
            name=message.text
        )
        exercise.save()
    question = bot.message_handler(
        message.chat.id,
        'Это всё?'
    )
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(types.KeyboardButton("Да"), types.KeyboardButton("Нет"))
    bot.register_next_step_handler(
        question, exercise_generating, reply_markup=markup
    )


def exercise_yes_or_no(message, training):
    if message.text.lower() == 'да':  # если это всё
        bot.send_message(message.chat.id, 'Шаблон создан!')
    else:  # если ещё не всё
        gen_ex = bot.message_handler(
            message.chat.id,
            'Продолжай.'
        )
        bot.register_next_step_handler(
            gen_ex, exercise_generating(message, training)
        )


def new_training(message):
    bot.send_message(message.chat.id, 'You send me message')


bot.polling(none_stop=True)
