import aiohttp
from fastapi import HTTPException
from calendar import monthrange
import asyncio
from aiocache import cached
from models.weather_models import (
    Coordinates,
    WeatherResponse,
    WeatherRequestParams,
    DailyData,
)


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
    params = {"name": city, "count": 1, "format": "json", "language": "en"}

    async with aiohttp.ClientSession() as session:
        async with session.get(GEOCODING_API_URL, params=params) as response:
            if response.status != 200:
                raise HTTPException(
                    status_code=response.status,
                    detail=f"Failed to fetch coordinates for city '{city}'",
                )
            data = await response.json()
            results = data.get("results")
            if not results:
                raise HTTPException(status_code=404, detail=f"City '{city}' not found.")
            return Coordinates(
                latitude=results[0]["latitude"], longitude=results[0]["longitude"]
            )


@cached(ttl=CACHE_TTL)
async def fetch_weather_data(
    session, coordinates: Coordinates, year: int, month: int
) -> DailyData:
    """Fetch historical weather data for a specific location and time period."""
    params = WeatherRequestParams(
        latitude=coordinates.latitude,
        longitude=coordinates.longitude,
        start_date=f"{year}-{month:02d}-01",
        end_date=f"{year}-{month:02d}-{get_last_day_of_month(year, month)}",
        timezone="auto",
        disable_bias_correction="true",
        daily=["temperature_2m_max", "temperature_2m_min"],
    )

    async with session.get(CLIMATE_API_URL, params=params.model_dump()) as response:
        response.raise_for_status()
        data = await response.json()
        return DailyData(**data.get("daily", {}))


@cached(ttl=CACHE_TTL)
async def calculate_monthly_averages(
    city: str, coordinates: Coordinates, month: int
) -> WeatherResponse:
    """Calculate average temperatures for a specific month across multiple years."""
    years = range(MIN_YEAR, MAX_YEAR)
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_weather_data(session, coordinates, year, month) for year in years
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        print(results)
    min_temps = []
    max_temps = []

    for result in results:
        min_temps.extend(result.temperature_2m_min)
        max_temps.extend(result.temperature_2m_max)

    if not min_temps or not max_temps:
        raise HTTPException(
            status_code=404,
            detail="No weather data available for the specified city and month.",
        )

    return WeatherResponse(
        city=city,
        month=month,
        min_temp_avg=round(sum(min_temps) / len(min_temps), 2),
        max_temp_avg=round(sum(max_temps) / len(max_temps), 2),
    )


@cached(ttl=CACHE_TTL)
async def get_monthly_weather_averages(city: str, month: int) -> WeatherResponse:
    """Get monthly average temperatures for a city."""
    try:
        coordinates = await get_city_coordinates(city)
        averages = await calculate_monthly_averages(city, coordinates, month)
        return averages
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
