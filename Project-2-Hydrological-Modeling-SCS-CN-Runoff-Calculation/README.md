# 💧 SCS-CN Runoff Model
### Specialized Experiment 2 · Xi'an Jiaotong University · Software Development 2026

---

Python implementation of the **USDA Soil Conservation Service Curve Number (SCS-CN)** method — the industry-standard equation for estimating direct surface runoff from rainfall. Covers formula implementation, edge-case testing, CN sensitivity analysis, and physical constraint validation, all developed with AI-assisted prompting.

---

## The Model

```
S  =  25400 / CN  −  254          potential maximum retention  [mm]
Ia =  0.2 × S                     initial abstraction          [mm]

        (P − Ia)²
Q  =  ───────────────    when P > Ia,   else  Q = 0
        P − Ia + S
```

**Verified against the reference case:**
P = 50 mm, CN = 80 → S = 63.5 mm, Ia = 12.7 mm, **Q = 13.8 mm** ✓

---

## Test Coverage

Six boundary conditions, all passing:

```
✅  Zero rainfall          (0, 80)       →  Q = 0
✅  Below abstraction      (P < Ia, 80)  →  Q = 0
✅  At threshold           (P = Ia, 80)  →  Q = 0
✅  Reference case         (50, 80)      →  Q ≈ 13.8 mm
✅  Impervious surface     (50, 100)     →  Q ≈ P
✅  Constraint check       all inputs    →  Q ≤ P always
```

---

## Outputs

| File | Description |
|---|---|
| `cn_sensitivity.png` | Bar chart — Q vs CN at fixed P = 50 mm |
| `rainfall_runoff_curves.png` | P–Q curves for CN ∈ {60, 70, 80, 90, 95, 100} |

**Key finding:** The CN–Q relationship is **strongly non-linear above CN = 90** — small increases in impervious cover cause disproportionately large runoff jumps.

---

## Project Files

```
├── scs_cn_runoff.py          core model  —  calculate_S(), calculate_Ia(), calculate_runoff()
├── test_runoff.py            pytest suite  —  6 boundary conditions
├── sensitivity_analysis.py   CN sweep + plot generation
├── validate_scs_cn.py        physical constraint verification
├── main.py                   end-to-end pipeline runner
├── prompt_log.md             all AI prompts and responses, in order
└── report.tex                Overleaf experiment write-up
```

---

## Run It

```bash
git clone https://github.com/phaixiaobai/software-development-class-2026.git
cd software-development-class-2026 && git checkout project-2

pip install numpy matplotlib pytest scipy

python main.py                  # full pipeline
pytest test_runoff.py -v        # tests only
python sensitivity_analysis.py  # plots only
```

---

*Phanpasorn Laor-iam · 3125999087 · Xi'an Jiaotong University · 2026*
