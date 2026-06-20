"""
Rainfall Monitor Dashboard
Professional Streamlit dashboard for real-time rainfall monitoring
with multi-city support, alerts, predictions, and map visualization
"""

import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import functions from weather_monitor module
from weather_monitor import get_weather_data, check_alert


# Page configuration
st.set_page_config(
    page_title="Rainfall Monitor",
    page_icon="🌧️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==================== HELPER FUNCTIONS ====================


def init_session_state():
    """Initialize session state for history and multi-city tracking."""
    if "history" not in st.session_state:
        st.session_state["history"] = []
    if "multi_city_data" not in st.session_state:
        st.session_state["multi_city_data"] = []
    if "last_settings" not in st.session_state:
        st.session_state["last_settings"] = {"city": "", "api_key": "", "cities": ""}


def add_to_history(rainfall: float):
    """Add rainfall reading to session history (max 10)."""
    entry = {"time": datetime.now().strftime("%H:%M:%S"), "rainfall": rainfall}
    st.session_state["history"].append(entry)
    if len(st.session_state["history"]) > 10:
        st.session_state["history"] = st.session_state["history"][-10:]


def get_multiple_cities_data(
    cities: List[str], api_key: str, yellow_threshold: float, red_threshold: float
) -> List[Dict]:
    """
    Fetch weather data for multiple cities.

    Args:
        cities: List of city names
        api_key: OpenWeatherMap API key

    Returns:
        List of dictionaries with city data and alert info
    """
    results = []

    for city in cities:
        city = city.strip()
        if not city:
            continue

        data = get_weather_data(city, api_key)

        if "error" in data:
            results.append(
                {
                    "city": city,
                    "rainfall": 0,
                    "temperature": 0,
                    "timestamp": "",
                    "alert": {
                        "level": "Unknown",
                        "color": "gray",
                        "message": data["error"],
                    },
                    "error": data["error"],
                }
            )
        else:
            alert = check_alert(
                data["rainfall_mm_per_hour"], yellow_threshold, red_threshold
            )
            results.append(
                {
                    "city": data["city"],
                    "rainfall": data["rainfall_mm_per_hour"],
                    "temperature": data["temperature_celsius"],
                    "timestamp": data["timestamp"],
                    "alert": alert,
                    "error": None,
                }
            )

    return results


def send_alert_notification(city: str, rainfall: float, level: str) -> Dict:
    """
    Send alert notification (email/SMS mock implementation).

    Args:
        city: City name
        rainfall: Rainfall in mm/h
        level: Alert level (Yellow/Red)

    Returns:
        Dictionary with status and message
    """
    # Only send for Yellow and Red alerts
    if level not in ("Yellow", "Red"):
        return {"status": "skipped", "message": "No notification needed"}

    # Mock notification (replace with real SMTP/SMS API in production)
    try:
        subject = f"Rainfall Alert - {city}"
        message = f"""
        🌧️ RAINFLARM ALERT
        
        City: {city}
        Rainfall: {rainfall} mm/h
        Level: {level}
        Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        
        Please take necessary precautions.
        """

        # In production, integrate with:
        # - Email: smtplib + email.mime
        # - SMS: Twilio, AWS SNS, etc.

        return {
            "status": "success",
            "message": f"Alert sent for {city} ({level})",
            "subject": subject,
            "body": message,
        }

    except Exception as e:
        return {"status": "error", "message": f"Failed to send notification: {str(e)}"}


def get_prediction(rainfall_data: List[float], days: int = 10) -> pd.DataFrame:
    """
    Predict future rainfall using moving average.

    Args:
        rainfall_data: List of historical rainfall readings
        days: Number of days to predict

    Returns:
        DataFrame with predicted rainfall
    """
    if not rainfall_data or len(rainfall_data) < 2:
        # Return placeholder if insufficient data
        dates = [
            (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
            for i in range(1, days + 1)
        ]
        return pd.DataFrame({"date": dates, "rainfall_mm": [0] * days})

    # Calculate moving average
    window = min(3, len(rainfall_data))
    avg_rainfall = sum(rainfall_data[-window:]) / window

    # Generate predictions with slight variation
    dates = [
        (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(1, days + 1)
    ]

    predictions = []
    base = avg_rainfall
    for i in range(days):
        # Add small variation (±20%)
        variation = base * 0.2 * (i % 3 - 1) * 0.5
        predictions.append(max(0, base + variation))

    return pd.DataFrame({"date": dates, "rainfall_mm": predictions})


def get_city_coordinates(city: str, api_key: str) -> Optional[tuple]:
    """Get city coordinates using geocoding API."""
    url = "https://api.openweathermap.org/geo/1.0/direct"
    params = {"q": city, "limit": 1, "appid": api_key}

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                return (data[0]["lat"], data[0]["lon"])
    except Exception:
        pass
    return None


def create_map(cities_data: List[Dict], api_key: str):
    """
    Create an enhanced Folium map with city markers colored by alert level.

    Args:
        cities_data: List of city data with alert info
        api_key: OpenWeatherMap API key

    Features:
        - Full-width responsive map (600px height)
        - Auto-centering based on all city coordinates
        - Color-coded markers and circle markers
        - Circle radius based on rainfall intensity
        - Rich popups with city info
        - Tooltips on hover
        - Legend explaining color codes
        - CartoDB positron tile style
    """
    try:
        import folium
        from streamlit_folium import st_folium
        from folium.plugins import MarkerCluster

        # Collect all valid coordinates
        valid_coords = []

        for data in cities_data:
            city = data["city"]
            coords = get_city_coordinates(city, api_key)
            if coords:
                valid_coords.append((city, coords, data))

        if not valid_coords:
            st.warning("📍 No city coordinates available for mapping")
            return

        # Calculate center based on all cities
        avg_lat = sum(c[1][0] for c in valid_coords) / len(valid_coords)
        avg_lon = sum(c[1][1] for c in valid_coords) / len(valid_coords)

        # Create map with clean tile style
        m = folium.Map(
            location=[avg_lat, avg_lon], zoom_start=5, tiles="CartoDB positron"
        )

        # Add marker cluster for better visualization
        marker_cluster = MarkerCluster().add_to(m)

        # Color and label mapping based on alert level
        color_map = {
            "Green": ("green", "✅ Normal"),
            "Yellow": ("orange", "⚠️ Moderate Warning"),
            "Red": ("red", "🚨 Heavy Rain Alert"),
        }

        # Add markers for each city
        for city, coords, data in valid_coords:
            lat, lon = coords
            level = data["alert"]["level"]
            rainfall = data["rainfall"]

            color, label = color_map.get(level, ("gray", "❓ Unknown"))

            # Create rich popup content
            popup_html = f"""
            <div style="font-family: Arial; min-width: 150px;">
                <h4 style="margin: 0; color: #333;">📍 {city}</h4>
                <hr style="margin: 5px 0;">
                <p><b>Rainfall:</b> {rainfall} mm/h</p>
                <p><b>Alert:</b> <span style="color: {color}; font-weight: bold;">{label}</span></p>
                <p><b>Temp:</b> {data.get("temperature", "N/A")} °C</p>
            </div>
            """

            # Add circle marker (radius based on rainfall intensity)
            # Scale: 1mm = 500m radius, min 3km, max 20km
            radius = min(20000, max(3000, rainfall * 500))

            folium.Circle(
                location=[lat, lon],
                radius=radius,
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.4,
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"{city} | {rainfall} mm/h | {level}",
            ).add_to(m)

            # Add icon marker on top
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=250),
                icon=folium.Icon(color=color, icon="cloud", prefix="fa"),
                tooltip=f"{city}: {rainfall} mm/h",
            ).add_to(marker_cluster)

        # Add a legend
        legend_html = """
        <div style="position: fixed; 
                    bottom: 50px; right: 50px; 
                    z-index: 1000; 
                    background-color: white; 
                    padding: 10px; 
                    border-radius: 5px;
                    border: 2px solid gray;
                    font-size: 12px;">
            <b>Legend</b><br>
            <i class="fa fa-circle" style="color: green;"></i> ✅ Normal<br>
            <i class="fa fa-circle" style="color: orange;"></i> ⚠️ Moderate<br>
            <i class="fa fa-circle" style="color: red;"></i> 🚨 Heavy Alert<br>
            <hr style="margin: 5px 0;">
            <small>Circle size = rainfall</small>
        </div>
        """
        m.get_root().html.add_child(folium.Element(legend_html))

        # Display map with full width and 600px height
        st_folium(m, width="100%", height=600)

    except ImportError:
        st.warning("📍 Map visualization requires: pip install folium streamlit-folium")
    except Exception as e:
        st.warning(f"Map unavailable: {str(e)}")


def get_forecast_data(city: str, api_key: str, days: int) -> pd.DataFrame:
    """
    Fetch forecast/predicted rainfall data.

    Args:
        city: City name
        api_key: OpenWeatherMap API key
        days: Number of days to predict

    Returns:
        DataFrame with date and rainfall_mm columns
    """
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"q": city, "appid": api_key, "units": "metric"}

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            return pd.DataFrame(columns=["date", "rainfall_mm"])

        data = response.json()
        rainfall_list = []

        for item in data.get("list", []):
            dt = datetime.fromtimestamp(item["dt"])
            rain = item.get("rain", {}).get("3h", 0)
            rainfall_list.append(
                {
                    "date": dt.strftime("%Y-%m-%d"),
                    "time": dt.strftime("%H:%M"),
                    "rainfall_mm": rain,
                }
            )

        if not rainfall_list:
            return pd.DataFrame(columns=["date", "rainfall_mm"])

        df = pd.DataFrame(rainfall_list)
        daily = df.groupby("date")["rainfall_mm"].sum().reset_index()
        daily = daily.head(days)

        return daily

    except Exception:
        return pd.DataFrame(columns=["date", "rainfall_mm"])


# ==================== MAIN APPLICATION ====================


def main():
    """Main dashboard application."""

    # Initialize session state
    init_session_state()

    # ==================== SIDEBAR ====================
    st.sidebar.title("⚙️ Settings")

    # Single city or multi-city input
    city_input = st.sidebar.text_area(
        "Cities (comma-separated)",
        value="Bangkok, Singapore, Jakarta",
        help="Enter cities separated by commas",
    )

    api_key = st.sidebar.text_input(
        "API Key",
        type="password",
        value="21a5b4a0ce4c7b101ca34bce8b4c6f86",
        help="Your OpenWeatherMap API key",
    )

    # Configurable alert thresholds
    st.sidebar.markdown("---")
    st.sidebar.caption("Alert thresholds (mm/h)")
    yellow_threshold = st.sidebar.number_input(
        "Yellow threshold (mm/h)", min_value=0.0, value=10.0, step=0.1
    )
    red_threshold = st.sidebar.number_input(
        "Red threshold (mm/h)", min_value=0.0, value=1.0, step=0.1
    )

    # Prediction days slider
    pred_days = st.sidebar.slider(
        "Prediction days",
        min_value=5,
        max_value=30,
        value=10,
        help="Number of days to predict",
    )

    # Notification toggle
    enable_notif = st.sidebar.toggle("Enable alert notifications", value=False)

    st.sidebar.markdown("---")

    # Action buttons
    fetch_button = st.sidebar.button("Fetch Data", type="primary")
    refresh_button = st.sidebar.button("🔄 Refresh")

    st.sidebar.markdown("---")
    st.sidebar.info("⏱️ Auto-refresh every 5 minutes")

    # ==================== PARSE CITIES ====================
    cities = [c.strip() for c in city_input.split(",") if c.strip()]
    main_city = cities[0] if cities else "Bangkok"

    # ==================== TOP SECTION ====================
    st.title(f"🌧️ Rainfall Monitor")
    st.caption(
        f"🕐 Auto-refresh enabled | Last updated: {datetime.now().strftime('%H:%M:%S')}"
    )
    st.divider()

    # ==================== FETCH DATA ====================
    should_fetch = (
        fetch_button
        or refresh_button
        or st.session_state["last_settings"]["city"] != city_input
        or st.session_state["last_settings"]["api_key"] != api_key
    )

    if should_fetch:
        st.session_state["last_settings"] = {
            "city": city_input,
            "api_key": api_key,
            "cities": city_input,
        }

        with st.spinner("Fetching weather data..."):
            multi_data = get_multiple_cities_data(cities, api_key, yellow_threshold, red_threshold)
            st.session_state["multi_city_data"] = multi_data

            # Add to history for main city
            if multi_data and "error" not in multi_data[0]:
                add_to_history(multi_data[0]["rainfall"])

                # Send notification if enabled and alert is Yellow/Red
                if enable_notif:
                    alert = multi_data[0]["alert"]
                    notif = send_alert_notification(
                        multi_data[0]["city"], multi_data[0]["rainfall"], alert["level"]
                    )
                    if notif["status"] == "success":
                        st.toast(f"📧 {notif['message']}")

    # ==================== MULTI-CITY TABLE ====================
    if st.session_state["multi_city_data"]:
        st.subheader("📊 Multi-City Overview")

        # Create DataFrame for display
        display_data = []
        highest_risk = None
        max_rainfall = -1

        for data in st.session_state["multi_city_data"]:
            display_data.append(
                {
                    "City": data["city"],
                    "Rainfall (mm/h)": data["rainfall"],
                    "Temp (°C)": data["temperature"],
                    "Alert": data["alert"]["level"],
                }
            )

            # Track highest risk
            if data["rainfall"] > max_rainfall:
                max_rainfall = data["rainfall"]
                highest_risk = data["city"]

        df_overview = pd.DataFrame(display_data)
        st.dataframe(df_overview, use_container_width=True, hide_index=True)

        if highest_risk:
            st.caption(f"⚠️ Highest risk: **{highest_risk}** ({max_rainfall} mm/h)")

        st.divider()

    # ==================== MAIN CITY METRICS ====================
    if st.session_state["multi_city_data"] and st.session_state["multi_city_data"][0]:
        data = st.session_state["multi_city_data"][0]
        rainfall = data["rainfall"]
        temperature = data["temperature"]
        alert = data["alert"]

        # 3-column metrics row
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("🌧️ Rainfall (mm/h)", f"{rainfall}")

        with col2:
            st.metric("🌡️ Temperature (°C)", f"{temperature}")

        with col3:
            st.metric("⚠️ Alert Level", alert["level"])

        st.divider()

        # ==================== MAIN CONTENT ====================
        col_left, col_right = st.columns([1, 2])

        with col_left:
            st.subheader("🚨 Alert Status")

            if alert["level"] == "Green":
                st.success("🟢 Normal\n\nNo alert - conditions are safe")
            elif alert["level"] == "Yellow":
                st.warning("🟡 Moderate Warning\n\nRain expected - take precautions")
            else:
                st.error("🔴 HEAVY RAIN ALERT\n\nDangerous conditions - stay alert!")

            st.divider()

            st.subheader("🗺️ Rainfall Map Overview")
            st.caption(
                "Interactive map showing all monitored cities with color-coded rainfall intensity"
            )

            # Full-width map container
            with st.container():
                if st.session_state["multi_city_data"]:
                    create_map(st.session_state["multi_city_data"], api_key)

        with col_right:
            st.subheader("📈 Real-Time Rainfall (Last 10 Readings)")

            if st.session_state["history"]:
                df_rt = pd.DataFrame(st.session_state["history"])
                st.line_chart(df_rt.set_index("time"))

                with st.expander("View Raw Data"):
                    st.dataframe(df_rt, use_container_width=True, hide_index=True)
            else:
                st.info("No readings yet. Click Fetch Data to start.")

        st.divider()

        # ==================== PREDICTION SECTION ====================
        st.subheader(f"📊 Predicted Rainfall (Next {pred_days} Days)")

        # Get forecast data
        forecast_data = get_forecast_data(main_city, api_key, pred_days)

        if forecast_data.empty:
            st.warning("⚠️ Forecast unavailable. Using prediction model.")
            # Use history for prediction
            history_rainfall = [h["rainfall"] for h in st.session_state["history"]]
            pred_data = get_prediction(history_rainfall, pred_days)
        else:
            pred_data = forecast_data

        # Plotly visualization
        try:
            import plotly.express as px

            fig = px.line(
                pred_data,
                x="date",
                y="rainfall_mm",
                markers=True,
                title=f"Predicted Daily Rainfall - {main_city}",
            )
            fig.update_layout(
                xaxis_title="Date", yaxis_title="Rainfall (mm)", hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("View Prediction Data"):
                st.dataframe(pred_data, use_container_width=True)

        except ImportError:
            st.line_chart(pred_data.set_index("date"))

    # ==================== AUTO REFRESH ====================
    st.markdown('<meta http-equiv="refresh" content="300">', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
