"""
Validation Script for Reservoir Optimization Solution
Checks all physical constraints and outputs validation_report.txt
"""

import csv
import os

# Parameters (must match optimization)
V_min = 100_000
V_max = 1_000_000
Q_eco = 10
Q_max = 100
dt = 86400
eta = 0.85
g = 9.81
H = 50
TOLERANCE = 1  # m³ tolerance for mass balance

# Input file
INPUT_FILE = "/Users/pasorn/Desktop/Xian-Jiaotong/class/sofware-dev/Assignment-4-Projects/Project-3/optimal_schedule.csv"
OUTPUT_FILE = "/Users/pasorn/Desktop/Xian-Jiaotong/class/sofware-dev/Assignment-4-Projects/Project-3/validation_report.txt"


def read_csv(filename):
    """Read CSV and return data as list of dicts."""
    data = []
    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(
                {
                    "day": int(row["Day"]),
                    "inflow": float(row["Inflow"]),
                    "release": float(row["Release"]),
                    "storage": float(row["Storage"]),
                    "revenue": float(row["Revenue"]),
                    "price": float(row["Price"]),
                }
            )
    return data


def validate_storage_lower(data):
    """CHECK 1: Storage >= V_min"""
    violations = []
    min_storage = float("inf")
    min_day = None

    for row in data:
        if row["storage"] < min_storage:
            min_storage = row["storage"]
            min_day = row["day"]
        if row["storage"] < V_min:
            violations.append(row["day"])

    if violations:
        return (
            False,
            f"Days violate: {violations}, min={min_storage:.0f} m³ on Day {min_day}",
        )
    else:
        return True, f"Min storage: {min_storage:.0f} m³ on Day {min_day}"


def validate_storage_upper(data):
    """CHECK 2: Storage <= V_max"""
    violations = []
    max_storage = 0
    max_day = None

    for row in data:
        if row["storage"] > max_storage:
            max_storage = row["storage"]
            max_day = row["day"]
        if row["storage"] > V_max:
            violations.append(row["day"])

    if violations:
        return (
            False,
            f"Days violate: {violations}, max={max_storage:.0f} m³ on Day {max_day}",
        )
    else:
        return True, f"Max storage: {max_storage:.0f} m³ on Day {max_day}"


def validate_eco_release(data):
    """CHECK 3: Release >= Q_eco"""
    violations = []
    min_release = float("inf")
    min_day = None

    for row in data:
        if row["release"] < min_release:
            min_release = row["release"]
            min_day = row["day"]
        if row["release"] < Q_eco:
            violations.append(row["day"])

    if violations:
        return (
            False,
            f"Days violate: {violations}, min={min_release:.2f} m³/s on Day {min_day}",
        )
    else:
        return (
            True,
            f"All releases >= {Q_eco} m³/s, min={min_release:.2f} m³/s on Day {min_day}",
        )


def validate_max_release(data):
    """CHECK 4: Release <= Q_max"""
    violations = []
    max_release = 0
    max_day = None

    for row in data:
        if row["release"] > max_release:
            max_release = row["release"]
            max_day = row["day"]
        if row["release"] > Q_max:
            violations.append(row["day"])

    if violations:
        return (
            False,
            f"Days violate: {violations}, max={max_release:.2f} m³/s on Day {max_day}",
        )
    else:
        return (
            True,
            f"All releases <= {Q_max} m³/s, max={max_release:.2f} m³/s on Day {max_day}",
        )


def validate_mass_balance(data):
    """CHECK 5: Mass balance verification"""
    V0 = 500_000  # initial storage
    violations = []

    for i, row in enumerate(data):
        if i == 0:
            expected_storage = V0 + (row["inflow"] - row["release"]) * dt
        else:
            expected_storage = (
                data[i - 1]["storage"] + (row["inflow"] - row["release"]) * dt
            )

        actual_storage = row["storage"]
        diff = abs(expected_storage - actual_storage)

        if diff > TOLERANCE:
            violations.append((row["day"], diff, expected_storage, actual_storage))

    if violations:
        details = ", ".join([f"Day {v[0]}: diff={v[1]:.1f}m³" for v in violations])
        return False, f"Violations: {details}"
    else:
        return True, f"All 7 days satisfy mass balance (tolerance={TOLERANCE}m³)"


def validate_revenue(data):
    """CHECK 6: Revenue recalculation"""
    violations = []

    for row in data:
        # Revenue = Q * H * eta * g * price * dt / 3_600_000
        calculated_rev = row["release"] * H * eta * g * row["price"] * dt / 3_600_000
        actual_rev = row["revenue"]
        diff = abs(calculated_rev - actual_rev)

        if diff > 0.01:  # Allow small floating point tolerance
            violations.append((row["day"], diff, calculated_rev, actual_rev))

    if violations:
        details = ", ".join(
            [f"Day {v[0]}: calc=${v[2]:.4f} vs CSV=${v[3]:.4f}" for v in violations]
        )
        return False, f"Violations: {details}"
    else:
        total_calc = sum(
            row["release"] * H * eta * g * row["price"] * dt / 3_600_000 for row in data
        )
        return True, f"All revenues verified, total=${total_calc:.2f}"


def main():
    """Run all validation checks."""
    print("=" * 70)
    print("RESERVOIR OPTIMIZATION VALIDATION REPORT")
    print("=" * 70)

    # Read data
    if not os.path.exists(INPUT_FILE):
        print(f"\n[ERROR] Input file not found: {INPUT_FILE}")
        return

    data = read_csv(INPUT_FILE)
    print(f"\nLoaded {len(data)} days from optimal_schedule.csv\n")

    # Run checks
    checks = [
        ("Storage Lower Bound (V_min)", validate_storage_lower),
        ("Storage Upper Bound (V_max)", validate_storage_upper),
        ("Ecological Release (Q_eco)", validate_eco_release),
        ("Maximum Release (Q_max)", validate_max_release),
        ("Mass Balance", validate_mass_balance),
        ("Revenue Calculation", validate_revenue),
    ]

    results = []
    for name, check_func in checks:
        passed, detail = check_func(data)
        status = "[PASS] ✓" if passed else "[FAIL] ✗"
        results.append(passed)
        print(f"{status} {name} — {detail}")

    # Calculate total revenue
    total_revenue = sum(row["revenue"] for row in data)
    passed_count = sum(results)

    # Final summary
    print("\n" + "=" * 70)
    print(f"{passed_count}/6 checks passed | Total Revenue: ${total_revenue:.2f}")
    print("=" * 70)

    # Write to file
    output_lines = [
        "=" * 70,
        "RESERVOIR OPTIMIZATION VALIDATION REPORT",
        "=" * 70,
        "",
        f"Loaded {len(data)} days from optimal_schedule.csv",
        "",
    ]

    for i, (name, check_func) in enumerate(checks):
        passed, detail = check_func(data)
        status = "[PASS] ✓" if passed else "[FAIL] ✗"
        output_lines.append(f"{status} {name} — {detail}")

    output_lines.extend(
        [
            "",
            "=" * 70,
            f"{passed_count}/6 checks passed | Total Revenue: ${total_revenue:.2f}",
            "=" * 70,
        ]
    )

    with open(OUTPUT_FILE, "w") as f:
        f.write("\n".join(output_lines))

    print(f"\nReport saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
