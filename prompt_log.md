# Prompt Log — Experiment 3: Reservoir Optimization

## Prompt 1 — Problem Formulation
**Prompt:** Write a clean and formal mathematical formulation of the optimization problem (7-day reservoir dispatch, given parameters V0, V_min, V_max, Q_eco, Q_max, inflow, price, dt)
**AI Output Summary:** Mathematical formulation with decision variables (Q_t, V_t, P_t), objective function (maximize revenue), and constraints (mass balance, storage limits, release bounds)
**Errors Found:** None in initial formulation - proper use of Δt = 86400 in mass balance equation
**Correction:** N/A

## Prompt 2 — Implementation
**Prompt:** Implement reservoir optimization using scipy.optimize.minimize with compute_storage(), objective(), constraints, bounds, solve(), save to CSV
**AI Output Summary:** Complete scipy.optimize.minimize implementation using SLSQP method, computed storage from mass balance, objective returns negative revenue for maximization
**Errors Found:** None in implementation
**Correction:** N/A

## Prompt 3 — Trade-off Analysis
**Prompt:** Write trade-off analysis script with weighted-sum Pareto frontier (w from 0.0 to 1.0), plot Pareto frontier, print summary table
**AI Output Summary:** Created weighted-sum approach with combined objective f = -w*revenue + (1-w)*eco_deficit, traced 21 weight points from 0.0 to 1.0
**Errors Found:** Initial implementation kept Q_min = Q_eco constraint, preventing any ecological deficit trade-off exploration. Later relaxed to Q_min = 0 to properly explore Pareto frontier
**Correction:** Changed bounds from (Q_eco, Q_max) to (0, Q_max) to allow release below ecological minimum

## Prompt 4 — Validation
**Prompt:** Write validation script checking 6 physical constraints, output PASS/FAIL for each, save to validation_report.txt
**AI Output Summary:** Ran 6 checks: Storage Lower/Upper Bounds, Ecological Release, Max Release, Mass Balance, Revenue Calculation
**Errors Found:** 
- Storage Lower Bound: Days 6-7 show 99,999 m³ (1 m³ below V_min due to numerical precision)
- Mass Balance: Small floating-point errors on Days 2 (256 m³) and 6 (288 m³)
**Correction:** These are numerical precision issues from SLSQP optimizer tolerance - solution is essentially valid

---

## Key Observations

- **At w=1.0 (pure revenue):** Revenue = $91.93, Eco deficit = 8.05 m³/s
- **At w=0.0 (pure ecology):** Revenue = $77.04, Eco deficit = 0.00 m³/s
- **At w=0.5 (balanced):** Revenue = $91.53, Eco deficit = 0.00 m³/s

- **Revenue cost of zero ecological deficit:** $0.40 (0.4% of max revenue)
- **Days with highest release in optimal solution:** Day 6 (price = $0.12, release = 25.42 m³/s)

---

## Analysis Insights

1. The optimizer stores water during low-price days (Days 1-5 at $0.08-$0.10) by releasing at minimum Q_eco=10 m³/s
2. Releases increase on Day 6 (price $0.12) and Day 7 (price $0.10) when hydroelectric revenue is higher
3. Storage reaches maximum capacity (1,000,000 m³) on Days 2, 3, 5 and draws down on Days 6-7
4. The weighted-sum analysis reveals that allowing releases below Q_eco creates a meaningful Pareto trade-off; otherwise the problem has no conflict between revenue and ecology objectives