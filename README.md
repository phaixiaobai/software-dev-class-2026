# 🌊 Flood Inundation Analysis (DEM-based)
### Specialized Experiment 4 · Xi'an Jiaotong University · Software Development 2026

---

A five-part computational pipeline for DEM-based flood modelling: generate synthetic terrain, compute inundation at any water level, visualize in four panels, simulate a rising flood from 40–50 m, and verify every physical constraint with a 13-check validation suite. Extended with an animated GIF and multi-stage comparison figure — developed end-to-end with AI-assisted prompting.

---

## Physics

```
flood mask    flood[i,j] = 1    if  z[i,j] < W
depth         d[i,j] = max(W − z[i,j],  0)
flooded area  P = (Σ flood[i,j] / N) × 100 %
flood volume  V = Σ d[i,j] × 900 m²
```

The synthetic DEM is a 100×100 grid: base gradient 30–80 m, river valley depression at columns 40–50, spatially correlated Gaussian noise (σ = 5 m).

---

## Validation — 13/13 PASS

```
Edge cases        ✅  zero flood below min elevation
                  ✅  100 % flood above max elevation
                  ✅  ~50 % flood at mean elevation

Depth             ✅  max depth = W − z_min
                  ✅  no negative depths
                  ✅  depth > 0 for all flooded cells
                  ✅  depth = 0 for all dry cells

Monotonicity      ✅  flooded % non-decreasing (35–55 m sweep)
                  ✅  flood volume non-decreasing (35–55 m sweep)
                  ✅  max depth increases exactly 1 m per 1 m rise

Area / Volume     ✅  total area = 1,997,100 m²
                  ✅  volume = 11,422,919 m³ at W = 45 m
                  ✅  manual cell count matches at W = 45 m (n = 2,219)
```

---

## Dynamic Simulation (40–50 m)

| Water Level | Flooded % | Max Depth | Volume |
|---|---|---|---|
| 40 m | 11.8% | 10.4 m | 4,591,080 m³ |
| 45 m | 22.2% | 15.4 m | 11,422,800 m³ |
| 50 m | 36.2% | 20.4 m | 24,001,200 m³ |

Fastest-growing interval: **49→50 m (+3.1 %/m)** — valley floor widening as water overtops channel banks.

---

## Project Files

```
├── dem_generator.py           Part 1 — terrain generation → dem_data.npy
├── flood_analysis.py          Part 2 — calculate_flood(), validate_flood()
├── flood_visualization.py     Part 3 — four-panel figure at any water level
├── rising_water_simulation.py Part 4 — 40–50 m sweep → flood_curve.png
├── validation_suite.py        Part 5 — 13 physical checks
├── example_usage.py           runs the complete pipeline end-to-end
├── run.sh                     activates venv and executes pipeline
├── flood_extent_40m.png       output visualization at 40 m
├── flood_extent_50m.png       output visualization at 50 m
├── flood_curve.png            dynamic simulation chart
├── flood_stages.png           extension: multi-level side-by-side
├── flood_simulation.gif       extension: animated rising water (11 frames)
├── validation_report.txt      13/13 PASS report
├── prompt_log.md              all AI prompts and responses, in order
└── report.tex                 Overleaf experiment write-up
```

---

## Run It

```bash
git clone https://github.com/phaixiaobai/software-development-class-2026.git
cd software-development-class-2026 && git checkout project-4

# recommended — uses the bundled venv setup
chmod +x run.sh && ./run.sh

# or manually
pip install -r requirements.txt
python example_usage.py
```

---

*Phanpasorn Laor-iam · 3125999087 · Xi'an Jiaotong University · 2026*
