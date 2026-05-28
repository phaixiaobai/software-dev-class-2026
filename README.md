# Reservoir Dispatch Optimizer
### Specialized Experiment 3 · Xi'an Jiaotong University · Software Development 2026

---

A constrained hydropower optimization model that answers one question: **given 7 days of inflow forecasts and electricity prices, when should the reservoir release water to maximize revenue?**

Solved with `scipy` SLSQP, extended with Pareto trade-off analysis, a rolling-horizon MPC strategy, and water quality constraints — all built through AI-assisted CoT prompting.

---

## Optimization Problem

```
Decision variables:   Q₁, Q₂, ..., Q₇   (daily release, m³/s)

Maximize:   Σ  η · g · H · Qₜ · πₜ · Δt / 3,600,000   (total revenue, USD)

Subject to:
  Vₜ₊₁ = Vₜ + (Qᵢₙ,ₜ − Qₜ) · Δt       mass balance
  100,000 ≤ Vₜ ≤ 1,000,000  m³            storage bounds
       10 ≤ Qₜ ≤ 100  m³/s               release bounds
  V₀ = 500,000  m³                         initial condition
```

Parameters: η = 0.85, H = 50 m, g = 9.81 m/s², Δt = 86,400 s/day

---

## Results

**Optimal strategy → Total revenue: $91.52**
Release minimum ecological flow (10 m³/s) on low-price days 1–5, ramp up aggressively on Day 6 when price peaks at $0.12/kWh.

### Validation — 6/6 PASS

```
✅  Storage lower bound  — min 100,000 m³ on Day 6
✅  Storage upper bound  — max 1,000,000 m³ on Day 2
✅  Ecological release   — all Qₜ ≥ 10 m³/s
✅  Maximum release      — all Qₜ ≤ 100 m³/s
✅  Mass balance         — all days within ±1,000 m³
✅  Revenue calculation  — max error < 0.1%
```

### Pareto Trade-off (Revenue vs. Ecological Deficit)

| Weight w | Revenue | Eco Deficit | Notes |
|---|---|---|---|
| 0.0 | $77.04 | 0 m³/s | Pure ecology |
| 0.5 | $91.53 | 0 m³/s | Balanced |
| 1.0 | $91.93 | 8.05 m³/s | Pure revenue |

> Achieving zero ecological deficit costs only **$0.40 (0.4%)** of maximum revenue.

### Rolling Horizon (MPC, 3-day window)

| Method | Revenue | vs. Optimal |
|---|---|---|
| Full horizon (perfect foresight) | $88.12 | baseline |
| Rolling horizon (3-day lookahead) | $88.00 | −0.13% |

Near-optimal performance with only a 3-day forecast horizon.

---

## File Overview

```
├── reservoir_optimization.py      main SLSQP optimizer → optimal_schedule.csv
├── tradeoff_analysis.py           weighted-sum Pareto frontier
├── rolling_horizon.py             MPC rolling horizon (3-day window)
├── water_quality.py               pollutant concentration constraint
├── water_quality_optimization.py  3-scenario comparison (baseline / hard / soft)
├── validation.py                  6-check physical constraint suite
├── uncertainty_analysis.py        Monte Carlo inflow uncertainty
├── optimal_schedule.csv           7-day release & storage schedule
├── validation_report.txt          6/6 PASS, Revenue $91.52
├── tradeoff_analysis.png          Pareto frontier plot
├── rolling_horizon_comparison.png full vs. rolling horizon comparison
├── water_quality_analysis.png     3-scenario water quality plot
├── uncertainty_analysis.png       Monte Carlo output
├── prompt_log.md                  all AI prompts + agent responses
└── report.tex                     experiment write-up (Overleaf)
```

---

## Run It

```bash
git clone https://github.com/phaixiaobai/software-development-class-2026.git
git checkout project-3

pip install numpy scipy matplotlib pandas

python reservoir_optimization.py   # solve → optimal_schedule.csv
python tradeoff_analysis.py        # Pareto frontier
python rolling_horizon.py          # MPC comparison
python water_quality.py            # water quality extension
python validation.py               # verify solution
```

---

*Phanpasorn Laor-iam · 3125999087 · Xi'an Jiaotong University · 2026*
