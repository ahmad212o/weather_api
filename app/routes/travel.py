from fastapi import APIRouter, Query, HTTPException
from services.travel_service import best_travel_month, compare_cities_weather
from utils.metrics import track_metrics
from aiocache import cached


router = APIRouter()


@router.get("/best-month")
@cached(ttl=3600)
@track_metrics("/travel/best-month")
async def best_travel_month_endpoint(
    city: str = Query(..., description="City name"),
    min_temp: float = Query(..., description="Preferred minimum temperature"),
    max_temp: float = Query(..., description="Preferred maximum temperature"),
):
    try:
        result = await best_travel_month(
            city=city, min_temp=min_temp, max_temp=max_temp
        )
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/compare-cities")
@cached(ttl=3600)
@track_metrics("/travel/compare-cities")
async def compare_cities_weather_endpoint(
    cities: str = Query(
        ..., description="Comma-separated list of city names (2-5 cities)"
    ),
    month: int = Query(..., ge=1, le=12, description="Month number (1-12)"),
):
    try:
        city_list = cities.split(",")
        if len(city_list) < 2 or len(city_list) > 5:
            raise HTTPException(
                status_code=400, detail="You must provide between 2 and 5 cities."
            )

        result = await compare_cities_weather(cities=city_list, month=month)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
