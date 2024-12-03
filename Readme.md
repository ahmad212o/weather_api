# Weather and Travel API

A production-ready REST API for retrieving historical weather data and travel recommendations based on weather preferences. The API utilizes the Open-Meteo Climate API to provide accurate historical weather information from 2018 to 2023.

## Features
- **Weather**: Fetch monthly weather profiles for cities.
- **Travel**: Compare travel insights across destinations.
- **Metrics**: Monitor API performance and usage.

## Async API Calls
This application leverages FastAPI's asynchronous capabilities to provide high-performance, non-blocking API calls.

## Memory Cache

This API uses an **in-memory caching mechanism** powered by the `aiocache` library. In-memory caching is ideal for **development** and **testing environments** as it stores data temporarily in RAM. 

## Requirements
- Python 3.8+  

## Setup
1. Clone the repository and navigate to the directory:
   ```bash
   git clone git@github.com:ahmad212o/weather_api.git && cd weather_api

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate 
3. Install the dependencies:
    ```bash
   pip install -r requirements.txt
4. Run the application on ip: 0.0.0.0  port: 8000:
     ```bash
     python main.py


