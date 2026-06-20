"""
Rainfall Monitoring System
Fetches current weather data from OpenWeatherMap API
"""

import requests
import os
from datetime import datetime


def get_weather_data(city: str, api_key: str) -> dict:
    """
    Fetch current weather data for a given city.

    Args:
        city: Name of the city to get weather for
        api_key: OpenWeatherMap API key

    Returns:
        Dictionary with weather data or error information
    """
    # API endpoint
    url = "https://api.openweathermap.org/data/2.5/weather"

    # Parameters for the API request
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",  # Temperature in Celsius
    }

    try:
        # Send GET request to the API
        response = requests.get(url, params=params, timeout=10)

        # Handle HTTP error status codes
        if response.status_code == 401:
            return {
                "error": "Invalid API key. Please check your OpenWeatherMap API key."
            }
        elif response.status_code == 404:
            return {"error": f"City '{city}' not found. Please check the city name."}
        elif response.status_code != 200:
            return {"error": f"HTTP error {response.status_code}: {response.text}"}

        # Parse JSON response
        data = response.json()

        # Extract rainfall intensity (1-hour rainfall)
        # rainfall["1h"] contains rainfall in last 1 hour
        rainfall_mm_per_hour = 0
        if "rain" in data and "1h" in data["rain"]:
            rainfall_mm_per_hour = data["rain"]["1h"]

        # Extract temperature from main section
        temperature_celsius = data["main"]["temp"]

        # Extract and convert timestamp to readable format
        # API returns Unix timestamp
        timestamp_unix = data.get("dt", 0)
        timestamp = datetime.fromtimestamp(timestamp_unix).strftime("%Y-%m-%d %H:%M:%S")

        # Return formatted result
        return {
            "city": data["name"],
            "rainfall_mm_per_hour": float(rainfall_mm_per_hour),
            "temperature_celsius": float(temperature_celsius),
            "timestamp": timestamp,
        }

    except requests.exceptions.Timeout:
        return {"error": "Connection timed out. Please try again."}

    except requests.exceptions.ConnectionError:
        return {"error": "Network error. Please check your internet connection."}

    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

    except (KeyError, ValueError) as e:
        return {"error": f"Failed to parse response: {str(e)}"}


def check_alert(rainfall: float) -> dict:
    """
    Classify rainfall intensity and return alert information.

    Args:
        rainfall: Rainfall in mm per hour

    Returns:
        Dictionary containing:
            - level: "Green", "Yellow", or "Red"
            - color: "green", "yellow", or "red"
            - message: descriptive alert message

    Logic:
        - Green (Normal):     rainfall < 10 mm/h
        - Yellow (Moderate):  10 ≤ rainfall < 20 mm/h
        - Red (Heavy Alert):   rainfall ≥ 20 mm/h

    Edge Cases:
        - None or negative rainfall treated as 0 (Green/Normal)
    """
    # Handle edge cases
    if rainfall is None or rainfall < 0:
        rainfall = 0

    # Classify based on threshold
    if rainfall >= 20:
        return {
            "level": "Red",
            "color": "red",
            "message": "HEAVY RAIN ALERT - Take precautions!",
        }
    elif rainfall >= 10:
        return {
            "level": "Yellow",
            "color": "yellow",
            "message": "Moderate Warning - Rain expected to continue",
        }
    else:
        return {"level": "Green", "color": "green", "message": "Normal - No alert"}


def log_alert(city: str, rainfall: float, level: str) -> None:
    """
    Log alert to file for Yellow or Red levels.

    Args:
        city: Name of the city
        rainfall: Rainfall in mm/h
        level: Alert level ("Green", "Yellow", "Red")

    Log Format:
        [YYYY-MM-DD HH:MM:SS] | City: {city} | Rainfall: {rainfall} mm/h | Level: {level}

    Note:
        Only logs when level is "Yellow" or "Red"
        Appends to file (does not overwrite)
    """
    # Only log warnings and alerts
    if level not in ("Yellow", "Red"):
        return

    # Format timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Format log entry
    log_entry = (
        f"[{timestamp}] | City: {city} | Rainfall: {rainfall} mm/h | Level: {level}\n"
    )

    try:
        # Append to log file
        with open("alert_log.txt", "a") as f:
            f.write(log_entry)
    except IOError as e:
        print(f"Warning: Could not write to log file: {e}")


def main():
    """Example usage of the get_weather_data function with alerts."""

    # Get API key from environment variable or use placeholder
    api_key = os.getenv("OPENWEATHERMAP_API_KEY", "YOUR_API_KEY")

    # Example city
    city = "Bangkok"

    print(f"Fetching weather data for {city}...")
    print("-" * 40)

    # Get weather data
    result = get_weather_data(city, api_key)

    # Print results
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        rainfall = result["rainfall_mm_per_hour"]
        print(f"City:              {result['city']}")
        print(f"Rainfall (mm/hr):  {rainfall}")
        print(f"Temperature (°C):  {result['temperature_celsius']}")
        print(f"Timestamp:         {result['timestamp']}")

        # Check alert classification
        alert = check_alert(rainfall)
        print(f"Alert Level:       {alert['level']} ({alert['color']})")
        print(f"Message:           {alert['message']}")

        # Log alert if needed
        log_alert(city, rainfall, alert["level"])


if __name__ == "__main__":
    main()
