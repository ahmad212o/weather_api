from fastapi import FastAPI
from routes import weather, travel, metrics
from aiocache import Cache, caches
import os

app = FastAPI()

caches.set_config({
    "default": {
        "cache": "aiocache.SimpleMemoryCache",  
        "serializer": {
            "class": "aiocache.serializers.JsonSerializer"  
        },
        "ttl": 3600  
    }
})


app.include_router(router=weather.router, prefix="/weather")
app.include_router(router=travel.router, prefix="/travel")
app.include_router(router=metrics.router, prefix="/metrics")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)