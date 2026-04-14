# Prompt Log — Experiment 2: SCS-CN Runoff

This document logs the AI-assisted coding experiment for implementing the Soil Conservation Service Curve Number (SCS-CN) runoff method.

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

**What AI generated:**
- Created three functions: `calculate_S(CN)`, `calculate_Ia(S)`, and `calculate_runoff(P, CN)`
- Implemented the SCS-CN formula with proper type hints and docstrings
- Added input validation for CN range (1-100) and negative precipitation
- Included step 4 to cap Q if it exceeds P

**Errors found:**
- Initial implementation was mathematically correct, but did not explicitly include the Q ≤ P capping step in the original requirements
- The validation logic was present but could have been more explicit about the physical constraint

**Correction made:**
- Added explicit check: `if Q > P: Q = P` to ensure conservation of mass
- This ensures runoff never exceeds precipitation, which is a fundamental physical constraint

---

## Prompt 2 — Test Suite

**Prompt used:**
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

**What AI generated:**
- Created `test_runoff.py` with parametrized tests for zero runoff conditions
- Implemented individual tests for normal case, high CN, max CN, and Q ≤ P constraint
- Added monotonicity test looping CN from 60 to 100 with constant P=50mm
- Included input validation tests for negative P and out-of-range CN

**Errors found:**
- Minor issue with import path when running from different directories
- Initial test ran with wrong Python environment lacking pytest

**Correction made:**
- Updated test to import from `scs_cn_runoff` module
- Used full path `/opt/anaconda3/bin/python -m pytest` to ensure correct environment

---

## Prompt 3 — Sensitivity Analysis

**Prompt used:**
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

**What AI generated:**
- Created `sensitivity_analysis.py` with two analysis functions
- Generated summary table showing CN, Q, and Runoff Ratio percentage
- Created bar+line chart with RdYlGn color gradient
- Generated multi-line plot with viridis colors and shaded region

**Errors found:**
- No critical errors; code executed correctly on first attempt

**Correction made:**
- No corrections needed; visualizations produced matching outputs

---

## Prompt 4 — Validation

**Prompt used:**
> Write a Python script to validate the SCS-CN implementation with 6 checks:
> 1. Zero rainfall: P=0 → Q=0 for CN=[60,70,80,90,100]
> 2. Below Ia: P < Ia → Q=0
> 3. Physical constraint: Q ≤ P for 1000 random samples (seed=42)
> 4. Monotonicity: Q increases as CN increases (60-100)
> 5. Known reference: P=50, CN=80 → Q between 13.5-14.1
> 6. Impervious: CN=100, P=[100,150,200] → Q within 1mm of P

**What AI generated:**
- Created `validate_scs_cn.py` with 6 validation functions
- Used numpy with seed=42 for reproducible random testing
- Printed structured PASS/FAIL report with symbols
- Final summary showing X/6 checks passed

**Errors found:**
- No errors detected

**Correction made:**
- None required; all 6 checks passed successfully

---

## Key Observations

### 1. How does Q change as CN increases?

As the Curve Number (CN) increases, runoff (Q) increases significantly. This has clear physical meaning: higher CN values represent watersheds with less infiltration capacity, meaning more precipitation becomes runoff rather than being absorbed into the soil. For P=50mm, increasing CN from 60 to 100 increases Q from 1.40 mm to 50.00 mm — a 35-fold increase. This demonstrates the model correctly captures the inverse relationship between infiltration and runoff.

### 2. What CN value produces the biggest jump in runoff?

The runoff curve becomes steepest between CN=90 and CN=100. Using the sensitivity analysis data:
- CN 80→90: Q increases from 13.80 mm to 27.11 mm (+13.31 mm)
- CN 90→95: Q increases from 27.11 mm to 36.90 mm (+9.79 mm)  
- CN 95→100: Q increases from 36.90 mm to 50.00 mm (+13.10 mm)

The steepest absolute jump occurs around CN 80→90, but the proportional increase is highest near CN=100 where the watershed approaches impervious behavior.

### 3. Does the AI-generated code match the expected Q = 13.8 mm?

Yes. The implementation produces Q = 13.80 mm for P = 50 mm and CN = 80, which matches the expected value exactly (within 0.01 mm tolerance). This confirms the SCS-CN formula was implemented correctly according to the standard method.

---

## Summary

All four AI-generated components (implementation, tests, analysis, validation) passed verification. The code correctly implements the SCS-CN method and satisfies physical constraints including conservation of mass, monotonicity, and boundary conditions.
