import aiohttp
from fastapi import HTTPException
from calendar import monthrange
import asyncio
import logging
from aiocache import cached
from models.weather_models import (
    Coordinates,
    WeatherResponse,
    WeatherRequestParams,
    DailyData,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CACHE_TTL = 3600
MIN_YEAR = 2018
MAX_YEAR = 2024
GEOCODING_API_URL = "https://geocoding-api.open-meteo.com/v1/search"
CLIMATE_API_URL = "https://climate-api.open-meteo.com/v1/climate"


def get_last_day_of_month(year: int, month: int) -> int:
    """Get the last day of a specific month in a year."""
    _, last_day = monthrange(year, month)
    return last_day


@cached(ttl=CACHE_TTL)
async def get_city_coordinates(city: str) -> Coordinates:
    """Fetch geographical coordinates for a given city name."""
    logger.info(f"Fetching coordinates for city: {city}")
    params = {"name": city, "count": 1, "format": "json", "language": "en"}

    async with aiohttp.ClientSession() as session:
        async with session.get(GEOCODING_API_URL, params=params) as response:
            if response.status != 200:
                logger.error(
                    f"Failed to fetch coordinates for {city}. Status: {response.status}"
                )
                raise HTTPException(
                    status_code=response.status,
                    detail=f"Failed to fetch coordinates for city '{city}'",
                )
            data = await response.json()
            results = data.get("results")
            logger.debug(f"Returned results: {results}")
            if not results:
                logger.warning(f"City not found: {city}")
                raise HTTPException(status_code=404, detail=f"City '{city}' not found.")
            return Coordinates(
                latitude=results[0]["latitude"], longitude=results[0]["longitude"]
            )


@cached(ttl=CACHE_TTL)
async def fetch_weather_data(
    session, coordinates: Coordinates, year: int, month: int
) -> DailyData:
    """Fetch historical weather data for a specific location and time period."""
    logger.info(
        f"Fetching weather data for coordinates: {coordinates.latitude}, {coordinates.longitude}, {year}-{month}"
    )
    params = WeatherRequestParams(
        latitude=coordinates.latitude,
        longitude=coordinates.longitude,
        start_date=f"{year}-{month:02d}-01",
        end_date=f"{year}-{month:02d}-{get_last_day_of_month(year, month)}",
        timezone="auto",
        disable_bias_correction="true",
        daily=["temperature_2m_max", "temperature_2m_min"],
    )
    try:
        async with session.get(CLIMATE_API_URL, params=params.model_dump()) as response:
            response.raise_for_status()
            data = await response.json()
            logger.info(f"Successfully fetched weather data for {year}-{month}")
            logger.debug(f"Returned data: {data}")
            return DailyData(**data.get("daily", {}))
    except Exception as e:
        logger.error(f"Error fetching weather data: {str(e)}")
        raise


@cached(ttl=CACHE_TTL)
async def calculate_monthly_averages(
    city: str, coordinates: Coordinates, month: int
) -> WeatherResponse:
    """Calculate average temperatures for a specific month across multiple years."""
    logger.info(f"Calculating monthly averages for {city}, month {month}")
    years = range(MIN_YEAR, MAX_YEAR)
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_weather_data(session, coordinates, year, month) for year in years
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    min_temps = []
    max_temps = []

    for result in results:
        min_temps.extend(result.temperature_2m_min)
        max_temps.extend(result.temperature_2m_max)

    if not min_temps or not max_temps:
        logger.error(f"No weather data available for {city} in month {month}")
        raise HTTPException(
            status_code=404,
            detail="No weather data available for the specified city and month.",
        )
    logger.info(f"Successfully calculated averages for {city}, month {month}")
    result = WeatherResponse(
        city=city,
        month=month,
        min_temp_avg=round(sum(min_temps) / len(min_temps), 2),
        max_temp_avg=round(sum(max_temps) / len(max_temps), 2),
    )
    logger.debug(f"Returned Result: {result}")
    return result


@cached(ttl=CACHE_TTL)
async def get_monthly_weather_averages(city: str, month: int) -> WeatherResponse:
    """Get monthly average temperatures for a city."""
    logger.info(f"Getting monthly weather averages for {city}, month {month}")

    try:
        coordinates = await get_city_coordinates(city)
        averages = await calculate_monthly_averages(city, coordinates, month)
        logger.info(f"Successfully retrieved monthly averages for {city}")
        logger.debug(f"Returned Averages: {averages}")
        return averages
    except HTTPException as e:
        logger.error(f"HTTP error for {city}: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error for {city}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
