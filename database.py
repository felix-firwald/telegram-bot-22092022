import sqlite3
from datetime import datetime, timedelta

from peewee import SqliteDatabase

from models import (
    User,
    TemplateTraining,
    TemplateExercise,
    Training,
    Exercise
)

db = SqliteDatabase('data.db')


def save_template_training(message):
    with db:
        training = TemplateTraining.create(
            name=message.text.capitalize(),
            author=message.from_user.id
        )
        training.save()
    return training


def save_template_exercise(message, training):
    with db:
        exercise = TemplateExercise.create(
            template=training,
            name=message.text.capitalize()
        )
        exercise.save()
    return exercise


def save_training(message, data):
    with db:
        training = Training.create(
            start=datetime.now() + timedelta(hours=3),
            template=data[0],
            user=message.from_user.id
        )
        training.save()
    return training


def save_end_of_training(training):
    with db:
        training.end = datetime.now() + timedelta(hours=3)
        training.save()
    return training.id


def save_exercise(count, training, exercise, weight):
    with db:
        Exercise.create(
            name=exercise,
            count=int(count),
            weight=weight,
            training=training.id,
            time=datetime.now() + timedelta(hours=3)
        )


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
            return user
        except Exception:
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
        names.append(each.name)
    return (template_name.name, names)


def get_exercises_of_training(id):
    with db:
        exercises = Exercise.select().where(
            Exercise.training == id
        )
        training = Training.get(Training.id == id)
        name = TemplateTraining.get(
            TemplateTraining.id == training.template
        )
    return (
        exercises,
        name.name,
        training.start,
        training.end
    )


def get_all_trainings_of_user(id):
    with db:
        user = User.get(
            User.user_id == id
        )
        trainings = Training.select().where(
            Training.user == user
        )
        data = [one.id for one in trainings]
        print(data)
    return data


def delete_training(id):
    with db:
        training = Training.get(Training.id == id)
        training.delete_instance()


def delete_template_of_training(id):
    with db:
        template = TemplateTraining.get(
            TemplateTraining.id == id
        )
        template.delete_instance()
