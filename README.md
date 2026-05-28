# SCS-CN Runoff Model
### Specialized Experiment 2 · Xi'an Jiaotong University · Software Development 2026

---

Python implementation of the **USDA Soil Conservation Service Curve Number** method — the industry-standard technique for estimating direct surface runoff from a rainfall event. Built through AI-assisted prompting, fully tested with `pytest`, and validated against physical constraints.

---

## The Model

Three inputs, one output:

```
              CN (land-use type, 1–100)
              P  (rainfall depth, mm)
               │
               ▼
    S  = 25400/CN − 254        maximum retention (mm)
    Iₐ = 0.2 × S               initial abstraction (mm)
               │
     ┌─────────┴─────────┐
  P ≤ Iₐ               P > Iₐ
     │                     │
   Q = 0        Q = (P−Iₐ)² / (P−Iₐ+S)
               │
               ▼
            Q (mm)   runoff depth
```

**Verified example** — P = 50 mm, CN = 80 → S = 63.5, Iₐ = 12.7, **Q = 13.8 mm** ✓

---

## What's Included

| File | Purpose |
|---|---|
| `scs_cn_runoff.py` | Core functions: `calculate_S()`, `calculate_Ia()`, `calculate_runoff()` |
| `test_runoff.py` | pytest suite — 6 boundary conditions |
| `sensitivity_analysis.py` | CN sweep at P = 50 mm + full P–Q family of curves |
| `validate_scs_cn.py` | Automated physical constraint checks |
| `main.py` | Runs the full pipeline in one command |
| `cn_sensitivity.png` | Output plot — Q vs CN bar chart |
| `rainfall_runoff_curves.png` | Output plot — P–Q curves for CN 60 → 100 |
| `prompt_log.md` | All AI interactions, in order |
| `report.tex` | Experiment write-up (Overleaf) |

---

## Test Coverage

```
pytest test_runoff.py -v

  ✅  zero rainfall              → Q = 0
  ✅  P below initial abstraction → Q = 0
  ✅  P exactly at threshold      → Q = 0
  ✅  standard case (P=50, CN=80) → Q ≈ 13.8 mm
  ✅  impervious surface (CN=100) → Q ≈ P
  ✅  physical constraint Q ≤ P   → holds for all cases
```

---

## Sensitivity Findings

- Runoff increases **monotonically** with CN at fixed rainfall — consistent with physical expectations
- The curve steepens sharply above **CN = 90**, making urbanizing watersheds particularly sensitive to small land-use changes
- All P–Q curves converge toward `Q → P` as rainfall grows large — the upper bound holds everywhere

---

## Run It

```bash
git clone https://github.com/phaixiaobai/software-development-class-2026.git
git checkout project-2

pip install numpy matplotlib scipy pytest

python main.py                # full pipeline
pytest test_runoff.py -v      # tests only
python sensitivity_analysis.py  # regenerate plots
```

---

*Phanpasorn Laor-iam · 3125999087 · Xi'an Jiaotong University · 2026*
