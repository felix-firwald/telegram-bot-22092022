from datetime import datetime
from peewee import (
    SqliteDatabase,
    Model,
    PrimaryKeyField,
    IntegerField,
    CharField,
    ForeignKeyField,
    DateTimeField,
    TimeField,
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
    author = ForeignKeyField(
        User,
        to_field='user_id',
        backref='trainings'
    )
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
    template = ForeignKeyField(
        TemplateTraining,
        to_field='id',
        backref='tasks'
    )
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
    end = DateTimeField(null=True)
    template = ForeignKeyField(
        TemplateTraining,
        to_field='name',
        related_name='trainings'
    )
    user = ForeignKeyField(
        User,
        to_field='user_id',
        related_name='trainings'
    )

    class Meta:
        database = db
        order_by = 'start'


class Exercise(Model):
    """
    Класс, хранящий сделанные упражнения.
    """
    id = PrimaryKeyField(unique=True)
    name = CharField()
    training = ForeignKeyField(
        Training,
        to_field='id',
        related_name='exercises'
    )
    time = TimeField(default=datetime.now)
    count = IntegerField()
    weight = IntegerField()

    class Meta:
        database = db
        order_by = 'time'
