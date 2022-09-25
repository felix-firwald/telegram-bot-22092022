import sqlite3
from peewee import SqliteDatabase

from models import (
    User,
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
