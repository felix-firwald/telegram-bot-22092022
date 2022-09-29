

def formatting_data_for_training(training, exercises):
    '''
    Информация из базы данных должна быть представлена
    в текстовом виде. Эта функция возвращает готовую строку.
    '''
    format = '%H:%M'
    format_date = '%d.%m.%Y'
    name, start_time, end_time = training[1], training[2], training[3]
    date = start_time.strftime(format_date)
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
        f'#<b>{name}</b> ({date})\n'
        f'\n<i>Начало: {start_time}'
        f'\nКонец: {end_time}</i>'
    )
    for key, value in validation_dict.items():
        count += 1
        string += f'\n\n{count}. {key}:'
        for weight, times in value:
            string += f'\n - {weight} кг {times} раз'
    return string
