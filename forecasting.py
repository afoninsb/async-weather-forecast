import logging
import multiprocessing

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
    pool = multiprocessing.Pool(processes=4)

    # Получаем данные
    logging.info('Начинаем импорт json по API')
    calculated_data = []
    if cities_data := pool.map(
        DataFetchingTask.get_data, CITIES, chunksize=len(CITIES)
    ):
        logging.info('Импорт json по API завершён удачно')

        # Вычисляем необходимые средние значения
        logging.info('Начинаем расчёт средних значений для всех городов')
        dct = DataCalculationTask()
        calculated_data = pool.map(
            dct.city_data, cities_data, chunksize=len(cities_data)
        )
    else:
        logging.error('Импорт json по API вернул пустой словарь!')

    pool.close()
    pool.join()

    if not calculated_data:
        logging.error(
            'Расчёт средних значений для всех городов вернул пустой словарь!'
        )
        return
    logging.info('Расчёт средних значений для всех городов завершён')

    logging.info('Сохраняем данные в файл')
    # Сохраняем данные в json
    DataAggregationTask.to_json(calculated_data)
    logging.info('Сохранение данных в файл завершено')

    # Определяем лучший город
    logging.info('Начинаем определение лучшего города')
    best_city = DataAnalyzingTask.rating(calculated_data)
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
