# Flood Inundation System - User Prompts

## Prompt 1: DEM Generation Function

**Task:** Implement a function to load or generate a synthetic Digital Elevation Model (DEM) for flood inundation experiments.

```
def load_dem(filepath: str | None = None) -> np.ndarray:
    """
    Load or generate a synthetic DEM.

    Args:
        filepath (str | None): Path to a .npy DEM file. If provided, load DEM from file.

    Returns:
        np.ndarray: 2D array of shape (100, 100) representing elevation in meters.
    """
```

### Behavior

#### Case 1: filepath is NOT None
- Load DEM using: np.load(filepath)
- Validate:
  - Must be a numpy array
  - Must have shape (100, 100)
- If validation fails → raise ValueError with clear message
- Return the loaded DEM

#### Case 2: filepath is None → Generate synthetic DEM

##### Step 1: Base terrain (smooth gradient)
- Create two 1D gradients:
  row_gradient = np.linspace(30, 80, 100)
  col_gradient = np.linspace(30, 80, 100)

- Create 2D terrain:
  terrain[i, j] = (row_gradient[i] + col_gradient[j]) / 2

##### Step 2: Add valley channel
- For all rows:
  columns 40 to 50 (inclusive)
  subtract 10 meters from terrain

##### Step 3: Add realistic terrain noise
- Set seed: np.random.seed(42)
- Generate noise: np.random.normal(0, 3, (100, 100))
- Smooth noise using:
  scipy.ndimage.gaussian_filter(noise, sigma=5)

- Add smoothed noise to terrain

##### Step 4: Clip elevation
- Clip values to range [25, 85] using np.clip

##### Step 5: Save DEM
- Save as: "dem_data.npy" in current working directory
- Use np.save()

##### Step 6: Print statistics (formatted)
- Shape: (100, 100)
- Min elevation: X.X m
- Max elevation: X.X m
- Mean elevation: X.X m
- Std deviation: X.X m

### Technical Requirements

- Use:
  - numpy
  - scipy.ndimage
- Include:
  - Type hints
  - Google-style docstring
  - Clear variable naming
- Ensure:
  - Deterministic output (via seed)
  - Numerical stability

---

## Prompt 2: Flood Inundation Functions

**Task:** Write Python flood inundation functions for my DEM-based analysis.

### Function 1: calculate_flood(dem, water_level) → tuple

Input: dem (100×100 numpy array), water_level (float, meters)

**Steps:**
1. flooded_mask = boolean array where dem < water_level (True = flooded)
2. depth_array = water_level - dem, set to 0 where not flooded
   depth_array = np.maximum(water_level - dem, 0)
3. n_flooded = number of True cells in flooded_mask
4. percentage = (n_flooded / dem.size) * 100
5. max_depth = depth_array.max()
6. total_volume = depth_array.sum() * (30 * 30)  # cell size 30m × 30m

**Return:** (flooded_mask, depth_array, percentage, max_depth, total_volume)
Add docstring with physical explanation of each return value.

### Function 2: validate_flood(dem, water_level, flooded_mask, depth_array, percentage)

Run these checks and return dict of {check_name: pass/fail}:

- CHECK 1: percentage between 0 and 100
- CHECK 2: max depth == water_level - dem.min() if any cell flooded (only valid if dem.min() < water_level)
- CHECK 3: depth is 0 everywhere NOT flooded
- CHECK 4: depth is positive everywhere flooded
- CHECK 5: if water_level <= dem.min(): percentage == 0
- CHECK 6: if water_level > dem.max(): percentage == 100

Print each check as [PASS] ✓ or [FAIL] ✗ with details.

### Test both functions with:
- water_level = 45m → print results
- water_level = 20m → should give 0% flooded
- water_level = 90m → should give 100% flooded

---

## Prompt 3: Visualization Function

**Task:** Write a comprehensive visualization function for my flood inundation analysis.

**Function: visualize_flood(dem, water_level, save_path=None)**
- Internally calls calculate_flood(dem, water_level)
- Creates a figure with 2 rows × 2 columns (figsize=14,10)

### Subplot 1 (top-left) — Original DEM Terrain:
- imshow(dem, cmap='terrain')
- Colorbar labeled "Elevation (m)"
- Title: "Digital Elevation Model"
- Add contour lines at every 5m interval in white, linewidth=0.5

### Subplot 2 (top-right) — Flood Extent Overlay:
- Show DEM as grayscale background: imshow(dem, cmap='gray', alpha=0.6)
- Overlay flood mask in blue:
  flood_display = np.ma.masked_where(~flooded_mask, flooded_mask)
  imshow(flood_display, cmap='Blues', alpha=0.7, vmin=0, vmax=1)
- Title: f"Flood Extent at {water_level}m Water Level"
- Add text annotation: f"Flooded: {percentage:.1f}%"
  position: top-right corner of plot, fontsize=12, color=white,
  bbox=dict(boxstyle='round', facecolor='blue', alpha=0.7)

### Subplot 3 (bottom-left) — Inundation Depth Heatmap:
- depth_display = np.ma.masked_where(depth_array==0, depth_array)
- imshow(depth_display, cmap='Blues', vmin=0)
- Colorbar labeled "Inundation Depth (m)"
- Title: "Inundation Depth Map"

### Subplot 4 (bottom-right) — Depth Distribution:
- Histogram of depth_array[flooded_mask] values
- bins=30, color='steelblue', edgecolor='white'
- xlabel: "Inundation Depth (m)"
- ylabel: "Number of Cells"
- Title: "Distribution of Flood Depths"
- Add vertical dashed line at mean depth
- Add text: f"Mean depth: {mean_depth:.2f}m\nMax depth: {max_depth:.2f}m"

### Overall figure title:
f"Flood Inundation Analysis — Water Level: {water_level}m"
plt.tight_layout()

If save_path provided: plt.savefig(save_path, dpi=150, bbox_inches='tight')

### Test:
Call visualize_flood(dem, 40, 'flood_extent_40m.png')
Call visualize_flood(dem, 50, 'flood_extent_50m.png')

---

## Prompt 4: Rising Water Simulation

**Task:** Write a dynamic rising water simulation for my flood inundation system.

**Function: simulate_rising_water(dem, levels=None) → pandas DataFrame**

If levels is None: use np.arange(40, 51, 1) → [40,41,...,50]

For each water_level in levels:
- Call calculate_flood(dem, water_level)
- Record: water_level, percentage, max_depth, total_volume_m3

**Return DataFrame with columns:**
water_level, flooded_pct, max_depth_m, flood_volume_m3

### After collecting results:

1. **Validate monotonicity:**
   - Check flooded_pct increases at each step (or stays same)
   - Print: "[PASS] ✓ Flooded area increases monotonically"
   - Or: "[FAIL] ✗ Non-monotonic at water level Xm"

2. **Calculate rate of change:**
   - d_pct_per_meter = np.diff(flooded_pct) / np.diff(water_levels)
   - Find: which 1m rise causes the biggest area increase?
   - Print: f"Fastest flooding: {X}m → {X+1}m (+{Y:.1f}% per meter)"
   - Explain: this corresponds to the valley/flat area in the DEM

3. **Create flood_curve.png with 3 subplots stacked vertically:**

   **Subplot 1 — Water Level vs Flooded Percentage:**
   - Line plot with markers (marker='o', color='steelblue')
   - Fill area under curve: fill_between with alpha=0.2
   - xlabel: "Water Level (m)", ylabel: "Flooded Area (%)"
   - Title: "Flood Inundation Curve"
   - Add grid

   **Subplot 2 — Water Level vs Max Depth:**
   - Line plot (color='darkblue', marker='s')
   - xlabel: "Water Level (m)", ylabel: "Max Depth (m)"
   - Title: "Maximum Inundation Depth"

   **Subplot 3 — Rate of Area Change:**
   - Bar chart of d_pct_per_meter vs mid-level values
   - Highlight the max bar in red
   - xlabel: "Water Level (m)", ylabel: "Δ Flooded % per meter"
   - Title: "Rate of Flood Extent Growth"

4. **Print summary table:**

```
Water Level | Flooded % | Max Depth | Volume (m³)
40m         | X%        | X.Xm      | X,XXX,XXX
```

Save plot as: flood_curve.png

---

## Prompt 5: Advanced Flood Inundation System

**Task:** Extend the existing DEM-based flood inundation system with advanced features.
All implementations must be modular, numerically stable, and physically interpretable.

### Extension Objectives

#### 1. Load and Analyze Real DEM Data
- Support loading GeoTIFF DEM files (preferred: rasterio)
- Extract:
  - Elevation grid
  - Spatial resolution (cell size in meters)
- Normalize DEM if needed (preserve relative elevation differences)

- Compute terrain metrics:
  - Slope (finite difference)
  - Flow direction (D8 method, simplified)
- Validate DEM integrity (no NaNs, consistent resolution)

---

#### 2. Flood Routing (Grid-Based Inundation Model)

Implement a cellular flood spread algorithm:

- **Input:**
  - DEM (2D array)
  - Water level (scalar or time-varying)

- **Logic:**
  - A cell is flooded if: water_level > elevation[cell]
  - Water spreads to 4 or 8 neighboring cells (configurable)

- **Implement iterative propagation:**
  - BFS or queue-based flood fill
  - Ensure no infinite loops
  - Maintain visited mask

- **Output:**
  - Flood extent map (boolean grid)
  - Flood depth map: depth = water_level - elevation

---

#### 3. Building Footprints as Barriers

- Represent buildings as a binary mask:
  - 1 = भवन (blocked), 0 = open

- **Behavior:**
  - Flood cannot pass through building cells
  - Buildings reduce connectivity in flood routing

- **Allow:**
  - Synthetic building generation (random rectangles)
  OR
  - Load from external mask file

---

#### 4. Animated Flood Simulation

- Simulate rising water levels over time:
  - Define water level series (e.g., linear or hydrograph-driven)

- For each timestep:
  - Compute flood extent + depth
  - Store frame

- **Export:**
  - Animated GIF using imageio or matplotlib.animation

- **Requirements:**
  - Consistent color scale for depth
  - Overlay DEM or flood mask

---

#### 5. Flood Volume Calculation

- Compute total flood volume:

  volume = Σ (depth[cell] × cell_area)

- **Where:**
  - depth in meters
  - cell_area = resolution²

- **Return:**
  - Total volume (m³)
  - Number of flooded cells
  - Mean flood depth

---

### Technical Requirements

- **Language:** Python
- **Libraries:**
  - numpy
  - scipy (optional)
  - rasterio (for real DEM)
  - matplotlib / imageio

- **Structure:**
  ```
  hydrology/
    flood_routing.py
    terrain_analysis.py
  visualization/
    animation.py
  data/
    (DEM + masks)
  ```

- **Code Quality:**
  - Type hints
  - Google-style docstrings
  - Deterministic where applicable
  - No hardcoded constants

---

### Output Requirements

Return in this order:

1. Full modular code implementation
2. Example usage:
   - Load DEM
   - Run flood simulation
   - Generate animation
3. Brief explanation:
   - Flood routing logic
   - Key assumptions
4. Suggested improvements:
   - Real hydrodynamic modeling (2D shallow water equations)
   - Coupling with rainfall-runoff models

---

### Constraints

- Use physically meaningful units (meters, m³)
- Avoid oversimplified flood logic (must include propagation)
- Ensure computational efficiency (avoid O(n³) patterns)

---

### Execution Strategy

1. Define data structures (DEM, masks, grids)
2. Implement flood routing core
3. Add building constraints
4. Add time simulation
5. Add visualization + volume calculation