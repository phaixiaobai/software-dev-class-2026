# Flood Inundation System - Documentation

## Overview

This is a comprehensive DEM-based flood inundation modeling system implemented in Python. It includes terrain analysis, flood routing with building barriers, volume calculation, and animated visualization.

---

## Module Structure

```
Project-4/
├── hydrology/
│   ├── terrain_analysis.py    # DEM loading, slope, flow direction
│   └── flood_routing.py        # BFS-based flood propagation
├── visualization/
│   └── animation.py            # Static plots and animated GIFs
├── data/                       # Data directory (DEM, masks)
├── dem_generator.py           # Synthetic DEM generation
├── flood_analysis.py           # Basic flood calculations
├── flood_visualization.py     # 4-panel visualization
├── rising_water_simulation.py # Rising water analysis
├── example_usage.py           # Complete example
└── prompt.md                  # Original requirements
```

---

## Flood Routing Logic

### Algorithm: Breadth-First Search (BFS) Propagation

1. **Initialization**: Find all cells where `elevation < water_level` (initially flooded)

2. **Queue-based propagation**:
   - Add all initially flooded cells to queue
   - For each cell popped from queue:
     - Check 4 or 8 neighbors (configurable)
     - If neighbor elevation < water_level AND not visited:
       - Mark as flooded
       - Add to queue

3. **Building constraints**:
   - Building cells act as barriers (flood cannot pass through)
   - Neighboring check skips building cells

### Key Assumptions

- **Simplified physics**: No momentum, diffusion, or time-varying flows
- **Instantaneous flooding**: Water level is static (not a hydrograph)
- **Flat water surface**: No grade/advection effects
- **Cell-based resolution**: 30m default (configurable)

---

## Key Features

### 1. Terrain Analysis
- Slope calculation using finite differences
- D8 flow direction (simplified)
- DEM validation (no NaNs, consistent resolution)

### 2. Building Barriers
- Binary mask: 1 = blocked, 0 = open
- Synthetic generation (random rectangles)
- External loading (optional)

### 3. Flood Volume Calculation
```
volume = Σ(depth[cell] × cell_area)
cell_area = resolution² (default: 30m × 30m = 900m²)
```

### 4. Animated Simulation
- Time-varying water levels
- Consistent color scaling
- GIF export via imageio

---

## Suggested Improvements

### 1. Real Hydrodynamic Modeling

- **2D Shallow Water Equations (SWE)**
  - Include momentum conservation
  - Simulate flow velocity and direction
  - Better for flash floods, dam breaks

- **Diffusion Wave Approximation**
  - Simpler than full SWE
  - Still captures inundation dynamics

### 2. Rainfall-Runoff Coupling

- Integrate with models like:
  - **HEC-HMS** (US Army Corps)
  - **SWAT** (Soil and Water Assessment Tool)
  - ** VIC** (Variable Infiltration Capacity)

- Use rainfall intensity → runoff → water level input

### 3. Additional Enhancements

- **Infiltration**: Green-Ampt, SCS curve number methods
- **Levee/sewer modeling**: Breach simulation
- **Uncertainty**: Monte Carlo on DEM error
- **Real data**: SRTM, LiDAR DEMs via rasterio

---

## Usage Example

```python
from hydrology.terrain_analysis import create_synthetic_terrain
from hydrology.flood_routing import FloodRouter, BuildingGenerator
from visualization.animation import FloodAnimator

# Create DEM
dem = create_synthetic_terrain(100, 100, resolution=30.0)

# Generate buildings
buildings = BuildingGenerator(100, 100, num_buildings=30).generate()

# Initialize router with buildings
router = FloodRouter(dem, resolution=30.0, building_mask=buildings)

# Compute flood at 45m
flooded, depth = router.compute_flood_extent(45.0)

# Get volume stats
stats = router.compute_flood_volume(45.0)
print(f"Volume: {stats['total_volume_m3']:,.0f} m³")

# Create animation
animator = FloodAnimator(dem, building_mask=buildings)
levels = np.arange(40, 60, 5)
animator.create_animation(levels, 'flood.gif', fps=1)
```

---

## Physical Units

| Parameter | Unit |
|-----------|------|
| Elevation | meters (m) |
| Depth | meters (m) |
| Volume | cubic meters (m³) |
| Cell size | meters (m) |
| Slope | degrees (°) |

---

## Limitations

- No momentum/velocity modeling
- No infiltration/evapotranspiration
- Buildings are complete barriers (no door/windows)
- No temporal dynamics (static water level)

For production flood modeling, consider coupling with专业的 hydrodynamic models (e.g., MIKE FLOOD, TUFLOW, HEC-RAS 2D).