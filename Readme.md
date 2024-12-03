# Weather and Travel API

A lightweight FastAPI application for retrieving weather data, travel comparisons, and tracking metrics.

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
   git clone <repository-url> && cd <repository-name>

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


