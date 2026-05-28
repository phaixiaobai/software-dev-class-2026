# DEM-based Flood Inundation Analysis
### Specialized Experiment 4 · Xi'an Jiaotong University · Software Development 2026

---

A five-part flood modelling pipeline — from synthetic terrain generation to animated inundation simulation — built using AI-assisted CoT prompting and verified by a 13-check physical validation suite.

---

## Pipeline Overview

```
  dem_generator.py
        │  generates a 100×100 synthetic elevation grid
        │  (gradient 30–80 m · river valley cols 40–50 · Gaussian noise σ=5)
        ▼
  flood_analysis.py
        │  calculate_flood(dem, W) → mask, depth, area%, max depth, volume
        │  validate_flood()        → 6 physical consistency checks
        ▼
  flood_visualization.py
        │  four-panel figure per water level:
        │  terrain+contours | flood extent | depth heatmap | histogram
        ▼
  rising_water_simulation.py
        │  sweeps W from 40 m → 50 m in 1 m steps
        │  verifies monotonicity · identifies fastest-growing interval
        ▼
  validation_suite.py
        │  13 automated checks across 4 categories
        └─ → 13/13 PASS ✅
```

---

## Governing Physics

```python
flood[i,j]  =  1        if  z[i,j] < W          # flooded cell
depth[i,j]  =  max(W - z[i,j], 0)               # inundation depth (m)
area_pct    =  sum(flood) / N * 100              # % of grid flooded
volume      =  sum(depth) * 900                  # m³  (cell = 30m × 30m)
```

---

## Validation — 13/13 PASS

```
Edge Cases     ✅ zero flood below min elev  ✅ full flood above max elev  ✅ ~50% at mean elev
Depth          ✅ d_max = W − z_min          ✅ no negatives               ✅ depth>0 iff flooded  ✅ depth=0 iff dry
Monotonicity   ✅ area non-decreasing        ✅ volume non-decreasing       ✅ d_max linear with W
Area/Volume    ✅ area = 1,997,100 m²        ✅ volume = 11,422,919 m³      ✅ manual verification at 45 m
```

---

## Dynamic Simulation (40 → 50 m)

| W (m) | Flooded % | Max Depth (m) | Volume (m³) |
|---|---|---|---|
| 40 | 11.8 | 10.4 | 4,591,080 |
| 45 | 22.2 | 15.4 | 11,422,800 |
| 50 | 36.2 | 20.4 | 24,001,200 |

Fastest growth: **49 → 50 m** at +3.1%/m — valley floor widening drives the jump.

---

## File Overview

```
├── dem_generator.py           Part 1 — terrain generation → dem_data.npy
├── flood_analysis.py          Part 2 — core flood engine
├── flood_visualization.py     Part 3 — four-panel plots
├── rising_water_simulation.py Part 4 — dynamic rising-water loop
├── validation_suite.py        Part 5 — 13-check physical validation
├── example_usage.py           runs the full pipeline end-to-end
├── run.sh                     shell convenience script
├── dem_data.npy               saved 100×100 DEM array
├── flood_extent_40m.png       visualization output at 40 m
├── flood_extent_50m.png       visualization output at 50 m
├── flood_curve.png            dynamic simulation curve
├── flood_stages.png           extension: multi-level comparison
├── flood_simulation.gif       extension: animated rising water
├── validation_report.txt      13/13 PASS summary
├── requirements.txt           pip dependencies
├── prompt_log.md              all AI prompts + agent responses
└── report.tex                 experiment write-up (Overleaf)
```

---

## Run It

```bash
git clone https://github.com/phaixiaobai/software-development-class-2026.git
git checkout project-4

# recommended — uses bundled venv setup
chmod +x run.sh && ./run.sh

# or manually
pip install -r requirements.txt
python example_usage.py         # full pipeline
python validation_suite.py      # check all 13 constraints
```

---

*Phanpasorn Laor-iam · 3125999087 · Xi'an Jiaotong University · 2026*
