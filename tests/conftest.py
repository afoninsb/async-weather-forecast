import pytest


@pytest.fixture()
def right_data():
    """Right data about weather in the city."""
    return {
        'date': '2022-05-26',
        'hours': [
            {'hour': '8', 'temp': 13, 'condition': 'cloudy'},
            {'hour': '9', 'temp': 15, 'condition': 'cloudy'},
            {'hour': '19', 'temp': 15, 'condition': 'light-rain'},
            {'hour': '20', 'temp': 14, 'condition': 'light-rain'},
        ]
    }


@pytest.fixture()
def incomplete_data():
    """Incomplete data about weather in the city."""
    return {
        'date': '2022-05-26',
        'hours': [
            {'hour': '7', 'temp': 13, 'condition': 'cloudy'},
            {'hour': '8', 'temp': 15, 'condition': 'cloudy'},
            {'hour': '20', 'temp': 15, 'condition': 'light-rain'},
            {'hour': '21', 'temp': 14, 'condition': 'light-rain'},
        ]
    }


@pytest.fixture()
def empty_data():
    """Empty data about weather in the city."""
    return {
        'date': '2022-05-26',
    }


@pytest.fixture()
def avg_data():
    """Данные для расчёта средних величин для города за все дни."""
    return [
        {'date': '2022-05-26', 'avg_temp': 17.7, 'count_dry': 7},
        {'date': '2022-05-27', 'avg_temp': 13.1, 'count_dry': 0}
    ]


@pytest.fixture()
def initial_city_data():
    """Начальные данные по городу для упаковки."""
    return {
        'city_name': 'Moscow',
        'forecasts': [{
            'date': '2022-05-26',
            'hours': [
                {
                    'hour': '8',
                    'temp': 13,
                    'condition': 'cloudy',
                },
                {
                    'hour': '9',
                    'temp': 13,
                    'condition': 'cloudy',
                },
                {
                    'hour': '19',
                    'temp': 15,
                    'condition': 'light-rain',
                },
                {
                    'hour': '20',
                    'temp': 14,
                    'condition': 'light-rain',
                },
            ]
        }, {
            'date': '2022-05-27',
            'hours': [
                {
                    'hour': '8',
                    'temp': 11,
                    'condition': 'light-rain',
                },
                {
                    'hour': '9',
                    'temp': 12,
                    'condition': 'cloudy',
                },
                {
                    'hour': '19',
                    'temp': 13,
                    'condition': 'cloudy',
                },
                {
                    'hour': '20',
                    'temp': 13,
                    'condition': 'cloudy',
                },
            ]
        },
        ]
    }
