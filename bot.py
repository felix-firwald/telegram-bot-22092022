from telebot import types
from peewee import IntegrityError
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
    create_a_new_training,
    messages_for_delete
)

db = SqliteDatabase('data.db')


@bot.message_handler(commands=["menu"])
def answer_to_menu(message):
    get_user_or_create(message)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    for command in MENU_COMMANDS:
        markup.add(types.KeyboardButton(command))
    buttons_message = bot.send_message(
        message.chat.id,
        'Взгляни на <b>кнопки меню</b>',
        parse_mode='html',
        reply_markup=markup
    )
    bot.register_next_step_handler(
        buttons_message,
        main_logic
    )


@bot.callback_query_handler(
    func=lambda call: call.data.split('//')[0] == 'TEMPL'
)
def training_choosen(call):
    chat_id = call.message.chat.id
    request = call.data.split('//')
    data = get_exercises_of_template(request[1])
    template_name = data[0]
    exercises = data[1]
    string = str()
    for i in range(len(exercises)):
        string += f'\n{i + 1}. {exercises[i]}'
    message = bot.send_message(
        chat_id,
        f'Тренировка: {template_name}.\n{string}',
        reply_markup=None
    )
    create_a_new_training(message, data, message.id)


# @bot.message_handler(content_types=["text"])
def main_logic(message):
    bot.send_message(
        message.chat.id,
        'Секунду...',
        reply_markup=types.ReplyKeyboardRemove()
    )
    text = message.text
    chat_id = message.chat.id
    user_id = message.from_user.id
    if text == MENU_COMMANDS[0]:
        markup = types.InlineKeyboardMarkup()
        for template in get_templates_of_user(user_id):
            markup.add(types.InlineKeyboardButton(
                text=template.name,
                callback_data=f'TEMPL//{template.id}'
            ))
        choice_template = bot.send_message(
            chat_id,
            'Выбери шаблон тренировки:',
            reply_markup=markup
        )
        messages_for_delete.append(choice_template.id)
        # bot.register_next_step_handler(choice_template, new_training)
    elif text == MENU_COMMANDS[1]:
        pass
    elif text == MENU_COMMANDS[2]:
        get_name = bot.send_message(
            chat_id,
            'Введи название шаблона:'
        )
        bot.register_next_step_handler(get_name, template_generating)
    else:
        bot.send_message(chat_id, DEFAULT_ANSWER)
        answer_to_menu(message)


def new_training(message):
    bot.send_message(message.chat.id, 'You send me message')


@bot.message_handler(commands=["clear", "clean"])
def clear_database(message):
    clear()
    bot.send_message(
        message.chat.id,
        'База данных очищена',
    )


bot.polling(none_stop=True)
