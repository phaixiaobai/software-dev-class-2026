# 🌧️ Rainfall Forecasting & Alert System
### Specialized Experiment 1 · Xi'an Jiaotong University · Software Development 2026

---

Real-time rainfall monitoring powered by the **OpenWeatherMap API** and **Streamlit**.
Fetches live weather data, classifies rainfall intensity into three severity levels, logs every alert event, and renders it all in a multi-city interactive dashboard — built end-to-end with AI-assisted prompting.

---

## Alert Classification

| Severity | Threshold | Indicator |
|---|---|---|
| Normal | < 10 mm/h | 🟢 No action |
| Watch | 10 – 19 mm/h | 🟡 Elevated monitoring |
| Heavy Rainfall | ≥ 20 mm/h | 🔴 Flood risk alert |

---

## What's Inside

| File | Role |
|---|---|
| `weather_monitor.py` | Fetches `rainfall_mm/h`, `temperature`, `timestamp` from OWM API |
| `weather_alert.py` | Threshold logic — returns severity level + writes to `alert_log.txt` |
| `weather_dashboard.py` | Streamlit app: multi-city selector, live map, 10-day forecast chart |
| `alert_log.txt` | Timestamped history of every triggered alert |
| `prompt_log.md` | Complete record of every AI prompt and agent response |
| `requirements.txt` | `streamlit`, `requests`, `pandas` |
| `report.tex` | Overleaf-ready experiment write-up |

---

## Run It

```bash
# clone & switch branch
git clone https://github.com/phaixiaobai/software-development-class-2026.git
cd software-development-class-2026 && git checkout project-1

# install
pip install -r requirements.txt

# launch  (you'll need a free OWM key → openweathermap.org/api_keys)
streamlit run weather_dashboard.py
```

---

## Development Notes

Built across **3 AI-assisted prompt iterations**, each logged in `prompt_log.md`:

- **Round 1** — API integration: city lookup, JSON parsing, error handling
- **Round 2** — Alert engine: threshold classification with edge cases
- **Round 3** — Dashboard: 3 successive refinements — base layout → UI polish → multi-city + map extension

---

*Phanpasorn Laor-iam · 3125999087 · Xi'an Jiaotong University · 2026*
