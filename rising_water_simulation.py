import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from flood_analysis import calculate_flood


def simulate_rising_water(
    dem: np.ndarray, levels: np.ndarray | None = None
) -> pd.DataFrame:
    """
    Simulate flood inundation at multiple rising water levels.

    Parameters
    ----------
    dem : np.ndarray
        100x100 Digital Elevation Model (elevation in meters).
    levels : np.ndarray | None, optional
        Array of water levels to simulate. If None, uses np.arange(40, 51, 1).

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: water_level, flooded_pct, max_depth_m, flood_volume_m3
    """
    if levels is None:
        levels = np.arange(40, 51, 1)

    results = []
    for water_level in levels:
        _, depth_array, percentage, max_depth, total_volume = calculate_flood(
            dem, water_level
        )
        results.append(
            {
                "water_level": water_level,
                "flooded_pct": percentage,
                "max_depth_m": max_depth,
                "flood_volume_m3": total_volume,
            }
        )

    df = pd.DataFrame(results)

    flooded_pct = df["flooded_pct"].values
    water_levels = df["water_level"].values

    monotonic = all(
        flooded_pct[i] <= flooded_pct[i + 1] for i in range(len(flooded_pct) - 1)
    )
    if monotonic:
        print("[PASS] ✓ Flooded area increases monotonically")
    else:
        for i in range(len(flooded_pct) - 1):
            if flooded_pct[i] > flooded_pct[i + 1]:
                print(f"[FAIL] ✗ Non-monotonic at water level {water_levels[i]}m")
                break

    d_pct_per_meter = np.diff(flooded_pct) / np.diff(water_levels)
    max_idx = np.argmax(d_pct_per_meter)
    fastest_level = int(water_levels[max_idx])
    fastest_rate = d_pct_per_meter[max_idx]
    print(
        f"Fastest flooding: {fastest_level}m → {fastest_level + 1}m (+{fastest_rate:.1f}% per meter)"
    )
    print("  → Corresponds to valley/flat area in DEM")

    print("\n" + "=" * 55)
    print(
        f"{'Water Level':<12} | {'Flooded %':<10} | {'Max Depth':<10} | {'Volume (m³)':<15}"
    )
    print("=" * 55)
    for _, row in df.iterrows():
        print(
            f"{row['water_level']:<12} | {row['flooded_pct']:<10.1f} | {row['max_depth_m']:<10.1f} | {row['flood_volume_m3']:<15,.0f}"
        )
    print("=" * 55)

    fig, axes = plt.subplots(3, 1, figsize=(10, 12))

    ax1 = axes[0]
    ax1.plot(
        df["water_level"], df["flooded_pct"], marker="o", color="steelblue", linewidth=2
    )
    ax1.fill_between(df["water_level"], df["flooded_pct"], alpha=0.2, color="steelblue")
    ax1.set_xlabel("Water Level (m)")
    ax1.set_ylabel("Flooded Area (%)")
    ax1.set_title("Flood Inundation Curve")
    ax1.grid(True, alpha=0.3)

    ax2 = axes[1]
    ax2.plot(
        df["water_level"], df["max_depth_m"], marker="s", color="darkblue", linewidth=2
    )
    ax2.set_xlabel("Water Level (m)")
    ax2.set_ylabel("Max Depth (m)")
    ax2.set_title("Maximum Inundation Depth")
    ax2.grid(True, alpha=0.3)

    ax3 = axes[2]
    mid_levels = (df["water_level"].values[:-1] + df["water_level"].values[1:]) / 2
    colors = [
        "red" if i == max_idx else "steelblue" for i in range(len(d_pct_per_meter))
    ]
    ax3.bar(mid_levels, d_pct_per_meter, width=0.8, color=colors, edgecolor="white")
    ax3.set_xlabel("Water Level (m)")
    ax3.set_ylabel("Δ Flooded % per meter")
    ax3.set_title("Rate of Flood Extent Growth")
    ax3.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    plt.savefig("flood_curve.png", dpi=150, bbox_inches="tight")
    print(f"\nSaved: flood_curve.png")
    plt.close()

    return df


if __name__ == "__main__":
    dem = np.load("dem_data.npy")
    df = simulate_rising_water(dem)
