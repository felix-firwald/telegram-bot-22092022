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
    MENU_COMMANDS,
    USE_MENU
)
from messages import (
    template_generating,
    create_a_new_training,
    messages_for_delete
)
from user_configs import user_configs_menu


db = SqliteDatabase('data.db')
# db.create_tables([
#    Exercise,
#    Training,
#    TemplateExercise,
#    TemplateTraining,
#    User
# ])


@bot.message_handler(content_types=["pinned_message"])
def delete_alarms(message):
    bot.delete_message(message.chat.id, message.id)
    bot.send_message(
        message.chat.id,
        'pinned message deleted',
        reply_markup=types.ReplyKeyboardRemove()
    )


@bot.message_handler(commands=["start"])
def answer_to_start(message):
    get_user_or_create(message)
    bot.send_message(
        message.chat.id,
        f'Привет, я бот для <b>учета тренировок</b>{USE_MENU}',
        parse_mode='html'
    )


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
    bot.answer_callback_query(call.id)
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


def main_logic(message):
    sec = bot.send_message(
        message.chat.id,
        '...',
        reply_markup=types.ReplyKeyboardRemove()
    )
    bot.delete_message(
        sec.chat.id,
        sec.id
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
    elif text == MENU_COMMANDS[1]:
        pass
    elif text == MENU_COMMANDS[2]:
        get_name = bot.send_message(
            chat_id,
            'Введи название шаблона:'
        )
        bot.register_next_step_handler(get_name, template_generating)
    elif text == MENU_COMMANDS[3]:
        bot.send_message(
            chat_id,
            'Введи название шаблона:'
        )
        user_configs_menu(message)
    else:
        bot.send_message(chat_id, DEFAULT_ANSWER)
        answer_to_menu(message)


@bot.message_handler(commands=["clear", "clean"])
def clear_database(message):
    clear()
    bot.send_message(
        message.chat.id,
        'База данных очищена',
    )


bot.polling(none_stop=True)
