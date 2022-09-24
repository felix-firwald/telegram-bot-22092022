from telebot import types
from peewee import SqliteDatabase

from settings import bot, DEFAULT_ANSWER
from models import (
    TemplateExercise,
    TemplateTraining,
    User,
)

db = SqliteDatabase('data.db')
# bot = telebot.TeleBot(settings.TOKEN)

MENU_COMMANDS = [
    'Новая тренировка',
    'Посмотреть свои тренировки',
    'Создать шаблон тренировки'
]


if_voice_send = 'Я не умею распознавать голосовые сообщения.'


@bot.message_handler(commands=["menu"])
def answer_to_menu(message):
    with db:
        try:
            User.get(User.user_id == message.from_user.id)
        except Exception:
            user = User.create(
                user_id=message.from_user.id
            )
            user.save()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    for command in MENU_COMMANDS:
        markup.add(types.KeyboardButton(command))
    bot.send_message(
        message.chat.id,
        'Взгляни на <b>кнопки</b> меню.',
        parse_mode='html',
        reply_markup=markup
    )


@bot.message_handler(commands=["clear"])
def clear_database(message):
    bot.send_message(
        message.chat.id,
        'База данных очищена.',
    )


@bot.message_handler(content_types=["text"])
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
        bot.register_next_step_handler(message, get_name, template_generating)
    else:
        bot.send_message(message.chat.id, DEFAULT_ANSWER)
        answer_to_menu(message)


# генерация шаблона тренировки
def template_generating(message):
    with db:
        training = TemplateTraining.create(
            name=message.text,
            author=message.from_user.id
        )
        training.save()
    gen_ex = bot.message_handler(
        message.chat.id,
        'Теперь укажи названия упражнений — по одному на каждое сообщение.'
    )
    # bot.register_next_step_handler(
    #    message,
    #    gen_ex, exercise_generating(message, training)
    #)


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
        message,
        question, exercise_generating(message, training), reply_markup=markup
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


bot.polling(none_stop=True)
