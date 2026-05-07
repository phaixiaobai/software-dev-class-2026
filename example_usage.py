"""
Example usage of the extended flood inundation system.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib.pyplot as plt
from hydrology.terrain_analysis import TerrainAnalyzer, create_synthetic_terrain
from hydrology.flood_routing import FloodRouter, BuildingGenerator, compute_flood_volume
from visualization.animation import FloodAnimator, create_static_visualization


def main():
    print("=" * 60)
    print("FLOOD INUNDATION SYSTEM - EXAMPLE USAGE")
    print("=" * 60)

    # Create synthetic DEM
    print("\n[1] Creating synthetic DEM...")
    dem = create_synthetic_terrain(rows=100, cols=100, resolution=30.0)
    print(f"    DEM shape: {dem.shape}")
    print(f"    Elevation range: {dem.min():.2f}m - {dem.max():.2f}m")

    # Terrain analysis
    print("\n[2] Computing terrain metrics...")
    analyzer = TerrainAnalyzer(dem, resolution=30.0)
    metrics = analyzer.compute_terrain_metrics()
    print(f"    Mean slope: {metrics['slope_mean']:.2f} degrees")
    print(f"    Max slope: {metrics['slope_max']:.2f} degrees")

    # Generate building footprints
    print("\n[3] Generating building footprints...")
    building_gen = BuildingGenerator(100, 100, num_buildings=30, seed=42)
    building_mask = building_gen.generate()
    print(f"    Buildings generated: {np.sum(building_mask)} cells")

    # Initialize flood router
    print("\n[4] Initializing flood router...")
    router = FloodRouter(dem, resolution=30.0, building_mask=building_mask, connectivity=8)

    # Single water level test
    print("\n[5] Running flood simulation at 45m water level...")
    flooded, depth = router.compute_flood_extent(45.0)
    stats = router.compute_flood_volume(45.0)
    print(f"    Flooded cells: {stats['flooded_cells']}")
    print(f"    Flooded area: {stats['flooded_percentage']:.2f}%")
    print(f"    Total volume: {stats['total_volume_m3']:,.0f} m³")
    print(f"    Mean depth: {stats['mean_depth_m']:.2f}m")

    # Rising water simulation
    print("\n[6] Running rising water simulation (40-50m)...")
    levels = np.arange(40, 51, 2)
    results = router.simulate_rising_water(levels)
    for i, lvl in enumerate(results['water_levels']):
        print(f"    {lvl}m: {results['flooded_pct'][i]:.1f}% flooded, "
              f"{results['volume_m3'][i]:,.0f} m³")

    # Static visualization
    print("\n[7] Creating static visualization...")
    create_static_visualization(dem, levels, building_mask=building_mask,
                                save_path='flood_stages.png')

    # Animation
    print("\n[8] Creating flood animation...")
    animator = FloodAnimator(dem, resolution=30.0, building_mask=building_mask)
    levels_anim = np.arange(40, 55, 5)
    animator.create_animation(levels_anim, 'flood_simulation.gif', fps=1)

    print("\n" + "=" * 60)
    print("COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    main()