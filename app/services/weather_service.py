import aiohttp
from fastapi import HTTPException
from calendar import monthrange
from statistics import mean
import asyncio
from aiocache import cached


def get_last_day_of_month(year: int, month: int) -> int:
    _, last_day = monthrange(year, month)
    return last_day


@cached(ttl=3600)
async def get_city_coordinates(city: str) -> dict:
    geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city, "count": 1, "format": "json", "language": "en"}

    async with aiohttp.ClientSession() as session:
        async with session.get(geocoding_url, params=params) as response:
            if response.status != 200:
                raise HTTPException(
                    status_code=response.status,
                    detail=f"Failed to fetch coordinates for city '{city}'",
                )
            data = await response.json()
            results = data.get("results")
            if not results:
                raise HTTPException(status_code=404, detail=f"City '{city}' not found.")
            return {
                "latitude": results[0]["latitude"],
                "longitude": results[0]["longitude"],
            }


@cached(ttl=3600)
async def fetch_weather_data(
    session, latitude: float, longitude: float, year: int, month: int
) -> dict:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": f"{year}-{month:02d}-01",
        "end_date": f"{year}-{month:02d}-{get_last_day_of_month(year, month)}",
        "timezone": "auto",
        "disable_bias_correction": "true",
        "daily": ["temperature_2m_max", "temperature_2m_min"],
    }
    async with session.get(
        "https://climate-api.open-meteo.com/v1/climate", params=params
    ) as response:
        response.raise_for_status()
        data = await response.json()
        return data.get("daily", {})


@cached(ttl=3600)
async def calculate_monthly_averages(
    city: str, latitude: float, longitude: float, month: int
) -> dict:
    years = range(2018, 2024)
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_weather_data(session, latitude, longitude, year, month)
            for year in years
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    min_temps = []
    max_temps = []

    for result in results:
        if isinstance(result, dict):
            min_temps.extend(result.get("temperature_2m_min", []))
            max_temps.extend(result.get("temperature_2m_max", []))

    if not min_temps or not max_temps:
        raise HTTPException(
            status_code=404,
            detail="No weather data available for the specified city and month.",
        )

    return {
        "city": city,
        "month": month,
        "min_temp_avg": round(sum(min_temps) / len(min_temps), 2),
        "max_temp_avg": round(sum(max_temps) / len(max_temps), 2),
    }


@cached(ttl=3600)
async def get_monthly_weather_averages(city: str, month: int):
    try:
        coordinates = await get_city_coordinates(city)
        averages = await calculate_monthly_averages(
            city, coordinates["latitude"], coordinates["longitude"], month
        )
        return averages
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
