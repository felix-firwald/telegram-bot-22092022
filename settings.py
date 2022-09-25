from telebot import TeleBot


TOKEN = "5323459283:AAFOD4TZWofyC3PjcanJDq3PZV82l_GJrFg"
DEFAULT_ANSWER = 'Прости, но я тебя не понимаю'
MENU_COMMANDS = (
    'Новая тренировка',
    'Посмотреть свои тренировки',
    'Создать шаблон тренировки',
    'Настройки'
)

bot = TeleBot(TOKEN)
