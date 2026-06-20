# Prompt Log - Hydrology Software Development

This file contains all prompts used in developing the SCS-CN hydrology project.

---

## Prompt 1 — Formula Implementation

**Prompt used:**
> Write clean, well-structured Python code that implements the following:
>
> ## Main Function
> Function: calculate_runoff(P: float, CN: float) -> float
>
> Steps:
> 1. Calculate potential maximum retention: S = (25400 / CN) - 254
> 2. Calculate initial abstraction: Ia = 0.2 * S
> 3. Apply runoff condition:
>    - If P <= Ia: Q = 0
>    - Otherwise: Q = (P - Ia)^2 / (P - Ia + S)
> 4. Final validation: Ensure Q ≤ P (cap Q if necessary)
>
> ## Helper Functions
> Create: calculate_S(CN: float) -> float, calculate_Ia(S: float) -> float
>
> Requirements: Type hints, validation (CN 1-100, P ≥ 0), docstrings, test example P=50mm, CN=80 → Q≈13.8mm

**Result:** Created `scs_cn_runoff.py` with three functions:
- `calculate_S(CN)`: calculates potential retention
- `calculate_Ia(S)`: calculates initial abstraction
- `calculate_runoff(P, CN)`: main runoff calculation

**Verification:** P=50mm, CN=80 → Q = 13.80 mm ✓

---

## Prompt 2 — Pytest Test Suite

**Prompt:**
> Write a complete pytest test suite for calculate_runoff(P: float, CN: float) -> float
>
> Test Cases:
> | Test Case | P (mm) | CN | Expected Q |
> | Zero rainfall | 0 | 80 | 0 |
> | Below Ia | 5 | 80 | 0 |
> | Exactly at Ia | 12.7 | 80 | 0 |
> | Normal case | 50 | 80 | ≈ 13.8 mm |
> | High CN | 50 | 95 | > 13.8 mm |
> | Max CN (impervious) | 50 | 100 | Q close to P |
> | Q never exceeds P | 100 | 90 | Q <= 100 |
>
> Requirements: Use @pytest.mark.parametrize, floating point comparison with pytest.approx, monotonicity test, docstrings

**Result:** Created `test_runoff.py` with 11 tests using pytest.

**Status:** All 11 tests passed ✓

---

## Prompt 3 — Sensitivity Analysis

**Prompt:**
> Write a complete Python script to perform sensitivity analysis and visualization using the SCS-CN method.
>
> ## Script 1 — CN Sensitivity Analysis
> - Fix P = 50 mm, CN = [60, 70, 80, 90, 95, 100]
> - Print summary table with CN, Q (mm), Runoff Ratio (%)
> - Create combined bar + line chart with color gradient green→red
> - Save as cn_sensitivity.png
>
> ## Script 2 — Rainfall vs Runoff Curves
> - P = 0 to 100 mm (step 1), CN = [60, 70, 80, 90, 100]
> - Plot multiple curves with distinct colors
> - Add diagonal dashed line Q = P, shade area between Q=P and CN=60
> - Save as rainfall_runoff_curves.png

**Result:** Created `sensitivity_analysis.py` generating two visualizations.

**Outputs:**
- `cn_sensitivity.png` (78.9 KB)
- `rainfall_runoff_curves.png` (134.8 KB)

---

## Prompt 4 — Model Validation

**Prompt:**
> Write a Python script to validate the SCS-CN implementation with 6 checks:
> 1. Zero rainfall: P=0 → Q=0 for CN=[60,70,80,90,100]
> 2. Below Ia: P < Ia → Q=0
> 3. Physical constraint: Q ≤ P for 1000 random samples (seed=42)
> 4. Monotonicity: Q increases as CN increases (60-100)
> 5. Known reference: P=50, CN=80 → Q between 13.5-14.1
> 6. Impervious: CN=100, P=[100,150,200] → Q within 1mm of P

**Result:** Created `validate_scs_cn.py`

**Status:** 6/6 checks passed ✓

---

## Prompt 5 — Reservoir Optimization

**Prompt:**
> Implement a reservoir optimization using scipy.optimize.minimize for this problem:
> Parameters (define as constants at top of file):
>   V0 = 500_000        # initial storage m³
>   V_min = 100_000     # minimum storage m³
>   V_max = 1_000_000   # maximum storage m³
>   Q_eco = 10          # min ecological release m³/s
>   Q_max = 100         # max release m³/s
>   dt = 86400          # seconds per day
>   inflow  = [15, 12, 10, 8, 12, 15, 18]          # m³/s
>   price   = [0.08, 0.08, 0.08, 0.08, 0.10, 0.12, 0.10]  # $/kWh
>   eta     = 0.85      # turbine efficiency
>   g       = 9.81      # gravity
>   H       = 50        # average head (m)
>
> Write these functions:
> 1. compute_storage(Q_releases) → array of 8 storage values (V0 to V7)
> 2. objective(Q_releases) → negative total revenue
> 3. constraints list using scipy format
> 4. bounds: Q_eco <= Q[t] <= Q_max
> 5. solve() function using method='SLSQP'
> 6. Save results to optimal_schedule.csv

**Result:** Created reservoir optimization module with SLSQP optimizer.

---

## Prompt 6 — Project Extension (SCS-CN, Rational, Time-Area)

**Prompt:**
> Extend this project with modular, well-documented, and testable code.
>
> ## Objectives
> 1. Implement Time-Area Method for watershed routing
>    - Discretized time-area histogram
>    - Configurable watershed travel time distribution
>    - Output hydrograph (Q vs time)
>
> 2. Add Antecedent Moisture Condition (AMC) adjustments to SCS-CN
>    - Support AMC I, II, III
>    - Adjust Curve Number using standard conversion formulas
>    - Dynamic AMC selection via parameter
>
> 3. Build Interactive Visualization
>    - Matplotlib + widgets or Plotly
>    - Sliders for: Rainfall (P), Curve Number (CN)
>    - Dynamically update runoff and hydrograph
>
> 4. Compare Runoff Methods
>    - SCS-CN method
>    - Rational Method
>    - Time-Area method output
>
> ## Technical Requirements
> - Language: Python
> - Structure:
>   - hydrology/scs_cn.py
>   - hydrology/rational.py
>   - hydrology/time_area.py
>   - visualization/interactive_plot.py
>   - main.py
> - Code quality: Type hints, Google docstrings, clear interfaces
> - Output: Graphs (hydrograph comparisons), Console summary table

**Result:** Created complete package structure:
```
Project-2/
├── main.py
├── hydrology/
│   ├── __init__.py
│   ├── scs_cn.py          # With AMC adjustments
│   ├── rational.py        # Rational method
│   └── time_area.py     # Time-Area routing
└── visualization/
    ├── __init__.py
    └── interactive_plot.py
```

---

## Summary of Outputs

| File | Description | Status |
|------|-------------|--------|
| scs_cn_runoff.py | Core SCS-CN implementation | ✓ |
| test_runoff.py | Pytest test suite (11 tests) | ✓ |
| sensitivity_analysis.py | Visualization scripts | ✓ |
| validate_scs_cn.py | Validation (6/6 checks) | ✓ |
| hydrology/scs_cn.py | Extended with AMC | ✓ |
| hydrology/rational.py | Rational method | ✓ |
| hydrology/time_area.py | Time-Area routing | ✓ |
| visualization/interactive_plot.py | Interactive plots | ✓ |
| main.py | Comparison script | ✓ |

---

## Usage Examples

```bash
# Run default comparison
python main.py

# Custom parameters
python main.py -p 50 -c 80 -a 10 -l 1000 -s 0.01 --amc 2

# Generate plot
python main.py -p 50 -c 80 --plot
python main.py --save-plot result.png
```

---

*Last Updated: May 2025*