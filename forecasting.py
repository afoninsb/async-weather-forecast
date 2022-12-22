# import logging
import multiprocessing

from tasks import (
    DataFetchingTask,
    DataCalculationTask,
    DataAggregationTask,
    DataAnalyzingTask,
)
from utils import CITIES


def forecast_weather():
    """
    Анализ погодных условий по городам
    """
    pool = multiprocessing.Pool(processes=4)

    # Получаем данные
    cities_data = pool.map(
        DataFetchingTask.get_data, CITIES, chunksize=len(CITIES)
    )

    # Вычисляем необходимые средние значения
    dct = DataCalculationTask()
    calculated_data = pool.map(
        dct.city_data, cities_data, chunksize=len(cities_data)
    )

    pool.close()
    pool.join()

    # Сохраняем данные в json
    DataAggregationTask.to_json(calculated_data)

    # Определяем лучший город
    print(DataAnalyzingTask.raiting(calculated_data))


if __name__ == "__main__":
    forecast_weather()
