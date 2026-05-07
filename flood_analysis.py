import numpy as np


def calculate_flood(dem: np.ndarray, water_level: float) -> tuple:
    """
    Calculate flood inundation metrics for a given water level.

    Parameters
    ----------
    dem : np.ndarray
        100x100 Digital Elevation Model (elevation in meters).
    water_level : float
        Water level elevation in meters.

    Returns
    -------
    tuple
        (flooded_mask, depth_array, percentage, max_depth, total_volume)
        - flooded_mask: Boolean array, True where elevation < water_level.
        - depth_array: Water depth (m), 0 where not flooded.
        - percentage: Percent of cells flooded (0-100).
        - max_depth: Maximum water depth in meters.
        - total_volume: Total flood volume in cubic meters (assuming 30m x 30m cells).
    """
    flooded_mask = dem < water_level
    depth_array = np.maximum(water_level - dem, 0)
    n_flooded = flooded_mask.sum()
    percentage = (n_flooded / dem.size) * 100
    max_depth = depth_array.max()
    total_volume = depth_array.sum() * (30 * 30)

    return flooded_mask, depth_array, percentage, max_depth, total_volume


def validate_flood(
    dem: np.ndarray,
    water_level: float,
    flooded_mask: np.ndarray,
    depth_array: np.ndarray,
    percentage: float,
) -> dict:
    """
    Validate flood calculation results with multiple checks.

    Parameters
    ----------
    dem : np.ndarray
        Original DEM array.
    water_level : float
        Water level used in calculation.
    flooded_mask : np.ndarray
        Flooded mask from calculate_flood.
    depth_array : np.ndarray
        Depth array from calculate_flood.
    percentage : float
        Flooded percentage from calculate_flood.

    Returns
    -------
    dict
        Dictionary mapping check names to 'pass' or 'fail'.
    """
    checks = {}

    result = "pass" if 0 <= percentage <= 100 else "fail"
    checks["percentage_range"] = result
    print(
        f"[{result.upper()}] {'✓' if result == 'pass' else '✗'} CHECK 1: percentage between 0 and 100 (got {percentage:.1f}%)"
    )

    dem_min = dem.min()
    dem_max = dem.max()
    any_flooded = flooded_mask.any()

    if dem_min < water_level:
        expected_max_depth = water_level - dem_min
        result = "pass" if np.isclose(max_depth, expected_max_depth) else "fail"
        checks["max_depth_consistency"] = result
        print(
            f"[{result.upper()}] {'✓' if result == 'pass' else '✗'} CHECK 2: max depth == water_level - dem.min() (expected {expected_max_depth:.1f}m, got {max_depth:.1f}m)"
        )
    else:
        checks["max_depth_consistency"] = "pass"
        print(f"[PASS] ✓ CHECK 2: max depth consistency (no cells flooded, skipped)")

    result = "pass" if np.all(depth_array[~flooded_mask] == 0) else "fail"
    checks["depth_zero_not_flooded"] = result
    print(
        f"[{result.upper()}] {'✓' if result == 'pass' else '✗'} CHECK 3: depth is 0 everywhere NOT flooded"
    )

    result = "pass" if np.all(depth_array[flooded_mask] > 0) else "fail"
    checks["depth_positive_flooded"] = result
    print(
        f"[{result.upper()}] {'✓' if result == 'pass' else '✗'} CHECK 4: depth is positive everywhere flooded"
    )

    if water_level <= dem_min:
        result = "pass" if percentage == 0 else "fail"
        checks["zero_flood_at_min"] = result
        print(
            f"[{result.upper()}] {'✓' if result == 'pass' else '✗'} CHECK 5: if water_level <= dem.min(), percentage == 0 (got {percentage:.1f}%)"
        )
    else:
        checks["zero_flood_at_min"] = "pass"
        print(f"[PASS] ✓ CHECK 5: zero flood at min (condition not met, skipped)")

    if water_level > dem_max:
        result = "pass" if percentage == 100 else "fail"
        checks["full_flood_above_max"] = result
        print(
            f"[{result.upper()}] {'✓' if result == 'pass' else '✗'} CHECK 6: if water_level > dem.max(), percentage == 100 (got {percentage:.1f}%)"
        )
    else:
        checks["full_flood_above_max"] = "pass"
        print(f"[PASS] ✓ CHECK 6: full flood above max (condition not met, skipped)")

    return checks


if __name__ == "__main__":
    dem = np.load("dem_data.npy")

    print("=" * 50)
    print("Test: water_level = 45m")
    print("=" * 50)
    flooded_mask, depth_array, percentage, max_depth, total_volume = calculate_flood(
        dem, 45
    )
    print(f"Flooded cells: {flooded_mask.sum()}")
    print(f"Percentage: {percentage:.1f}%")
    print(f"Max depth: {max_depth:.1f} m")
    print(f"Total volume: {total_volume:.1f} m³")
    print()
    validate_flood(dem, 45, flooded_mask, depth_array, percentage)
    print()

    print("=" * 50)
    print("Test: water_level = 20m")
    print("=" * 50)
    flooded_mask, depth_array, percentage, max_depth, total_volume = calculate_flood(
        dem, 20
    )
    print(f"Percentage: {percentage:.1f}%")
    print()
    validate_flood(dem, 20, flooded_mask, depth_array, percentage)
    print()

    print("=" * 50)
    print("Test: water_level = 90m")
    print("=" * 50)
    flooded_mask, depth_array, percentage, max_depth, total_volume = calculate_flood(
        dem, 90
    )
    print(f"Percentage: {percentage:.1f}%")
    print()
    validate_flood(dem, 90, flooded_mask, depth_array, percentage)
