from datetime import datetime

from telebot import types
from peewee import SqliteDatabase, IntegrityError

from database import (
    save_template_training,
    save_template_exercise,
    save_training,
    save_end_of_training,
    save_exercise,
    get_exercises_of_training
)
from settings import bot, USE_MENU

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
            f'Шаблон создан!{USE_MENU}',
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
    text = message.text
    if text == 'Записать упражнение' or text == 'Следующее упражнение':
        give_number = bot.send_message(
            message.chat.id,
            'Укажи номер упражнения для записи',
            reply_markup=types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(
            give_number,
            get_number_of_ex,
            training,
            data
        )
    elif text == 'Закончить тренировку':
        bot.send_message(
            message.chat.id,
            'Тренировка окончена!',
            reply_markup=types.ReplyKeyboardRemove()
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
    else:
        get_weight(message, data, exercise, training)


def get_weight(message, data, exercise, training):
    how_many = bot.send_message(message.chat.id, 'Какой вес?')
    bot.register_next_step_handler(
        how_many,
        choose_weight,
        data,
        exercise,
        training
    )


def training_complete(message, training):
    show_made_training(message, save_end_of_training(training))


def show_made_training(message, id):
    format = '%H:%M'
    training = get_exercises_of_training(id)
    exercises = [[i.name, i.weight, i.count] for i in training[0]]
    name, start_time, end_time = training[1], training[2], training[3]
    duration = (end_time - start_time).strftime(format)
    del training
    start_time = start_time.strftime(format)
    end_time = end_time.strftime(format)

    validation_dict = dict()
    for i in range(len(exercises)):
        ex = exercises[i]
        validation_dict.setdefault(ex[0], [])

    for key, value in validation_dict.items():
        for exer in exercises:
            if key == exer[0]:
                value.append([exer[1], exer[2]])
    count = 0
    string = (
        f'{name}\n'
        f'\n<i>Начало: {start_time}'
        f'\nКонец: {end_time}'
        f'\nДлительность: {duration}</i>'
    )
    del duration
    for key, value in validation_dict.items():
        count += 1
        string += f'\n\n{count}. {key}'
        for weight, times in value:
            string += f'\n - {weight} кг {times} раз'
    bot.send_message(
        message.chat.id,
        string,
        parse_mode='html',
        reply_markup=types.ReplyKeyboardRemove()
    )


def choose_weight(message, data, exercise, training):
    how_many = bot.send_message(
        message.chat.id,
        'Сколько раз?'
    )
    weight = message.text
    bot.register_next_step_handler(
        how_many,
        choose_times,
        data,
        exercise,
        weight,
        training
    )


def choose_times(message, data, exercise, weight, training):
    save_exercise(message.text, training, exercise, weight)
    buttons = (
        'Добавить подход',
        'Следующее упражнение',
        'Закончить тренировку'
    )
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    for button in buttons:
        markup.add(types.KeyboardButton(button))
    what_to_do = bot.send_message(
        message.chat.id,
        'Что дальше?',
        reply_markup=markup
    )
    bot.register_next_step_handler(
        what_to_do,
        switch_2,
        data,
        exercise,
        training
    )


def switch_2(message, data, exercise, training):
    text = message.text
    if text == 'Добавить подход':
        get_weight(message, data, exercise, training)
    elif text == 'Следующее упражнение':
        # get_number_of_ex(message, training, data)
        switch(message, training, data)
    elif text == 'Закончить тренировку':
        bot.send_message(
            message.chat.id,
            f'Тренировка окончена! {USE_MENU}',
            reply_markup=types.ReplyKeyboardRemove()
        )
        training_complete(message, training)
    else:
        bot.send_message(
            message.chat.id,
            'Нет такого варианта блять!',
        )
