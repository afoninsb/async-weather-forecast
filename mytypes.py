from typing import TypedDict


class HourDict(TypedDict):
    hour: str
    hour_ts: int
    temp: int
    feels_like: int
    icon: str
    condition: str
    cloudness: int
    prec_type: int
    prec_strength: int
    is_thunder: bool
    wind_dir: str
    wind_speed: float
    wind_gust: float
    pressure_mm: int
    pressure_pa: int
    humidity: int
    uv_index: int
    soil_temp: int
    soil_moisture: float
    prec_mm: int
    prec_period: int
    prec_prob: int


class ForecastDict(TypedDict):
    date: str
    date_ts: int
    week: int
    sunrise: str
    sunset: str
    rise_begin: str
    set_end: str
    moon_code: int
    moon_text: int
    hours: list[HourDict]


class CityDict(TypedDict):
    city_name: str
    forecasts: list[ForecastDict]


class DateDict(TypedDict):
    date: str
    hours: list[HourDict]


class DateAVGDict(TypedDict):
    date: str
    avg_temp: float
    count_dry: float


class CityResultDict(TypedDict):
    city: str
    data: list[DateAVGDict]
    avg: dict[str, float]


class CityAVGDict(TypedDict):
    city: str
    avg: dict[str, float]
