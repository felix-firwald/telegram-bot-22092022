from telebot import types
from peewee import SqliteDatabase, IntegrityError

from database import (
    save_template_training,
    save_template_exercise,
    save_training,
    save_end_of_training,
    save_exercise,
    get_exercises_of_training,
    delete_training
)
from formatting import formatting_data_for_training
from settings import bot, USE_MENU

db = SqliteDatabase('data.db')

messages_for_delete = []
g_ex = 'Теперь укажи названия упражнений — по одному на каждое сообщение.'


def template_generating(message):
    """
    Функция, которая пытается сохранить созданный шаблон тренировки.
    """
    try:
        training = save_template_training(message)
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
    """
    Функция генерации шаблона упражнения.
    Ожидает получить либо название шаблона, либо "да, это всё".
    """
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
        save_template_exercise(message, training)
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
    """
    Функция, которая предложит юзеру при создании
    тренировки отменить её (тренировка без единого
    привязанного к ней упражнения невалидна и удаляется
    из базы) или записать упражнение.
    """
    training = save_training(message, data)
    while messages_for_delete:
        bot.delete_message(
            message.chat.id,
            messages_for_delete.pop(0)
        )
    bot.pin_chat_message(chat_id=message.chat.id, message_id=message_id)
    buttons = (
        'Записать упражнение',
        'Отменить тренировку'
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
    """
    Функция разветвляет логику:
    а) если юзер хочет записать упражнение,
    то боту нужно знать, какое именно упражнение
    сейчас будет записано, поэтому бот запросит номер;
    б) если юзер хочет закончить тренировку,
    то бот перебросит в функцию training_complete.
    """
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
    elif text == 'Закончить тренировку' or text == 'Отменить тренировку':
        training_complete(message, training)


def get_number_of_ex(message, training, data):
    """
    Функция проверяет, что указанный номер упражнения
    в шаблоне действительно есть, и если такой есть,
    то она перебрасывает юзера в get_weight функцию.
    """
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
    """
    Функция спрашивает у юзера: с каким весом
    ты делал упражнение? (в килограммах)
    и перебрасывает в функцию choose_weight.
    """
    how_many = bot.send_message(
        message.chat.id,
        'Какой вес?',
        reply_markup=types.ReplyKeyboardRemove()
    )
    bot.register_next_step_handler(
        how_many,
        choose_weight,
        data,
        exercise,
        training
    )


def training_complete(message, training):
    """
    Функция открепляет сообщение с планом тренировки,
    чтобы оно не мешалось в чате, а также сохраняет
    время окончания тренировки, после чего
    перебрасывает в show_made_training функцию.
    """
    bot.send_message(
        message.chat.id,
        f'Тренировка окончена! {USE_MENU}',
        reply_markup=types.ReplyKeyboardRemove()
    )
    bot.unpin_all_chat_messages(message.chat.id)
    show_made_training(message, save_end_of_training(training))


def show_made_training(message, id):
    """
    Функция выводит в текстовом виде информацию
    о проведенной тренировке, если хотя бы одно
    упражнение ссылается на объект тренировки.
    """
    training = get_exercises_of_training(id)
    exercises = [[i.name, i.weight, i.count] for i in training[0]]
    if not exercises:
        string = (
            '<i>Нет данных.'
            '\nТренировка не была сохранена.</i>'
        )
        delete_training(id)
    else:
        string = formatting_data_for_training(training, exercises)
    bot.send_message(
        message.chat.id,
        string,
        parse_mode='html',
        reply_markup=types.ReplyKeyboardRemove()
    )


def choose_weight(message, data, exercise, training):
    """
    Функция проверяет указанный юзером вес на валидность,
    если вес невалиден - запрашивает вес снова.
    Если вес валиден - спрашивает, сколько раз
    сделано упражнение в рамках этого подхода.
    """
    try:
        weight = int(message.text)
    except ValueError:
        if_error = bot.send_message(
            message.chat.id,
            'Неправильно! Укажи вес цифрами'
        )
        bot.register_next_step_handler(
            if_error,
            choose_weight,
            data,
            exercise,
            training
        )
    else:
        how_many = bot.send_message(
            message.chat.id,
            'Сколько раз?'
        )
        bot.register_next_step_handler(
            how_many,
            choose_times,
            data,
            exercise,
            weight,
            training
        )


def choose_times(message, data, exercise, weight, training):
    """
    Функция сохраняет "разы" и "вес",
    а затем перебрасывает в what_to_do_next функцию.
    ВНИМАНИЕ: функция не валидирует количество раз,
    так как иногда я могу указывать "не считал".
    """
    save_exercise(message.text, training, exercise, weight)
    what_to_do_next(message, data, exercise, training)


def what_to_do_next(message, data, exercise, training):
    """
    После записи упражнения на сцену выходит эта функция.
    Она предоставляет юзеру выбор - он может продолжить
    заполнять текущее упражнение, может начать заполнять
    другое упражнение, а может завершить тренировку.
    """
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
    """
    Функция обрабатывает ответ юзера по поводу того,
    что делать после очередного заполнения упражнения.
    """
    text = message.text
    if text == 'Добавить подход':
        get_weight(message, data, exercise, training)
    elif text == 'Следующее упражнение':
        switch(message, training, data)
    elif text == 'Закончить тренировку':
        training_complete(message, training)
    else:
        bot.send_message(
            message.chat.id,
            'Нет такого варианта!',
        )
        what_to_do_next(message, data, exercise, training)
