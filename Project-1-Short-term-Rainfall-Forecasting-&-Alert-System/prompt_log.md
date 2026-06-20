# Prompt Log - Rainfall Monitoring Project

## 1. Introduction

This document provides a comprehensive record of all AI interactions during the development of a rainfall monitoring system. The project demonstrates AI-assisted software development using the OpenWeatherMap API to fetch real-time weather data, classify rainfall intensity, and visualize results through an interactive Streamlit dashboard.

The log is structured chronologically, documenting each prompt sent to the AI assistant, the generated outputs, and verification results.

---

## 2. Prompt History

### Prompt 1: Initial Weather Data Fetch

**User Prompt:**
You are a Python developer with experience in hydrology and API integration.

I am a water resources student building a rainfall monitoring system.
Write a clean, well-structured Python script to fetch current weather data from the OpenWeatherMap API.

Requirements:

1. Use the requests library to call:
   https://api.openweathermap.org/data/2.5/weather

2. Create a function:
   get_weather_data(city: str, api_key: str) -> dict

3. The function must:
   - Send a GET request with parameters: city, api_key, and units=metric
   - Parse the JSON response safely
   - Extract:
        - Rainfall intensity from rain["1h"] (return 0 if not present)
        - Temperature from main["temp"]
        - Timestamp (convert to readable format if possible)

4. Error Handling:
   - Handle HTTP 401 (invalid API key)
   - Handle HTTP 404 (city not found)
   - Handle network/connection errors
   - Return meaningful error messages instead of crashing

5. Output Format:
   Return a dictionary:
   {
       "city": str,
       "rainfall_mm_per_hour": float,
       "temperature_celsius": float,
       "timestamp": str
   }

6. Code Quality:
   - Add clear comments explaining each step
   - Use try-except blocks properly
   - Keep the code beginner-friendly but professional

7. Example Usage:
   - Show how to call the function
   - Use a placeholder API key like "YOUR_API_KEY"
   - Print the result clearly

Optional (if possible):
- Use environment variables for API key (os.getenv)
- Format output nicely

Output:
- Provide full Python script
- Ensure it runs independently

**Purpose:** Create initial weather data fetching functionality with API integration and error handling.

---

### Prompt 2: Alert Module Extension

**User Prompt:**
You are a Python developer working on a rainfall monitoring system.

I already have a script that fetches rainfall data. Extend the system by adding a threshold-based alert module.

Implement the following features:

1. Alert Classification Function

Create a function:
check_alert(rainfall: float) -> dict

Logic:
- Green: rainfall < 10 mm/h → "Normal"
- Yellow: 10 ≤ rainfall < 20 mm/h → "Moderate Warning"
- Red: rainfall ≥ 20 mm/h → "HEAVY RAIN ALERT"

Return format:
{
    "level": "Green/Yellow/Red",
    "color": "green/yellow/red",
    "message": "descriptive alert message"
}

Requirements:
- Handle edge cases (e.g., negative rainfall, None values)
- Keep logic clear and readable
- Include a proper docstring explaining inputs, outputs, and logic

2. Alert Logging Function

Create a function:
log_alert(city: str, rainfall: float, level: str) -> None

Requirements:
- Write alerts to a file named "alert_log.txt"
- Format each log entry as:
  [YYYY-MM-DD HH:MM:SS] | City: {city} | Rainfall: {rainfall} mm/h | Level: {level}
- Only log alerts when level is "Yellow" or "Red"
- Append to file (do not overwrite existing logs)
- Handle file errors safely (use try-except)

3. Integration

- Show how to integrate both functions into the existing workflow
- Example:
    rainfall_data = get_weather_data(...)
    alert = check_alert(rainfall_data["rainfall_mm_per_hour"])
    log_alert(city, rainfall, alert["level"])

4. Code Quality

- Add clear docstrings for both functions
- Use clean and readable Python code
- Include comments where necessary
- Ensure the code is beginner-friendly but follows good practices

Output:
- Provide only the new functions and example integration code
- Do not rewrite the entire existing system

**Purpose:** Add alert classification and logging functionality to the existing system.

---

### Prompt 3: Streamlit Dashboard Creation

**User Prompt:**
You are a Python developer with experience in Streamlit and data visualization.

I have an existing rainfall monitoring system with these functions:
- fetch_weather(city, api_key) → returns rainfall, temperature, timestamp, or error
- check_alert(rainfall) → returns {level, color, message}

Create a new file named "weather_dashboard.py" that builds a Streamlit dashboard with the following features:

1. Page Setup
- Title: "Rainfall Monitor - {city_name}" (dynamic based on user input)
- Use st.set_page_config for a clean layout

2. Sidebar Controls
- Text input for city name
- Text input for API key (masked)
- "Fetch Data" button
- Optional: Manual refresh button

3. Main Display Area
- Show a large metric:
    st.metric(label="Current Rainfall (mm/h)", value=rainfall)
- Display alert status:
    - Green → st.success(message)
    - Yellow → st.warning(message)
    - Red → st.error(message)
- Show last updated timestamp clearly

4. Auto Refresh
- Use st_autorefresh (from streamlit-autorefresh) OR implement manual refresh logic
- Refresh interval: 5 minutes (300,000 ms)

5. Rainfall History Visualization
- Store last 10 rainfall readings using st.session_state
- Structure:
    st.session_state["history"] = [{"time": ..., "rainfall": ...}, ...]
- Plot a line chart using:
    st.line_chart or matplotlib

6. Error Handling
- If fetch_weather returns an error:
    → Display st.error(error_message)
    → Do not crash the app

7. Integration
- Import and use:
    from your_module import fetch_weather, check_alert
- Example flow:
    data = fetch_weather(city, api_key)
    alert = check_alert(data["rainfall_mm_per_hour"])

8. Code Quality
- Include clear comments
- Keep code modular and readable
- Ensure it runs as a standalone Streamlit app:
    streamlit run weather_dashboard.py

Output Requirements:
- Provide the full Python script for "weather_dashboard.py"
- Do not include explanations outside the code
- Ensure compatibility with beginner-level setup

**Purpose:** Create Streamlit dashboard for visual rainfall monitoring.

---

### Prompt 4: Map Visualization Improvement

**User Prompt:**
You are a Python developer experienced in Streamlit and geospatial visualization using Folium.

Improve the map visualization in my rainfall monitoring dashboard.

Current issue:
- The map is too small and not easy to read

Enhance the map UI with the following requirements:

1. Expand Map Size

- Increase map width to full container width
- Increase height to at least 500–700 pixels
Use:
    st_folium(map, width=..., height=...)

2. Better Map Layout

- Place the map in a dedicated section:
    "🗺️ City Rainfall Map"

- Use full-width layout:
    st.container() or st.columns([1]) to span entire page

3. Improve Map Centering

- Automatically center the map based on all city coordinates
- If multiple cities:
    → Calculate average latitude and longitude

4. Marker Improvements

- Use color-coded markers based on alert level:
    - Green → Normal
    - Yellow → Moderate Warning
    - Red → Heavy Rain Alert

- Add popups with:
    - City name
    - Rainfall (mm/h)
    - Alert level

5. Add Marker Clustering (Optional but recommended)

- Use:
    from folium.plugins import MarkerCluster
- Group markers for better visualization

6. Improve Map Style

- Use a clean tile style:
    tiles="CartoDB positron" OR "OpenStreetMap"

7. Code Quality

- Wrap map creation in a function:
    create_map(city_data_list)
- Keep code modular and readable

Output Requirements:
- Provide only the updated map-related code
- Clearly indicate where to insert it in the Streamlit app
- Ensure compatibility with streamlit-folium

**Purpose:** Enhance Folium map size, layout, and marker visualization.

---

### Prompt 5: Additional Map Improvements

**User Prompt:**
You are a Python developer experienced in Streamlit and geospatial visualization using Folium.

I have a rainfall monitoring dashboard with a city map using Folium. Improve and expand the map window with the following requirements:

1. Expand Map Display

- Make the map take full width of the page
- Increase height to at least 500–700 pixels
- Use:
    st_folium(map, width="100%", height=600)

2. Improve Map Layout

- Place the map in its own section:
    "🗺️ Rainfall Map Overview"

- Ensure it is visually separated using:
    st.divider()

3. Multi-City Visualization

- Display multiple cities on the map
- Each city should have a marker with:
    - City name
    - Rainfall (mm/h)
    - Alert level

4. Color-Coded Markers

- Green → Normal
- Yellow → Moderate Warning
- Red → Heavy Rain Alert

Use folium.Icon(color=...)

5. Centering & Zoom

- Automatically center the map based on all city coordinates
- Adjust zoom level dynamically so all markers are visible

6. Popup Information

Each marker should show:
- City name
- Rainfall value
- Alert message

Example:
"Bangkok | 12 mm/h | Moderate Warning"

7. Optional Enhancements (if possible)

- Add circle markers (radius based on rainfall intensity)
- Add tooltip on hover
- Add legend explaining color codes

8. Code Quality

- Keep code modular (create_map(data))
- Add comments explaining logic
- Ensure compatibility with streamlit-folium

Output Requirements:
- Provide only the updated map-related code
- Do not rewrite the entire dashboard

**Purpose:** Further improve map with circle markers, tooltips, and enhanced layout.

---

### Prompt 6: Generate Deliverables

**User Prompt:**
You are a Python developer and technical documentation assistant.

Help me generate the required deliverables for my rainfall monitoring system project.

I need the following three files:

1. weather_monitor.py (Main Application)

Requirements:
- Python script that:
    - Fetches rainfall data from OpenWeather API
    - Uses function: fetch_weather(city, api_key)
    - Uses function: check_alert(rainfall)
    - Displays rainfall, temperature, and alert level
    - Calls log_alert(city, rainfall, level)

- Include:
    - Clear function structure
    - Error handling (API errors, missing data)
    - Comments explaining each step

2. alert_log.txt (Log File)

Requirements:
- Simulate or generate sample log entries
- Format:
    [YYYY-MM-DD HH:MM:SS] | City: {city} | Rainfall: {x} mm/h | Level: {level}

- Include:
    - At least 5–10 entries
    - Only Yellow and Red alerts

3. prompt_log.md (AI Interaction Documentation)

Requirements:
- Markdown format
- Include sections:
    - Prompts used (Direct + CoT)
    - Summary of AI outputs
    - Comparison (Direct vs CoT)
    - Verification results
    - Lessons learned

- Write in formal academic tone
- Keep it clear and structured

Output Requirements:
- Provide all three files clearly separated
- Use proper formatting:
    - Python code block for .py file
    - Plain text for .txt
    - Markdown for .md
- Ensure everything is ready to submit

**Purpose:** Generate final project deliverables with documentation.

---

### Prompt 7: Update Prompt Log Documentation

**User Prompt:**
You are a technical documentation assistant helping a university student record their AI-assisted workflow.

Create a file named "prompt_log.md" that documents all AI interactions for a rainfall monitoring system project.

Requirements:

1. Structure

Use clean Markdown format with the following sections:

# Prompt Log - Rainfall Monitoring Project

## 1. Introduction
- Briefly explain the purpose of the log
- Mention that it documents AI-assisted development

## 2. Prompt History (IMPORTANT)
- List ALL user prompts used during the project
- Each prompt should include:
    - Title (e.g., "Initial Data Fetch Prompt")
    - The FULL original prompt (do not summarize)
    - Optional: brief purpose of the prompt

**Purpose:** Create comprehensive prompt log documentation with full original prompts.

---

## 3. AI Outputs Summary

### Output 1: Weather Monitoring System (Prompt 1)
The AI generated a complete `weather_monitor.py` file with:
- `get_weather_data()` function for API fetching
- Proper error handling (401, 404, network errors)
- JSON parsing for rainfall extraction
- Clean docstrings and comments

### Output 2: Alert Module Extension (Prompt 2)
The AI added to the existing file:
- `check_alert()` with three-level classification (Green/Yellow/Red)
- `log_alert()` for file logging
- Edge case handling (None, negative values)
- Proper integration with existing workflow

### Output 3: Streamlit Dashboard (Prompt 3)
The AI created `weather_dashboard.py` with:
- Dynamic page title
- Sidebar controls (city, API key, buttons)
- Metrics display with `st.metric`
- Alert visualization (success/warning/error)
- Session state for history tracking
- Error handling

### Output 4: Map Visualization v1 (Prompt 4)
The AI enhanced the map function with:
- Full-width display (600px height)
- Auto-centering on city coordinates
- Color-coded markers
- Marker clustering
- CartoDB positron tile style

### Output 5: Map Visualization v2 (Prompt 5)
The AI further improved with:
- Circle markers (radius based on rainfall)
- Rich popup information
- Tooltips on hover
- Enhanced legend

### Output 6: Project Deliverables (Prompt 6)
The AI generated all three required files:
- Updated `weather_monitor.py`
- Sample `alert_log.txt` (10 entries)
- Initial `prompt_log.md`

---

## 4. Verification Results

### Syntax Verification
All Python files passed syntax validation:
```bash
python -m py_compile weather_monitor.py  # Syntax OK
```

### Function Testing
```python
# Test check_alert function
check_alert(0)   # -> Green
check_alert(5)   # -> Green
check_alert(10)  # -> Yellow
check_alert(15)  # -> Yellow
check_alert(20)  # -> Red
check_alert(25)  # -> Red
check_alert(None) # -> Green (edge case)
check_alert(-5)  # -> Green (edge case)
```

### API Testing
Live API calls verified with valid API key:
```
City: Bangkok
Rainfall (mm/hr): 0.0
Temperature (°C): 36.46
```

---

## 5. Comparison: Direct vs CoT Prompting

### Direct Prompting Approach Used

**Characteristics:**
- Clear, enumerated requirements
- Specific function signatures required
- Explicit output format specifications

**Results:**
- Generated exact code structure requested
- Minimal clarification needed
- Fast implementation

### Observations

| Aspect | Direct Prompting |
|--------|-----------------|
| Requirements clarity | Explicit |
| Code accuracy | High |
| Flexibility | Low (requires comprehensive specs) |
| Iterations needed | Multiple (refinement) |

The Direct prompting approach proved effective because:
1. Requirements were clearly specified in advance
2. Function signatures were explicitly required
3. Output formats were well-defined

---

## 6. Lessons Learned

### Technical Lessons
1. **API Dependencies:** Free tier has rate limits; always verify API key
2. **Edge Cases:** Better to specify edge case handling explicitly
3. **Visualization:** Streamlit-Folium requires specific library installation

### Process Lessons
1. **Clear Requirements:** Specifying function signatures upfront yields accurate code
2. **Iterative Development:** Breaking into multiple prompts improves results
3. **Documentation:** Maintaining prompt log aids in understanding the development process

### Code Quality Lessons
1. **Modular Functions:** Separating fetch/check/log improves maintainability
2. **Error Handling:** Try-except blocks should cover all potential failures
3. **Comments:** Docstrings benefit future maintenance

---

## 7. File Summary

| File | Purpose | Status |
|------|----------|--------|
| weather_monitor.py | Core API and alert functions | Complete |
| weather_dashboard.py | Streamlit visualization | Complete |
| alert_log.txt | Sample log entries (10) | Complete |
| prompt_log.md | This documentation | Complete |

---

*Documentation generated: April 2026*
*Project: Rainfall Monitoring System*
*Course: Software Development Assignment*
*Institution: Xian-Jiaotong University*