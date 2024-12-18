from fastapi import HTTPException
import asyncio
import logging
from services.weather_service import calculate_monthly_averages, get_city_coordinates
from aiocache import cached
from models.travel_models import (
    BestMonthResponse,
    CityComparison,
    ComparisonResponse,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CACHE_TTL = 3600


@cached(ttl=CACHE_TTL)
async def best_travel_month(
    city: str, min_temp: float, max_temp: float
) -> BestMonthResponse:
    """Get the best travel month for a city based on temperature preferences."""
    logger.info(
        f"Finding best travel month for {city} with temps {min_temp}-{max_temp}°C"
    )
    try:
        coordinates = await get_city_coordinates(city)
        months = range(1, 13)
        logger.info(f"Fetching monthly averages for {city}")
        monthly_averages = await asyncio.gather(
            *[calculate_monthly_averages(city, coordinates, month) for month in months],
            return_exceptions=True,
        )

        best_month = None
        best_diff = float("inf")
        best_details = {}

        for month, averages in enumerate(monthly_averages, start=1):
            if isinstance(averages, Exception):
                logger.error(f"Error processing month {month}: {str(averages)}")
                continue

            min_temp_diff = abs(min_temp - averages.min_temp_avg)
            max_temp_diff = abs(max_temp - averages.max_temp_avg)
            overall_diff = min_temp_diff + max_temp_diff

            if overall_diff < best_diff:
                best_month = month
                best_diff = overall_diff
                best_details = {
                    "min_temp_diff": round(min_temp_diff, 2),
                    "max_temp_diff": round(max_temp_diff, 2),
                    "overall_diff": round(overall_diff, 2),
                }

        if best_month is None:
            logger.error(f"No suitable travel month found for {city}")
            raise HTTPException(
                status_code=404, detail="No suitable travel month found."
            )
        result = BestMonthResponse(city=city, best_month=best_month, **best_details)
        logging.debug(f"Returned Result: {result}")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error analyzing travel months: {str(e)}",
        )


@cached(ttl=CACHE_TTL)
async def compare_cities_weather(cities: list, month: int) -> ComparisonResponse:
    """Compare historical weather conditions for multiple cities in a specific month."""
    logger.info(f"Comparing weather for cities: {cities}, month: {month}")
    try:
        comparisons = []

        for city in cities:
            coordinates = await get_city_coordinates(city)
            averages = await calculate_monthly_averages(city, coordinates, month)

            comparisons.append(
                CityComparison(
                    city=city,
                    month=month,
                    min_temp_avg=averages.min_temp_avg,
                    max_temp_avg=averages.max_temp_avg,
                )
            )
        logger.info(f"Successfully compared {len(comparisons)} cities")
        logger.debug(f"Data Returned {comparisons}")
        return ComparisonResponse(comparisons=comparisons)

    except HTTPException as e:
        logger.error(f"HTTP error in city comparison: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in city comparison: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
