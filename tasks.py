from __future__ import annotations

import csv
import logging
from dataclasses import dataclass
from threading import Thread, Lock

from api_client import YandexWeatherAPI
from mytypes import (
    CityAVGDict,
    CityDict,
    CityResultDict,
    DateAVGDict,
    DateDict
)


class DataFetchingTask:
    """Получение данных через API c YandexWeatherAPI."""

    @staticmethod
    def get_data(city: str) -> CityDict:
        """Получение данных для города по API.

        Args:
            city (str): имя города.
        Returns:
            dict: имя города и все данные, полученные для него.
        """
        yw = YandexWeatherAPI()
        if response := yw.get_forecasting(city):
            return {'city_name': city, 'forecasts': response['forecasts']}


class DataCalculationTask:
    """Вычисление средних температур и количества сухих дней
    за все дни в одном городе.
    """

    AVG_TEMP: float = float('-inf')
    AVG_DRY: float = float('-inf')
    HOUR_MIN = 9
    HOUR_MAX = 19

    def day_data(self, date: DateDict) -> DateAVGDict:
        """Вычисление данных по температуре и сухим часам за один день.

        Args:
            date (dict): дата и  список словарей данных за день по часам.
        Returns:
            dict: {'date': date, 'avg_temp': avg_temp, 'count_dry': count_dry}.
        """

        not_full_data: DateAVGDict = {
            'date': date['date'], 'avg_temp': 0, 'count_dry': 0
        }
        if not date.get('hours'):
            return not_full_data

        dry = ('clear', 'partly-cloudy', 'cloudy', 'overcast')

        sum_temp = num_temp = count_dry = 0
        for hour in date['hours']:
            if int(hour['hour']) < self.HOUR_MIN:
                continue
            elif int(hour['hour']) > self.HOUR_MAX:
                break
            sum_temp += hour['temp']
            num_temp += 1
            if hour['condition'] in dry:
                count_dry += 1

        if num_temp:
            return {
                'date': date['date'],
                'avg_temp': float("{0:.1f}".format(sum_temp / num_temp)),
                'count_dry': count_dry,
            }
        else:
            return not_full_data

    def avg_data(self, city_data: DateAVGDict):
        """Подсчёт средних значений температуры и количества сухих дней
            в городе за все дни.

        Args:
            city_data (dict): словарь: средние данные по дням.
        """
        if city_data.get('avg_temp'):
            if self.AVG_TEMP == float('-inf'):
                self.AVG_TEMP = city_data['avg_temp']
                self.AVG_DRY = city_data['count_dry']
            else:
                self.AVG_TEMP = (self.AVG_TEMP + city_data['avg_temp']) / 2
                self.AVG_DRY = (self.AVG_DRY + city_data['count_dry']) / 2

    def city_data(self, city_forecasts: CityDict) -> CityResultDict:
        """Вычисление данных по температуре и сухим часам по каждому
        дню в одном городе.

        Args:
            city_forecasts (dict): словарь: город и данные о погоде в нем.
        Returns:
            dict: {'city': city, 'data': {'date': 'date', 'avg_temp': avg_temp,
                   'count_dry': count_dry}, 'avg': (avg_temp, avg_count_dry)}.
        """

        city_name = city_forecasts['city_name']
        logging.info(f'Начинаем расчёт для города {city_name}')
        logging.info('Начинаем расчёт средних значений по дням '
                     f'для города {city_name}')
        city_data: CityResultDict = {
            'city': city_name,
            'data': [
                self.day_data(date)
                for date in city_forecasts['forecasts']
            ],
            'avg': {}
        }
        logging.info('Завершили расчёт средних значений по дням '
                     f'для города {city_name}')

        logging.info('Начинаем расчёт средних значений за все дни '
                     f'для города {city_name}')
        for date in city_data['data']:
            self.avg_data(date)
        avg_temp = float("{0:.1f}".format(self.AVG_TEMP))
        avg_dry = float("{0:.1f}".format(self.AVG_DRY))
        logging.info(
            'Завершили расчёт средних значений за все дни '
            f'для города {city_name}.'
            f'avg_temp = {avg_temp}, avg_dry = {avg_dry}'
        )
        city_data['avg'] = {'avg_temp': avg_temp, 'avg_dry': avg_dry}
        return city_data


class DataAggregationTask:
    """Сохраняем обработанные данные в csv."""

    lock = Lock()

    def write_to_csv(self, obj: csv.writer, city: CityResultDict):
        """Запись информации о городе в csv.

        Args:
            obj (csv.writer): объекст csv-файла.
            city (CityResultDict): информация о городе.
        """

        with self.lock:
            row = [city['city']]
            row.extend(iter(city['data']))
            row.extend(
                (city['avg']['avg_temp'], city['avg']['avg_dry'])
            )
            obj.writerow(row)

    def to_csv(self, data: list[CityResultDict]):
        """Запись информации о всех городах в csv.

        Args:
            data (list[CityResultDict]): список словарей
                                         с информацией о городах.
        """

        names = ['city']
        names.extend(f'day_{i + 1}' for i in range(len(data[0]['data'])))
        names.extend(('avg_temp', 'avg_dry'))

        with open('cities_data.csv', mode='w', encoding='utf-8') as w_file:
            file_writer = csv.writer(w_file, delimiter=',')
            file_writer.writerow(names)

            thread: list[Thread] = [Thread()] * len(data)
            for number, city in enumerate(data):
                thread[number] = Thread(
                    target=self.write_to_csv, args=(file_writer, city)
                )
                thread[number].start()
            for number in range(len(data)):
                thread[number].join()


@dataclass
class City:
    """Класс для сравнения городов."""

    __slots__ = ['name', 'temp', 'dry']

    def __init__(self, data: CityAVGDict):
        self.name: str = data['city']
        self.temp: float = data['avg']['avg_temp']
        self.dry: float = data['avg']['avg_dry']

    def __str__(self):
        return f'{self.name}: temp={self.temp}, dry={self.dry}'

    def __lt__(self, obj: City) -> bool:
        return ((-self.temp, -self.dry)
                < (-obj.temp, -obj.dry))


class DataAnalyzingTask:
    """Определяем самый благоприятный город."""

    def __init__(self):
        self.best_city: City = City(
            {'city': 'ZZ', 'avg': {"avg_temp": -99, "avg_dry": -99}}
        )

    def compare(self, city: City):
        """Поиск города с лучшими параметрами.

        Args:
            self (City): объект класса City.
        """

        logging.info(f"Сравниваем:  {city} и {self.best_city}.")
        if city < self.best_city:
            self.best_city = city
        logging.info(f'Пока лучший город {self.best_city}')

    def rating(self, cities: list[CityResultDict]) -> City:
        """Определяем самый благориятный город.

        Args:
            self (dict): словарь: город и средние данные о погоде в нем.
        Returns:
            BEST_CITY (City): лучший город с его средними парамтерами.
        """

        for city_data in cities:
            logging.info(f"Проверяем город {city_data['city']}.")
            self.compare(
                City({'city': city_data['city'], 'avg': city_data['avg']})
            )

        return self.best_city
