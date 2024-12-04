import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_monthly_profile_endpoint():
    """Test the monthly weather profile endpoint."""
    response = client.get("/weather/monthly-profile?city=London&month=7")
    assert response.status_code == 200
    data = response.json()
    assert "city" in data
    assert "month" in data
    assert "min_temp_avg" in data
    assert "max_temp_avg" in data

    response = client.get("/weather/monthly-profile?city=London&month=13")
    assert response.status_code == 422

    response = client.get("/weather/monthly-profile?city=&month=7")
    assert response.status_code == 404

    response = client.get("/weather/monthly-profile")
    assert response.status_code == 422


def test_best_travel_month_endpoint():
    """Test the best travel month endpoint."""
    response = client.get("/travel/best-month?city=Paris&min_temp=15&max_temp=25")
    assert response.status_code == 200
    data = response.json()
    assert "city" in data
    assert "best_month" in data
    assert "min_temp_diff" in data
    assert "max_temp_diff" in data
    assert "overall_diff" in data


def test_compare_cities_endpoint():
    """Test the city comparison endpoint."""
    response = client.get("/travel/compare-cities?cities=London,Paris,Rome&month=7")
    assert response.status_code == 200
    data = response.json()
    assert "comparisons" in data
    assert len(data["comparisons"]) == 3

    response = client.get("/travel/compare-cities?cities=London,Paris&month=7")
    assert response.status_code == 200
    assert len(response.json()["comparisons"]) == 2

    response = client.get(
        "/travel/compare-cities?cities=London,Paris,Rome,Berlin,Madrid,Lisbon&month=7"
    )
    assert response.status_code == 400

    response = client.get("/travel/compare-cities?cities=London,Paris&month=13")
    assert response.status_code == 422

    response = client.get("/travel/compare-cities?cities=London&month=7")
    assert response.status_code == 400


def test_metrics_endpoint():
    """Test the metrics endpoint."""
    client.get("/weather/monthly-profile?city=London&month=7")
    client.get("/travel/best-month?city=Paris&min_temp=15&max_temp=25")
    client.get("/travel/compare-cities?cities=London,Paris&month=7")

    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()

    assert "routes" in data
    routes = data["routes"]

    for route in [
        "/weather/monthly-profile",
        "/travel/best-month",
        "/travel/compare-cities",
    ]:
        assert route in routes
        metrics = routes[route]
        assert "hits" in metrics
        assert "errors" in metrics
        assert "avg_time" in metrics
        assert "max_time" in metrics
        assert "min_time" in metrics


def test_error_responses():
    """Test error handling across endpoints."""
    response = client.get("/weather/monthly-profile?city=NonExistentCity&month=7")
    assert response.status_code == 404

    response = client.get("/travel/best-month?city=Paris&min_temp=abc&max_temp=25")
    assert response.status_code == 422

    response = client.get("/travel/compare-cities?month=7")
    assert response.status_code == 422


if __name__ == "__main__":
    pytest.main(["-v"])
