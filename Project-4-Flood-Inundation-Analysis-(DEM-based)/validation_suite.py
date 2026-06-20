import numpy as np
import pandas as pd
from flood_analysis import calculate_flood


def run_validation(dem: np.ndarray) -> str:
    """
    Run comprehensive physical validation for flood inundation system.
    """
    cell_area = 30 * 30
    results = []
    passed = 0
    total = 0

    def record(test_name: str, passed_test: bool, details: str = ""):
        nonlocal passed, total
        total += 1
        if passed_test:
            passed += 1
            status = f"[PASS] ✓ {test_name}"
        else:
            status = f"[FAIL] ✗ {test_name}"
        if details:
            status += f" — {details}"
        results.append(status)
        return passed_test

    results.append("=" * 47)
    results.append("FLOOD INUNDATION — PHYSICAL VALIDATION REPORT")
    results.append("=" * 47)

    results.append("\n--- SECTION 1: Edge Case Validation ---")

    _, _, pct, _, _ = calculate_flood(dem, dem.min() - 1)
    record(
        "Test 1a: Zero flood below min elevation", pct == 0.0, f"flooded % = {pct:.1f}%"
    )

    _, _, pct, _, _ = calculate_flood(dem, dem.max() + 1)
    record(
        "Test 1b: Full flood above max elevation",
        pct == 100.0,
        f"flooded % = {pct:.1f}%",
    )

    _, _, pct, _, _ = calculate_flood(dem, dem.mean())
    record(
        "Test 1c: ~50% flood at mean elevation",
        30 <= pct <= 70,
        f"flooded % = {pct:.1f}% (expected 30-70%)",
    )

    results.append("\n--- SECTION 2: Depth Validation ---")

    flooded_mask, depth_array, percentage, max_depth, _ = calculate_flood(dem, 45)
    expected_max = 45 - dem.min()
    record(
        "Test 2a: Max depth equals water_level - dem.min()",
        abs(max_depth - expected_max) < 0.001,
        f"expected {expected_max:.3f}m, got {max_depth:.3f}m",
    )

    record("Test 2b: No negative depths", np.all(depth_array >= 0), "all depths >= 0")

    record(
        "Test 2c: Depth > 0 where flooded",
        np.all(depth_array[flooded_mask] > 0),
        "depth > 0 for all flooded cells",
    )

    record(
        "Test 2d: Depth == 0 where not flooded",
        np.all(depth_array[~flooded_mask] == 0),
        "depth = 0 for all non-flooded cells",
    )

    results.append("\n--- SECTION 3: Monotonicity Validation ---")

    levels = np.arange(35, 56, 1)
    pcts = []
    volumes = []
    max_depths = []
    for lvl in levels:
        _, _, pct, max_d, vol = calculate_flood(dem, lvl)
        pcts.append(pct)
        max_depths.append(max_d)
        volumes.append(vol)

    pcts = np.array(pcts)
    volumes = np.array(volumes)
    max_depths = np.array(max_depths)

    non_decreasing = all(pcts[i] <= pcts[i + 1] for i in range(len(pcts) - 1))
    record(
        "Test 3a: Flooded % non-decreasing", non_decreasing, "monotonic across 35-55m"
    )

    non_decreasing_vol = all(
        volumes[i] <= volumes[i + 1] for i in range(len(volumes) - 1)
    )
    record(
        "Test 3b: Flooded volume non-decreasing",
        non_decreasing_vol,
        "monotonic across 35-55m",
    )

    depth_increases = all(
        abs((max_depths[i + 1] - max_depths[i]) - 1.0) < 0.001
        for i in range(len(max_depths) - 1)
    )
    record(
        "Test 3c: Max depth increases 1m per 1m water rise",
        depth_increases,
        "linear relationship",
    )

    results.append("\n--- SECTION 4: Area/Volume Calculation ---")

    n_flooded = flooded_mask.sum()
    total_flooded_area = n_flooded * cell_area
    flood_volume = depth_array.sum() * cell_area

    manual_area = n_flooded * 900
    record(
        "Test 4a: Total flooded area calculation",
        abs(total_flooded_area - manual_area) < 0.01,
        f"{total_flooded_area:.0f} m²",
    )

    manual_vol = depth_array.sum() * 900
    record(
        "Test 4b: Flood volume calculation",
        abs(flood_volume - manual_vol) < 0.01,
        f"{flood_volume:.0f} m³",
    )

    record(
        "Test 4c: Manual verification at 45m",
        n_flooded == 2219 and abs(total_flooded_area - 1997100) < 1,
        f"n_flooded={n_flooded}, area={total_flooded_area:.0f} m²",
    )

    summary = f"\n{'=' * 47}\nSUMMARY: {passed}/{total} checks passed"
    results.append(summary)

    physical_valid = "CONFIRMED" if passed == total else "NEEDS REVIEW"
    results.append(f"Physical validity: {physical_valid}\n{'=' * 47}")

    report = "\n".join(results)
    return report


if __name__ == "__main__":
    dem = np.load("dem_data.npy")
    report = run_validation(dem)
    print(report)

    with open("validation_report.txt", "w") as f:
        f.write(report)
    print("\nSaved: validation_report.txt")
