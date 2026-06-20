"""
Rainfall Monitoring System
Fetches current weather data from OpenWeatherMap API
with alert classification and logging capabilities
"""

import requests
import os
from datetime import datetime


def fetch_weather(city: str, api_key: str) -> dict:
    """
    Fetch current weather data for a given city from OpenWeatherMap API.

    This function sends a GET request to the OpenWeatherMap API and retrieves
    current weather data including rainfall, temperature, and timestamp.

    Args:
        city: Name of the city to get weather for (e.g., "Bangkok", "Singapore")
        api_key: OpenWeatherMap API key (get free key at openweathermap.org)

    Returns:
        Dictionary with weather data:
            - city: City name
            - rainfall_mm_per_hour: Rainfall in mm/h (0 if no rain)
            - temperature_celsius: Temperature in °C
            - timestamp: Human-readable timestamp
        Or error dictionary:
            - error: Error message string

    Error Handling:
        - HTTP 401: Invalid API key
        - HTTP 404: City not found
        - Network errors: Connection issues
        - JSON parse errors: Invalid response
    """
    # API endpoint for current weather data
    url = "https://api.openweathermap.org/data/2.5/weather"

    # Parameters for the API request
    params = {
        "q": city,  # City name
        "appid": api_key,  # API key for authentication
        "units": "metric",  # Temperature in Celsius
    }

    try:
        # Send GET request to the API with timeout
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

        # Parse JSON response from API
        data = response.json()

        # Extract rainfall intensity (1-hour rainfall)
        # The "rain" key contains "1h" for last hour's rainfall
        rainfall_mm_per_hour = 0
        if "rain" in data and "1h" in data["rain"]:
            rainfall_mm_per_hour = data["rain"]["1h"]

        # Extract temperature from main section
        temperature_celsius = data["main"]["temp"]

        # Extract and convert timestamp to readable format
        # API returns Unix timestamp (seconds since 1970)
        timestamp_unix = data.get("dt", 0)
        timestamp = datetime.fromtimestamp(timestamp_unix).strftime("%Y-%m-%d %H:%M:%S")

        # Return formatted result dictionary
        return {
            "city": data["name"],
            "rainfall_mm_per_hour": float(rainfall_mm_per_hour),
            "temperature_celsius": float(temperature_celsius),
            "timestamp": timestamp,
        }
    # Handle connection timeout
    except requests.exceptions.Timeout:
        return {"error": "Connection timed out. Please try again."}

    # Handle network/connection errors
    except requests.exceptions.ConnectionError:
        return {"error": "Network error. Please check your internet connection."}

    # Handle any other request exceptions
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

    # Handle JSON parsing errors
    except (KeyError, ValueError) as e:
        return {"error": f"Failed to parse response: {str(e)}"}


def get_weather_data(city: str, api_key: str) -> dict:
    """
    Backwards-compatible wrapper for older callers named `get_weather_data`.

    Some modules (e.g., `weather_dashboard.py`) import `get_weather_data`.
    Keep this small adapter so both names work and external code doesn't break.
    """
    return fetch_weather(city, api_key)


def check_alert(rainfall: float, yellow_threshold: float = 10.0, red_threshold: float = 20.0) -> dict:
    """
    Classify rainfall intensity and return alert information.

    This function categorizes rainfall into three alert levels based on
    intensity thresholds commonly used in hydrology and weather monitoring.

    Args:
        rainfall: Rainfall in mm per hour (float)

    Returns:
        Dictionary containing:
            - level: "Green", "Yellow", or "Red"
            - color: Corresponding color name
            - message: Descriptive alert message

    Alert Classification Logic:
        - Green (Normal):     rainfall < 10 mm/h → Safe conditions
        - Yellow (Moderate):  10 ≤ rainfall < 20 mm/h → Caution advised
        - Red (Heavy Alert):  rainfall ≥ 20 mm/h → Take precautions

    Edge Cases:
        - None values are treated as 0
        - Negative rainfall is treated as 0
    """
    # Handle edge cases: None or negative rainfall
    if rainfall is None or rainfall < 0:
        rainfall = 0

    # Classify based on threshold values (configurable)
    # Ensure thresholds make sense: red should be >= yellow; if not, fall back to defaults
    try:
        y_th = float(yellow_threshold)
        r_th = float(red_threshold)
    except Exception:
        y_th = 10.0
        r_th = 20.0

    if r_th < y_th:
        # invalid configuration; use defaults
        y_th = 10.0
        r_th = 20.0

    if rainfall >= r_th:
        # Red level: Heavy rain alert
        return {
            "level": "Red",
            "color": "red",
            "message": "HEAVY RAIN ALERT - Take precautions!",
        }
    elif rainfall >= y_th:
        # Yellow level: Moderate warning
        return {
            "level": "Yellow",
            "color": "yellow",
            "message": "Moderate Warning - Rain expected to continue",
        }
    else:
        # Green level: Normal conditions
        return {"level": "Green", "color": "green", "message": "Normal - No alert"}


def log_alert(city: str, rainfall: float, level: str) -> None:
    """
    Log alert to file for Yellow (warning) and Red (alert) levels.

    This function writes alert events to a log file for record-keeping
    and later analysis. Only Yellow and Red alerts are logged.

    Args:
        city: Name of the city
        rainfall: Rainfall in mm/h
        level: Alert level ("Green", "Yellow", "Red")

    Log Format:
        [YYYY-MM-DD HH:MM:SS] | City: {city} | Rainfall: {rainfall} mm/h | Level: {level}

    Note:
        - Only logs when level is "Yellow" or "Red"
        - Appends to file (does not overwrite existing logs)
        - Handles file I/O errors gracefully
    """
    # Only log warnings (Yellow) and alerts (Red), not normal (Green)
    if level not in ("Yellow", "Red"):
        return

    # Format timestamp for log entry
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Format log entry with consistent structure
    log_entry = (
        f"[{timestamp}] | City: {city} | Rainfall: {rainfall} mm/h | Level: {level}\n"
    )

    try:
        # Append log entry to alert_log.txt
        with open("alert_log.txt", "a") as f:
            f.write(log_entry)
    except IOError as e:
        print(f"Warning: Could not write to log file: {e}")


def main():
    """
    Main function demonstrating the rainfall monitoring system.

    This function shows how to:
    1. Fetch weather data using fetch_weather()
    2. Check alert level using check_alert()
    3. Log alerts using log_alert()

    The API key can be provided via:
    - Environment variable: OPENWEATHERMAP_API_KEY
    - Default placeholder (replace with your own key)
    """
    # Get API key from environment variable or use default placeholder
    api_key = os.getenv("OPENWEATHERMAP_API_KEY", "YOUR_API_KEY")

    # Set the city to monitor
    city = "Bangkok"

    # Display status message
    print(f"Fetching weather data for {city}...")
    print("-" * 40)

    # Step 1: Fetch weather data from API
    result = fetch_weather(city, api_key)

    # Step 2: Process result and check for errors
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        # Display weather information
        rainfall = result["rainfall_mm_per_hour"]
        print(f"City:              {result['city']}")
        print(f"Rainfall (mm/hr):  {rainfall}")
        print(f"Temperature (°C):  {result['temperature_celsius']}")
        print(f"Timestamp:         {result['timestamp']}")

        # Step 3: Check alert classification
        alert = check_alert(rainfall)
        print(f"Alert Level:       {alert['level']} ({alert['color']})")
        print(f"Message:           {alert['message']}")

        # Step 4: Log alert if needed (Yellow or Red only)
        log_alert(city, rainfall, alert["level"])


# Entry point: Run main function when script is executed directly
if __name__ == "__main__":
    main()
