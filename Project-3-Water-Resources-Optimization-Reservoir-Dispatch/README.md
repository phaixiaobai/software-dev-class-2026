# 🏞️ Reservoir Dispatch Optimization
### Specialized Experiment 3 · Xi'an Jiaotong University · Software Development 2026

---

A constrained optimization model that schedules 7-day hydropower reservoir releases to **maximize electricity revenue** while meeting storage limits, ecological flow requirements, and physical mass balance. Extended with Pareto trade-off analysis, a rolling-horizon MPC strategy, and water quality constraints — all developed with AI-assisted prompting.

---

## Problem at a Glance

> *Given a 7-day forecast of inflows and electricity prices, decide how much water to release each day to earn the most revenue without violating any physical or environmental constraint.*

```
Objective    maximize  Σ η · g · H · Qₜ · πₜ · Δt / 3,600,000

Constraints  Vₜ₊₁ = Vₜ + (Qᵢₙₜ − Qₜ) · Δt    mass balance
             100,000 ≤ Vₜ ≤ 1,000,000  m³        storage
                  10 ≤ Qₜ ≤ 100  m³/s            release
```

Solved with `scipy.optimize.minimize` (SLSQP).

---

## Results

**Optimal revenue: $91.52** over 7 days — strategy holds water through low-price days 1–5,
then releases aggressively on Day 6 ($0.12/kWh peak price).

### Validation — 6/6 PASS

```
✅  Storage lower bound    min 100,000 m³ maintained
✅  Storage upper bound    max 1,000,000 m³ not exceeded
✅  Ecological release     all Qₜ ≥ 10 m³/s
✅  Maximum release        all Qₜ ≤ 100 m³/s
✅  Mass balance           error < ±1,000 m³/day (SLSQP tolerance)
✅  Revenue calculation    all daily values match (< 0.1% error)
```

### Extensions

| Extension | Result |
|---|---|
| Pareto trade-off (revenue vs. eco deficit) | Zero deficit costs only **$0.40** (0.4% of max revenue) |
| Rolling Horizon MPC (3-day window) | **99.87% efficiency** vs full-horizon optimal |
| Water quality constraint | Hard constraint forces high dilution releases; soft penalty finds a middle ground |

---

## Project Files

```
├── reservoir_optimization.py      SLSQP optimizer → optimal_schedule.csv
├── tradeoff_analysis.py           Pareto frontier (w = 0.0 to 1.0)
├── rolling_horizon.py             MPC with 3-day lookahead
├── water_quality.py               3-scenario pollutant concentration analysis
├── validation.py                  6-check constraint verifier
├── uncertainty_analysis.py        Monte Carlo over inflow variability
├── optimal_schedule.csv           7-day release, storage, and revenue table
├── validation_report.txt          6/6 PASS — Revenue $91.52
├── tradeoff_analysis.png          Pareto frontier plot
├── rolling_horizon_comparison.png full vs. rolling horizon bar chart
├── water_quality_analysis.png     3-scenario comparison
├── prompt_log.md                  all AI prompts and responses, in order
└── report.tex                     Overleaf experiment write-up
```

---

## Run It

```bash
git clone https://github.com/phaixiaobai/software-development-class-2026.git
cd software-development-class-2026 && git checkout project-3

pip install numpy scipy matplotlib pandas

python reservoir_optimization.py   # main solve
python tradeoff_analysis.py        # Pareto frontier
python rolling_horizon.py          # MPC comparison
python validation.py               # verify solution
```

---

*Phanpasorn Laor-iam · 3125999087 · Xi'an Jiaotong University · 2026*
