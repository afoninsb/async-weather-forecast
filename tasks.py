from __future__ import annotations

import json
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from api_client import YandexWeatherAPI
from mytypes import (CityAVGDict, CityDict, CityResultDict, DateAVGDict,
                     DateDict)

thread_lock = threading.Lock()


class DataFetchingTask:
    """получение данных через API c YandexWeatherAPI."""

    @staticmethod
    def get_data(city: str) -> CityDict:
        ywAPI = YandexWeatherAPI()
        if response := ywAPI.get_forecasting(city):
            return {'city_name': city, 'forecasts': response['forecasts']}
        else:
            return {}


class DataCalculationTask:
    """Вычисление средних температур и количества сухих дней
    за все дни в одном городе.
    """

    AVG_TEMP: float = float('-inf')
    AVG_DRY: float = float('-inf')

    @staticmethod
    def day_data(date: DateDict) -> DateAVGDict:
        """Вычисление данных по температуре и сухим часам за один день.
        Args:
            day (dict): дата и  список словарей данных за день по часам.
        Returns:
            dict: {'date': date, 'avg_temp': avg_temp, 'count_dry': count_dry}.
        """

        if not date.get('hours'):
            return {'date': date['date'], 'avg_temp': 0, 'count_dry': 0}

        dry = ('clear', 'partly-cloudy', 'cloudy', 'overcast')

        sum_temp = num_temp = count_dry = 0
        for hour in date['hours']:
            if int(hour['hour']) < 9:
                continue
            elif int(hour['hour']) > 19:
                break
            sum_temp += hour['temp']
            num_temp += 1
            if hour['condition'] in dry:
                count_dry += 1

        return (
            {
                'date': date['date'],
                'avg_temp': float("{0:.1f}".format(sum_temp / num_temp)),
                'count_dry': count_dry,
            }
            if num_temp
            else {'date': date['date'], 'avg_temp': 0, 'count_dry': 0}
        )

    def avg_data(self, city_data: DateAVGDict):
        """Подсчёт средних значений температуры и количества сухих дней
            в городе за все дни.
        Args:
            city_data (dict): словарь: город и данные о погоде в нем
                              по дням и часам.
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

        with ThreadPoolExecutor() as pool:
            city_data = pool.map(self.day_data, city_forecasts['forecasts'])
        city_data = list(city_data)
        with ThreadPoolExecutor() as pool:
            pool.map(self.avg_data, city_data)
        return {
            'city': city_forecasts['city_name'],
            'data': city_data,
            'avg': {
                'avg_temp': float("{0:.1f}".format(self.AVG_TEMP)),
                'avg_dry': float("{0:.1f}".format(self.AVG_DRY))
            }
        }


class DataAggregationTask:
    """Сохраняем обработанные данные в json."""

    @staticmethod
    def to_json(data: list[CityResultDict]):
        with open('cities_data.json', 'w') as outfile:
            json.dump(data, outfile)


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


class MyThread(threading.Thread):
    """Синхронизация потоков."""

    def __init__(self, city: City):
        threading.Thread.__init__(self)
        self.city = city

    def run(self):
        thread_lock.acquire()
        try:
            DataAnalyzingTask.compare(self.city)
        finally:
            thread_lock.release()


BEST_CITY = City({'city': 'ZZ', 'avg': {"avg_temp": -99, "avg_dry": -99}})


class DataAnalyzingTask:
    """Определяем самый благориятный город."""

    def compare(self: City):
        """Поиск города с лучшими параметрами.
        Args:
            self (City): объект класса City.
        """

        global BEST_CITY
        if self < BEST_CITY:
            BEST_CITY = self

    def raiting(self: list[CityResultDict]) -> City:
        """Определяем самый благориятный город.
        Args:
            self (dict): словарь: город и средние данные о погоде в нем.
        Returns:
            BEST_CITY (City): лучший город с его средними парамтерами.
        """

        global BEST_CITY
        thread = [0] * len(self)
        for number, city_data in enumerate(self):
            thread[number] = MyThread(
                City({'city': city_data['city'], 'avg': city_data['avg']}))
        for number, city_data in enumerate(self):
            thread[number].start()
        for number, city_data in enumerate(self):
            thread[number].join()
        return BEST_CITY
