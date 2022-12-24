from tasks import City, DataCalculationTask


def test_right_data(get_datacalculationtask, right_data):
    # GIVEN в данных есть информация о погоде с 9 до 19 часов.
    # THEN возвращются: дата; средняя температура за указанный период;
    #                   сумма сухих часов за указанный период.

    hours_data = right_data['hours']
    result = get_datacalculationtask.day_data(right_data)
    assert right_data['date'] == result['date'], (
        'Проверьте, что `day_data` отдаёт правильную дату в словарь.'
    )
    avg = (hours_data[1]['temp'] + hours_data[2]['temp']) / 2
    assert float("{0:.1f}".format(avg)) == result['avg_temp'], (
        'Проверьте, что `day_data` правильно считает среднее значение '
        'температуры.'
    )
    assert 1 == result['count_dry'], (
        'Проверьте, что `day_data` правильно считает количество сухихи дней.'
    )


def test_empty_data(get_datacalculationtask, incomplete_data, empty_data):
    # GIVEN в данных нет информация о погоде с 9 до 19 часов или
    #       совсем отсутствует информация о погоде за весь день.
    # THEN возвращются словарь только с датой.

    data = (incomplete_data, empty_data)
    for dt in data:
        result = get_datacalculationtask.day_data(dt)
        assert result == {'date': dt['date'], 'avg_temp': 0, 'count_dry': 0}, (
            'Проверьте, что `day_data` отдаёт только дату, когда нет данных '
            'о погоде с 9 до 19 ч или данные о погоде в этот день отсутствуют'
            ' совсем.'
        )


def test_avg_data(avg_data):
    # GIVEN словарь с данными: дата, средняя температура, кол-во сухих часов.
    # THEN возвращются: среднее значение температуры и среднее значение
    #                   сухих часов.

    dct = DataCalculationTask()
    dct.avg_data(avg_data[0])
    assert dct.AVG_TEMP == avg_data[0]['avg_temp'], (
        'Проверьте, что при первой итерации `avg_data` возвращает '
        'подставляемое значение средней температуры.'
    )
    assert dct.AVG_DRY == avg_data[0]['count_dry'], (
        'Проверьте, что при первой итерации `avg_data` возвращает '
        'подставляемое значение количества сухих дней.'
    )
    dct.avg_data(avg_data[1])
    avg_temp = (avg_data[0]['avg_temp'] + avg_data[1]['avg_temp']) / 2
    assert dct.AVG_TEMP == avg_temp, (
        'Проверьте, что `avg_data` правильно считает '
        'значение средней температуры.'
    )
    avg_dry = (avg_data[0]['count_dry'] + avg_data[1]['count_dry']) / 2
    assert dct.AVG_DRY == avg_dry, (
        'Проверьте, что `avg_data` правильно считает '
        'значение среднего количества сухих дней.'
    )


def test_city_data(initial_city_data):
    # GIVEN словарь с данными по городу.
    # THEN возвращются данные по городу со средними значениями по дням.

    dct = DataCalculationTask()
    city_data = dct.city_data(initial_city_data)
    result = {
        'city': 'Moscow',
        'data': [
            {'date': '2022-05-26', 'avg_temp': (13 + 15) / 2, 'count_dry': 1},
            {'date': '2022-05-27', 'avg_temp': (12 + 13) / 2, 'count_dry': 2}
        ],
        'avg': {
            'avg_temp':
                float("{0:.1f}".format(((13 + 15) / 2 + (12 + 13) / 2) / 2)),
            'avg_dry': float("{0:.1f}".format((1 + 2) / 2))
        }
    }
    assert result == city_data, (
        'Проверьте, что `city_data` выдаёт данные в правильном формате.'
    )


def test_rating(get_dataanalyzingtask, for_rating):
    # GIVEN словарь с данными по трём городам.
    # THEN возвращются данные по городу с большей темпратурой и более сухой.

    result = get_dataanalyzingtask.rating(for_rating)
    assert str(result) == str(City(for_rating[1])), (
        'Проверьте, что `compare` правильно сравнивает объекты City '
        'по температуре и количеству сухих дней.'
    )
    assert str(result) != str(City(for_rating[0])), (
        'Проверьте, что `compare` правильно сравнивает объекты City '
        'по количеству сухих дней.'
    )
    assert str(result) != str(City(for_rating[2])), (
        'Проверьте, что `compare` правильно сравнивает объекты City '
        'по температуре.'
    )
