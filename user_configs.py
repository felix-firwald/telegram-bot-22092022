from telebot import types

from database import (
    delete_template_of_training,
    get_templates_of_user
)
from settings import (
    bot
)


COMMANDS_SETTINGS = (
    'Редактировать шаблон',
    'Удалить шаблон',
    'Назад в меню'
)
WHAT_YOU_CAN = (
    'При помощи меню настроек '
    'ты можешь редактировать и удалять созданные тобой шаблоны'
)


def user_configs_menu(message):
    chat = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for command in COMMANDS_SETTINGS:
        markup.add(types.KeyboardButton(command))
    what_you_can = bot.send_message(
        chat,
        WHAT_YOU_CAN,
        reply_markup=markup
    )
    bot.register_next_step_handler(what_you_can, switcher)


def switcher(message):
    text = message.text
    if text == COMMANDS_SETTINGS[0]:
        get_name = bot.send_message(
            message.chat.id,
            'Укажи название шаблона, который ты хочешь отредактировать:',
            reply_markup=types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(
            get_name,
            edit_template
        )
    elif text == COMMANDS_SETTINGS[1]:
        get_name = bot.send_message(
            message.chat.id,
            'Укажи название шаблона, который ты хочешь удалить:',
            reply_markup=types.ReplyKeyboardRemove()
        )
        markup = types.InlineKeyboardMarkup()
        for template in get_templates_of_user(message.from_user.id):
            markup.add(types.InlineKeyboardButton(
                text=template.name,
                callback_data=f'DELETE_TEMPL//{template.id}'
            ))
    else:
        bot.send_message(
            message.chat.id,
            'Я НИЧЕГО НЕ ПОНЯЛА!',
            reply_markup=types.ReplyKeyboardRemove()
        )


def edit_template(message):
    name = message.text
    bot.send_message(
        message.chat.id,
        '<i>Этот функционал временно недоступен</i>',
        reply_markup=types.ReplyKeyboardRemove(),
        parse_mode='html'
    )


def delete_template(message):
    name = message.text
    final = delete_template_of_training(
        message.from_user.id,
        name
    )
    bot.send_message(
        message.chat.id,
        final
    )
