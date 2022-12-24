import logging
import multiprocessing
from concurrent.futures import ThreadPoolExecutor

from tasks import (
    DataAggregationTask,
    DataAnalyzingTask,
    DataCalculationTask,
    DataFetchingTask
)
from utils import CITIES


def forecast_weather():
    """
    Анализ погодных условий по городам
    """

    # Получаем данные по API
    logging.info('Начинаем импорт json по API')
    with ThreadPoolExecutor() as pool:
        cities_data = pool.map(
            DataFetchingTask.get_data, CITIES, chunksize=len(CITIES)
        )
    if not cities_data:
        return
    logging.info('Импорт json по API завершён удачно')

    # Рассчитываем средние значения
    logging.info('Начинаем расчёт средних значений для всех городов')
    dct = DataCalculationTask()
    pool = multiprocessing.Pool()
    calculated_data = pool.map(dct.city_data, cities_data)
    if not calculated_data:
        logging.error(
            'Расчёт средних значений для всех городов вернул пустой словарь!'
        )
        return
    logging.info('Расчёт средних значений для всех городов завершён')

    # Сохраняем данные в csv
    logging.info('Сохраняем данные в файл')
    write_to_csv = DataAggregationTask()
    write_to_csv.to_csv(calculated_data)
    logging.info('Сохранение данных в файл завершено')

    pool.close()
    pool.join()

    # Определяем лучший город
    logging.info('Начинаем определение лучшего города')
    dat = DataAnalyzingTask()
    best_city = dat.rating(calculated_data)
    logging.info('Определение лучшего города завершено')

    return best_city


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        filename='forecasting-log.log',
        filemode='w',
        format=(
            '[%(asctime)s] %(levelname)s  '
            '[%(name)s.%(funcName)s:%(lineno)d] %(message)s'
        )
    )
    logging.info('### СТАРТ ВЫПОЛНЕНИЯ ПРИЛОЖЕНИЯ ###')
    print(forecast_weather())
    logging.info('### ЗАВЕРШЕНИЕ РАБОТЫ ПРИЛОЖЕНИЯ ###')
