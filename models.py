from datetime import datetime
from peewee import (
    SqliteDatabase,
    Model,
    PrimaryKeyField,
    IntegerField,
    CharField,
    ForeignKeyField,
    DateTimeField,
    TimeField
)


db = SqliteDatabase('data.db')


class User(Model):
    """
    Класс пользователя, который написал боту.
    Если пользователь написал боту впервые - создать объект в базе.
    Если нет - ничего не создавать.
    """
    id = PrimaryKeyField(unique=True)
    chat_id = IntegerField()
    user_id = IntegerField()

    class Meta:
        database = db
        order_by = 'id'


class TemplateTraining(Model):
    """
    Класс, хранящий шаблоны тренировок.
    """
    id = PrimaryKeyField(unique=True)
    author = ForeignKeyField(User, to_field='user_id')
    name = CharField(max_length=30)

    class Meta:
        indexes = (
            (('author', 'name'), True),
        )
        database = db
        order_by = 'id'


class TemplateExercise(Model):
    """
    Класс, хранящий виды упражнений для шаблонов.
    """
    id = PrimaryKeyField(unique=True)
    template = ForeignKeyField(TemplateTraining, to_field='id')
    name = CharField(max_length=75)

    class Meta:
        indexes = (
            (('template', 'name'), True),
        )
        database = db
        order_by = 'id'


class Training(Model):
    """
    Класс, хранящий тренировки.
    """
    id = PrimaryKeyField(unique=True)
    start = DateTimeField(default=datetime.now)
    end = DateTimeField(default=datetime.now)
    template = ForeignKeyField(TemplateTraining, to_field='name')
    user = ForeignKeyField(User, to_field='user_id')

    class Meta:
        database = db
        order_by = 'start'


class Exercise(Model):
    """
    Класс, хранящий сделанные упражнения.
    """
    id = PrimaryKeyField(unique=True)
    template = ForeignKeyField(TemplateExercise, to_field='name')
    training = ForeignKeyField(Training, to_field='id')
    time = TimeField(default=datetime.now)
    count = IntegerField()
    weight = IntegerField()

    class Meta:
        database = db
        order_by = 'time'


class Settings(Model):
    """
    Класс, хранящий настройки для юзера.
    weights - какие "веса" предлагать кнопками
    при описании подхода
    times - какие "количества раз" предлагать кнопками
    при описании подхода
    """
    id = PrimaryKeyField(unique=True)
    user = ForeignKeyField(User, to_field='user_id')
    weights = CharField()
    times = CharField()
