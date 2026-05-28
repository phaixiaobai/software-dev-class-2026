# Rainfall Forecasting & Alert System
### Specialized Experiment 1 · Xi'an Jiaotong University · Software Development 2026

---

A real-time weather monitoring pipeline built end-to-end with AI-assisted development.
The system pulls live data from **OpenWeatherMap**, classifies rainfall severity, writes alert logs, and surfaces everything in a **Streamlit** dashboard — rebuilt through three rounds of CoT-prompted iteration.

---

## How It Works

```
OpenWeatherMap API
       │
       ▼
 weather_monitor.py        ← fetch rainfall, temp, timestamp for any city
       │
       ▼
  weather_alert.py         ← classify intensity → GREEN / YELLOW / RED
       │
       ▼
 weather_dashboard.py      ← render live dashboard + map + 10-day forecast
       │
       ▼
    alert_log.txt          ← persist every triggered alert
```

---

## Rainfall Classification

| | Intensity | Meaning |
|---|---|---|
| 🟢 Normal | < 10 mm/h | No action needed |
| 🟡 Watch | 10 – 19 mm/h | Elevated monitoring |
| 🔴 Alert | ≥ 20 mm/h | Heavy rainfall — flood risk |

---

## Stack

| Layer | Tool |
|---|---|
| Language | Python 3.10+ |
| Dashboard | Streamlit |
| Weather data | OpenWeatherMap REST API |
| HTTP | Requests |
| Data handling | Pandas |

---

## Files

```
├── weather_monitor.py     fetch + parse API response
├── weather_alert.py       threshold logic + alert classification
├── weather_dashboard.py   full Streamlit app (multi-city, map, forecast)
├── alert_log.txt          timestamped alert history
├── prompt_log.md          every AI prompt and agent response, in order
├── requirements.txt       pip dependencies
└── report.tex             experiment write-up (Overleaf)
```

---

## Quickstart

```bash
# 1 — get the branch
git clone https://github.com/phaixiaobai/software-development-class-2026.git
git checkout project-1

# 2 — install
pip install -r requirements.txt

# 3 — launch dashboard (enter your OpenWeatherMap key when prompted)
streamlit run weather_dashboard.py
```

Get a free API key → https://home.openweathermap.org/api_keys

---

## Development Approach

This project was built across **3 AI-assisted prompting stages**, each documented in `prompt_log.md`:

1. **API layer** — fetch real-time rainfall data for any city
2. **Alert engine** — classify intensity with edge-case handling
3. **Dashboard** — three rounds of refinement: base UI → improved interface → multi-city + map extension

---

*Phanpasorn Laor-iam · 3125999087 · Xi'an Jiaotong University · 2026*
