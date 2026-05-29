# Software Development — Specialized Experiments
### Xi'an Jiaotong University · Phanpasorn Laor-iam · 3125999087 · 2026

---

Four water-related engineering experiments built end-to-end with AI-assisted software development.
Each project lives on its own branch and follows the same workflow: structured CoT prompting → AI-generated code → iterative refinement → physical validation → documented outputs.

---

## Repository Structure

```
software-development-class-2026/
│
├── project-1   ── Short-term Rainfall Forecasting & Alert System
├── project-2   ── SCS-CN Runoff Calculation
├── project-3   ── Reservoir Dispatch Optimization
└── project-4   ── Flood Inundation Analysis (DEM-based)
```

---

## Projects at a Glance

### Project 1 — Rainfall Forecasting & Alert System
`branch: project-1`

Real-time rainfall monitoring via the OpenWeatherMap API. Classifies rainfall into three severity levels (Normal / Watch / Heavy Rainfall ≥ 20 mm/h) and displays live conditions through a multi-city Streamlit dashboard with map visualization and 10-day forecast trend.

| | |
|---|---|
| **Python files** | `weather_monitor.py` · `weather_alert.py` · `weather_dashboard.py` |
| **Output files** | `alert_log.txt` |
| **Docs** | `prompt_log.md` · `report.tex` · `requirements.txt` · `README.md` |
| **Total files** | 8 (+ `screenshot/` folder) |
| **Dependencies** | `streamlit` · `requests` · `pandas` |

---

### Project 2 — SCS-CN Runoff Model
`branch: project-2`

Python implementation of the USDA Soil Conservation Service Curve Number method for estimating direct runoff from rainfall. Includes a full pytest boundary test suite (6 cases, all pass), CN sensitivity analysis across 6 land-cover types, and physical constraint validation.

| | |
|---|---|
| **Python files** | `scs_cn_runoff.py` · `test_runoff.py` · `sensitivity_analysis.py` · `validate_scs_cn.py` · `main.py` |
| **Output files** | `cn_sensitivity.png` · `rainfall_runoff_curves.png` |
| **Docs** | `prompt_log.md` · `report.tex` · `README.md` |
| **Total files** | 10 (+ `screenshot/` folder) |
| **Dependencies** | `numpy` · `matplotlib` · `scipy` · `pytest` |

---

### Project 3 — Reservoir Dispatch Optimization
`branch: project-3`

SLSQP-based 7-day hydropower dispatch optimization. Achieves **$91.52 total revenue** with all 6 physical constraints verified. Extended with Pareto trade-off analysis (revenue vs. ecological deficit), a Rolling Horizon MPC strategy (99.87% efficiency), and a water quality constraint comparison.

| | |
|---|---|
| **Python files** | `reservoir_optimization.py` · `tradeoff_analysis.py` · `rolling_horizon.py` · `water_quality.py` · `water_quality_optimization.py` · `validation.py` · `uncertainty_analysis.py` |
| **Output files** | `optimal_schedule.csv` · `validation_report.txt` · `tradeoff_analysis.png` · `rolling_horizon_comparison.png` · `rolling_horizon_comparison.csv` · `water_quality_analysis.png` · `uncertainty_analysis.png` |
| **Docs** | `prompt_log.md` · `prompt.md` · `report.tex` · `README.md` |
| **Total files** | 18 (+ `screenshot/` folder) |
| **Dependencies** | `numpy` · `scipy` · `matplotlib` · `pandas` |

---

### Project 4 — Flood Inundation Analysis (DEM-based)
`branch: project-4`

Five-part flood modelling pipeline: synthetic DEM generation → flood simulation → four-panel visualization → dynamic rising-water simulation (40–50 m) → 13-check physical validation suite (**13/13 pass**). Extensions include an animated GIF and multi-stage comparison figure.

| | |
|---|---|
| **Python files** | `dem_generator.py` · `flood_analysis.py` · `flood_visualization.py` · `rising_water_simulation.py` · `validation_suite.py` · `example_usage.py` |
| **Output files** | `dem_data.npy` · `flood_extent_40m.png` · `flood_extent_50m.png` · `flood_curve.png` · `flood_stages.png` · `flood_simulation.gif` · `validation_report.txt` |
| **Docs** | `prompt_log.md` · `prompt.md` · `report.tex` · `requirements.txt` · `run.sh` · `README.md` |
| **Total files** | 19 (+ `screenshot/` folder) |
| **Dependencies** | `numpy` · `scipy` · `matplotlib` · `imageio` |

---

## Dependencies Summary

| Project | Key Libraries |
|---|---|
| Project 1 | `streamlit` `requests` `pandas` |
| Project 2 | `numpy` `matplotlib` `scipy` `pytest` |
| Project 3 | `numpy` `scipy` `matplotlib` `pandas` |
| Project 4 | `numpy` `scipy` `matplotlib` `imageio` |

All projects use **Python 3.10+** and are self-contained within their own branch and virtual environment (`.venv/`).

---

## Clone & Switch

```bash
git clone https://github.com/phaixiaobai/software-development-class-2026.git
cd software-development-class-2026

git checkout project-1   # Rainfall Alert System
git checkout project-2   # SCS-CN Runoff Model
git checkout project-3   # Reservoir Dispatch
git checkout project-4   # Flood Inundation
```

Each branch contains a `README.md` with setup and run instructions specific to that project.

---

*Phanpasorn Laor-iam · 3125999087 · Xi'an Jiaotong University · Software Development · 2026*
