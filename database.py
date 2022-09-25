import sqlite3
from peewee import SqliteDatabase

from models import (
    User,
    TemplateTraining,
    TemplateExercise
)

db = SqliteDatabase('data.db')


def clear():
    connection = sqlite3.connect("data.db")
    with connection:
        cursor = connection.cursor()
        models = [
            'user',
            'templatetraining',
            'templateexercise',
            'training',
            'exercise'
        ]
        for model in models:
            cursor.execute(f'''
            DELETE from {model}
            WHERE id > 0
            ''')
    return True


def get_user_or_create(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    with db:
        try:
            user = User.get(User.user_id == user_id)
            print("пользователь есть")
            return user
        except Exception:
            print("пользователя нет")
            user = User.create(
                user_id=user_id,
                chat_id=chat_id
            )
            user.save()
            return user


def get_templates_of_user(user_id):
    with db:
        templates = TemplateTraining.select().where(
            TemplateTraining.author == user_id
        )
    return templates


def get_exercises_of_template(id):
    '''
    возвращает кортеж,
    где первый элемент - имя шаблона, второй - упражнения (names)
    '''
    with db:
        template_name = TemplateTraining.get(TemplateTraining.id == id)
        exercises = TemplateExercise.select().where(
            TemplateExercise.template == template_name
        )
    names = list()
    for each in list(exercises):
        print(each)
        names.append(each.name)
    return (template_name.name, names)
