from telebot import types
from peewee import SqliteDatabase

from database import (
    clear,
    get_user_or_create,
    get_templates_of_user,
    get_exercises_of_template
)
from settings import (
    bot,
    DEFAULT_ANSWER,
    MENU_COMMANDS
)
from messages import (
    template_generating,
    create_a_new_training
)

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


@bot.callback_query_handler(func=lambda call: True)
def reaction(call):
    chat_id = call.message.chat.id
    request = call.data.split('//')
    if request[0] == 'TEMPL':
        data = get_exercises_of_template(request[1])
        template_name = data[0]
        exercises = data[1]
        string = str()
        for i in range(len(exercises)):
            string += f'\n{i + 1}. {exercises[i].capitalize()}'
        message = bot.send_message(
            chat_id,
            f'Тренировка: {template_name}.\n{string}',
            reply_markup=None
        )
        create_a_new_training(message, data)
        # bot.register_next_step_handler(message, create_a_new_training, data)
    else:
        pass

@bot.message_handler(content_types=["text"])
def other_text(message):
    text = message.text
    chat_id = message.chat.id
    user_id = message.from_user.id
    # Новая тренировка
    if text == MENU_COMMANDS[0]:
        markup = types.InlineKeyboardMarkup()
        for template in get_templates_of_user(user_id):
            markup.add(types.InlineKeyboardButton(
                text=template.name,
                callback_data=f'TEMPL//{template.id}'
            ))
        choice_template = bot.send_message(
            chat_id,
            'Выберите шаблон тренировки:',
            reply_markup=markup
        )
        bot.register_next_step_handler(choice_template, new_training)
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
