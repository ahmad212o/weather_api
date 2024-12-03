from functools import wraps
import time
from statistics import mean
from typing import Dict, Any

class MetricsTracker:
    def __init__(self):
        self.metrics = {
            "/weather/monthly-profile": {"hits": 0, "errors": 0, "times": []},
            "/travel/best-month": {"hits": 0, "errors": 0, "times": []},
            "/travel/compare-cities": {"hits": 0, "errors": 0, "times": []}
        }
    
    def track(self, route: str, execution_time: float, error: bool = False):
        if route in self.metrics:
            self.metrics[route]["hits"] += 1
            self.metrics[route]["times"].append(execution_time)
            if error:
                self.metrics[route]["errors"] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        result = {"routes": {}}
        for route, data in self.metrics.items():
            times = data["times"]
            result["routes"][route] = {
                "route_name": route,
                "hits": data["hits"],
                "errors": data["errors"],
                "avg_time": round(mean(times), 2) if times else 0,
                "max_time": round(max(times), 2) if times else 0,
                "min_time": round(min(times), 2) if times else 0
            }
        return result

metrics = MetricsTracker()

def track_metrics(route: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            error = False
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                error = True
                raise e
            finally:
                execution_time = time.time() - start_time
                metrics.track(route, execution_time, error)
        return wrapper
    return decorator
