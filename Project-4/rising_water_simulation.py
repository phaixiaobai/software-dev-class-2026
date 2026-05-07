import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from flood_analysis import calculate_flood


def simulate_rising_water(dem: np.ndarray, levels: np.ndarray = None) -> pd.DataFrame:
    """
    Simulate flood inundation at multiple rising water levels.

    Args:
        dem: 2D numpy array (100, 100) of elevation values in meters.
        levels: Array of water levels to simulate. If None, uses np.arange(40, 51, 1).

    Returns:
        pd.DataFrame with columns: water_level, flooded_pct, max_depth_m, flood_volume_m3
    """
    if levels is None:
        levels = np.arange(40, 51, 1)

    results = []
    for water_level in levels:
        flooded_mask, depth_array, percentage, max_depth, total_volume = calculate_flood(dem, water_level)
        results.append({
            'water_level': water_level,
            'flooded_pct': percentage,
            'max_depth_m': max_depth,
            'flood_volume_m3': total_volume
        })

    return pd.DataFrame(results)


if __name__ == "__main__":
    from dem_generator import load_dem

    dem = load_dem(None)

    df = simulate_rising_water(dem)

    flooded_pct = df['flooded_pct'].values
    water_levels = df['water_level'].values

    is_monotonic = all(flooded_pct[i] <= flooded_pct[i+1] for i in range(len(flooded_pct)-1))
    if is_monotonic:
        print("[PASS] ✓ Flooded area increases monotonically")
    else:
        for i in range(len(flooded_pct)-1):
            if flooded_pct[i] > flooded_pct[i+1]:
                print(f"[FAIL] ✗ Non-monotonic at water level {water_levels[i]}m")
                break

    d_pct_per_meter = np.diff(flooded_pct) / np.diff(water_levels)
    max_idx = np.argmax(d_pct_per_meter)
    fastest_level = water_levels[max_idx]
    fastest_rate = d_pct_per_meter[max_idx]
    print(f"Fastest flooding: {fastest_level}m → {fastest_level+1}m (+{fastest_rate:.1f}% per meter)")
    print("Explanation: This corresponds to the valley/flat area in the DEM where small water level rises cause large inundation")

    fig, axes = plt.subplots(3, 1, figsize=(10, 12))

    axes[0].plot(water_levels, flooded_pct, marker='o', color='steelblue')
    axes[0].fill_between(water_levels, flooded_pct, alpha=0.2)
    axes[0].set_xlabel("Water Level (m)")
    axes[0].set_ylabel("Flooded Area (%)")
    axes[0].set_title("Flood Inundation Curve")
    axes[0].grid(True)

    axes[1].plot(water_levels, df['max_depth_m'], color='darkblue', marker='s')
    axes[1].set_xlabel("Water Level (m)")
    axes[1].set_ylabel("Max Depth (m)")
    axes[1].set_title("Maximum Inundation Depth")
    axes[1].grid(True)

    mid_levels = (water_levels[:-1] + water_levels[1:]) / 2
    bars = axes[2].bar(mid_levels, d_pct_per_meter, color='steelblue', edgecolor='white')
    bars[max_idx].set_color('red')
    axes[2].set_xlabel("Water Level (m)")
    axes[2].set_ylabel("Δ Flooded % per meter")
    axes[2].set_title("Rate of Flood Extent Growth")
    axes[2].grid(True)

    plt.tight_layout()
    plt.savefig('flood_curve.png', dpi=150, bbox_inches='tight')
    print("\nFigure saved to flood_curve.png")

    print("\n" + "=" * 60)
    print("Summary Table")
    print("=" * 60)
    print(f"{'Water Level':<12} | {'Flooded %':<10} | {'Max Depth':<10} | {'Volume (m³)':<15}")
    print("-" * 60)
    for _, row in df.iterrows():
        print(f"{int(row['water_level'])}m{'':<8} | {row['flooded_pct']:.1f}%{'':<5} | {row['max_depth_m']:.1f}m{'':<5} | {int(row['flood_volume_m3']):,}")
    print("=" * 60)