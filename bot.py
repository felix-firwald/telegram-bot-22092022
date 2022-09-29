from telebot import types
from peewee import SqliteDatabase

from database import (
    clear,
    get_user_or_create,
    get_templates_of_user,
    get_exercises_of_template,
    get_all_trainings_of_user,
    delete_template_of_training,
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
    show_made_training,
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
    '''
    Просто для красоты: пускай бот удаляет
    системные сообщения о том, что он закрепил сообщение.
    '''
    bot.delete_message(message.chat.id, message.id)


@bot.message_handler(commands=["start"])
def answer_to_start(message):
    '''
    Эта функция встречает юзера,
    который впервые зашел в бота.
    '''
    get_user_or_create(message)
    bot.send_message(
        message.chat.id,
        f'Привет, я бот для <b>учета тренировок</b>{USE_MENU}',
        parse_mode='html'
    )


@bot.message_handler(commands=["menu"])
def answer_to_menu(message):
    '''
    Функция выводит кнопки главного меню.
    '''
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
    '''
    Функция работает при нажатии юзером на inline-кнопку
    при выборе шаблона для тренировки.
    '''
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


@bot.callback_query_handler(
    func=lambda call: call.data.split('//')[0] == 'DELETE_TEMPL'
)
def train_template_id_for_delete(call):
    '''
    Функция работает при нажатии юзером на inline-кнопку
    при выборе шаблона тренировки, который он хочет удалить.
    '''
    while messages_for_delete:
        bot.delete_message(
            call.message.chat.id,
            messages_for_delete.pop(0)
        )
    bot.answer_callback_query(call.id)
    request = call.data.split('//')
    delete_template_of_training(request[1])


def main_logic(message):
    '''
    Юзер нажал на одну из кнопок главного меню
    и в этой функции происходит обработка этого действия.
    '''
    bot.send_message(
        message.chat.id,
        '...',
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
    elif text == MENU_COMMANDS[1]:
        trainings = get_all_trainings_of_user(user_id)
        for id in trainings:
            show_made_training(message, id)
    elif text == MENU_COMMANDS[2]:
        get_name = bot.send_message(
            chat_id,
            'Введи название шаблона:'
        )
        bot.register_next_step_handler(get_name, template_generating)
    elif text == MENU_COMMANDS[3]:
        user_configs_menu(message)
    else:
        bot.send_message(chat_id, DEFAULT_ANSWER)
        answer_to_menu(message)


@bot.message_handler(commands=["clear", "clean"])
def clear_database(message):
    '''
    Функция в дальнейшем будет удалена,
    но пока что играет незаменимую роль в тестировании.
    '''
    clear()
    bot.send_message(
        message.chat.id,
        'База данных очищена',
    )


bot.polling(none_stop=True)
