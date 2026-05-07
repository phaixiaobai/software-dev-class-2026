import numpy as np


def calculate_flood(dem: np.ndarray, water_level: float) -> tuple:
    """
    Calculate flood inundation metrics for a given water level.

    Args:
        dem: 2D numpy array (100, 100) of elevation values in meters.
        water_level: Water surface elevation in meters.

    Returns:
        tuple: (flooded_mask, depth_array, percentage, max_depth, total_volume)
            - flooded_mask: Boolean array where True indicates flooded cells (dem < water_level)
            - depth_array: Water depth at each cell (0 where not flooded, positive where flooded)
            - percentage: Percentage of area flooded (0-100)
            - max_depth: Maximum flood depth in meters
            - total_volume: Total flood volume in cubic meters (cell size 30m x 30m)
    """
    flooded_mask = dem < water_level

    depth_array = np.maximum(water_level - dem, 0)

    n_flooded = np.sum(flooded_mask)
    percentage = (n_flooded / dem.size) * 100

    max_depth = depth_array.max()

    total_volume = depth_array.sum() * (30 * 30)

    return flooded_mask, depth_array, percentage, max_depth, total_volume


def validate_flood(dem: np.ndarray, water_level: float, flooded_mask: np.ndarray,
                   depth_array: np.ndarray, percentage: float) -> dict:
    """
    Validate flood calculation results with multiple checks.

    Args:
        dem: 2D numpy array of elevation values.
        water_level: Water surface elevation in meters.
        flooded_mask: Boolean array of flooded cells.
        depth_array: Calculated depth array.
        percentage: Percentage of area flooded.

    Returns:
        dict: Dictionary with check names as keys and pass/fail as values.
    """
    results = {}

    check1 = 0 <= percentage <= 100
    results["percentage_range"] = check1
    print(f"[{'PASS' if check1 else 'FAIL'}] CHECK 1: percentage_range (value: {percentage:.2f}%)")

    dem_min = dem.min()
    dem_max = dem.max()
    any_flooded = dem_min < water_level

    if any_flooded:
        expected_max_depth = water_level - dem_min
        check2 = np.isclose(max_depth, expected_max_depth)
        print(f"[{'PASS' if check2 else 'FAIL'}] CHECK 2: max_depth_correct (expected: {expected_max_depth:.2f}, got: {max_depth:.2f})")
    else:
        check2 = True
        results["max_depth_correct"] = check2
        print(f"[PASS] CHECK 2: max_depth_correct (no flood - not applicable)")

    not_flooded = ~flooded_mask
    check3 = np.all(depth_array[not_flooded] == 0)
    results["depth_zero_not_flooded"] = check3
    print(f"[{'PASS' if check3 else 'FAIL'}] CHECK 3: depth_zero_not_flooded")

    flooded = flooded_mask
    if np.any(flooded):
        check4 = np.all(depth_array[flooded] > 0)
    else:
        check4 = True
    results["depth_positive_flooded"] = check4
    print(f"[{'PASS' if check4 else 'FAIL'}] CHECK 4: depth_positive_flooded")

    if water_level <= dem_min:
        check5 = np.isclose(percentage, 0.0)
    else:
        check5 = True
    results["no_flood_below_terrain"] = check5
    print(f"[{'PASS' if check5 else 'FAIL'}] CHECK 5: no_flood_below_terrain (water_level: {water_level}, dem_min: {dem_min:.2f})")

    if water_level > dem_max:
        check6 = np.isclose(percentage, 100.0)
    else:
        check6 = True
    results["full_flood_above_terrain"] = check6
    print(f"[{'PASS' if check6 else 'FAIL'}] CHECK 6: full_flood_above_terrain (water_level: {water_level}, dem_max: {dem_max:.2f})")

    return results


if __name__ == "__main__":
    from dem_generator import load_dem

    dem = load_dem(None)

    print("\n=== Test: water_level = 45m ===")
    flooded_mask, depth_array, percentage, max_depth, total_volume = calculate_flood(dem, 45)
    print(f"Flooded cells: {np.sum(flooded_mask)}")
    print(f"Percentage: {percentage:.2f}%")
    print(f"Max depth: {max_depth:.2f} m")
    print(f"Total volume: {total_volume:.2f} m³")
    validate_flood(dem, 45, flooded_mask, depth_array, percentage)

    print("\n=== Test: water_level = 20m ===")
    flooded_mask, depth_array, percentage, max_depth, total_volume = calculate_flood(dem, 20)
    print(f"Percentage: {percentage:.2f}%")
    validate_flood(dem, 20, flooded_mask, depth_array, percentage)

    print("\n=== Test: water_level = 90m ===")
    flooded_mask, depth_array, percentage, max_depth, total_volume = calculate_flood(dem, 90)
    print(f"Percentage: {percentage:.2f}%")
    validate_flood(dem, 90, flooded_mask, depth_array, percentage)