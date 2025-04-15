import requests
import os
from typing import Optional
from dataclasses import dataclass

@dataclass
class WeatherInfo:
    temperature: float
    description: str
    humidity: int
    wind_speed: float

def get_weather(city: str) -> str:
    """Fetch current weather for a city using OpenWeatherMap API.
    
    Args:
        city: Name of the city
    """
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        weather = WeatherInfo(
            temperature=data["main"]["temp"],
            description=data["weather"][0]["description"],
            humidity=data["main"]["humidity"],
            wind_speed=data["wind"]["speed"]
        )
        
        return f"Weather in {city}: {weather.temperature}°C, {weather.description}, " \
               f"humidity {weather.humidity}%, wind speed {weather.wind_speed} m/s"
    except requests.exceptions.RequestException as e:
        return f"Error fetching weather: {str(e)}"