import csv
import numpy as np

V_min = 100_000
V_max = 1_000_000
Q_eco = 10
Q_max = 100
dt = 86400
H = 50
eta = 0.85
g = 9.81
tolerance = 1.0

input_file = "/Users/pasorn/Desktop/Xian-Jiaotong/class/sofware-dev/Assignment-4-Projects/Project-3/optimal_schedule.csv"
output_file = "/Users/pasorn/Desktop/Xian-Jiaotong/class/sofware-dev/Assignment-4-Projects/Project-3/validation_report.txt"


def read_csv():
    """Read optimal_schedule.csv and return data arrays."""
    days, inflows, releases, storages, revenues, prices = [], [], [], [], [], []

    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            days.append(int(row['Day']))
            inflows.append(float(row['Inflow']))
            releases.append(float(row['Release']))
            storages.append(float(row['Storage']))
            revenues.append(float(row['Revenue']))
            prices.append(float(row['Price']))

    return np.array(days), np.array(inflows), np.array(releases), np.array(storages), np.array(revenues), np.array(prices)


def validate():
    """Run all 6 validation checks."""
    days, inflows, releases, storages, revenues, prices = read_csv()

    results = []
    total_revenue_csv = revenues.sum()

    print("=" * 70)
    print("RESERVOIR OPTIMIZATION VALIDATION REPORT")
    print("=" * 70)

    min_storage = np.min(storages)
    min_storage_day = days[np.argmin(storages)]
    if min_storage >= V_min:
        results.append(True)
        print(f"[PASS] ✓ Storage Lower Bound — Min storage: {min_storage:,.0f} m³ on Day {min_storage_day}")
    else:
        results.append(False)
        print(f"[FAIL] ✗ Storage Lower Bound — Min storage: {min_storage:,.0f} m³ < {V_min:,} on Day {min_storage_day}")

    max_storage = np.max(storages)
    max_storage_day = days[np.argmax(storages)]
    if max_storage <= V_max:
        results.append(True)
        print(f"[PASS] ✓ Storage Upper Bound — Max storage: {max_storage:,.0f} m³ on Day {max_storage_day}")
    else:
        results.append(False)
        print(f"[FAIL] ✗ Storage Upper Bound — Max storage: {max_storage:,.0f} m³ > {V_max:,} on Day {max_storage_day}")

    violation_days = days[releases < Q_eco]
    if len(violation_days) == 0:
        results.append(True)
        print(f"[PASS] ✓ Ecological Release — All releases >= {Q_eco} m³/s")
    else:
        results.append(False)
        print(f"[FAIL] ✗ Ecological Release — Violated on days: {list(violation_days)}")

    violation_max = days[releases > Q_max]
    if len(violation_max) == 0:
        results.append(True)
        print(f"[PASS] ✓ Maximum Release — All releases <= {Q_max} m³/s")
    else:
        results.append(False)
        print(f"[FAIL] ✗ Maximum Release — Violated on days: {list(violation_max)}")

    V_current = 500000
    mass_balance_pass = True
    for i in range(len(days)):
        expected_V = V_current + (inflows[i] - releases[i]) * dt
        diff = abs(expected_V - storages[i])

        if storages[i] >= V_max - 1:
            action = "capped at V_max"
        elif storages[i] <= V_min + 1:
            action = "capped at V_min"
        else:
            action = ""

        if diff > tolerance and storages[i] < V_max - 1 and storages[i] > V_min + 1:
            mass_balance_pass = False
            print(f"[FAIL] ✗ Mass Balance — Day {days[i]}: Expected {expected_V:,.0f}, got {storages[i]:,.0f}, diff={diff:,.0f} m³ {action}")

        V_current = storages[i]

    if mass_balance_pass:
        results.append(True)
        print(f"[PASS] ✓ Mass Balance — All days within ±{tolerance} m³ tolerance")
    else:
        results.append(False)

    calc_revenues = releases * H * eta * g * prices * dt / 3_600_000
    revenue_matches = np.allclose(revenues, calc_revenues, rtol=1e-3)

    if revenue_matches:
        results.append(True)
        print(f"[PASS] ✓ Revenue Calculation — All revenues match (max error < 0.1%)")
    else:
        results.append(False)
        max_error = np.max(np.abs(revenues - calc_revenues))
        print(f"[FAIL] ✗ Revenue Calculation — Max error: ${max_error:.4f}")

    passed = sum(results)
    print("=" * 70)
    print(f"{passed}/6 checks passed | Total Revenue: ${total_revenue_csv:,.2f}")
    print("=" * 70)

    return results, total_revenue_csv, mass_balance_pass


def write_report(results, total_revenue, mass_balance_pass):
    """Write validation results to file."""
    days, inflows, releases, storages, revenues, prices = read_csv()

    with open(output_file, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("RESERVOIR OPTIMIZATION VALIDATION REPORT\n")
        f.write("=" * 70 + "\n\n")

        min_storage = np.min(storages)
        min_storage_day = days[np.argmin(storages)]
        if min_storage >= V_min:
            f.write(f"[PASS] ✓ Storage Lower Bound — Min storage: {min_storage:,.0f} m³ on Day {min_storage_day}\n")
        else:
            f.write(f"[FAIL] ✗ Storage Lower Bound — Min storage: {min_storage:,.0f} m³ < {V_min:,} on Day {min_storage_day}\n")

        max_storage = np.max(storages)
        max_storage_day = days[np.argmax(storages)]
        if max_storage <= V_max:
            f.write(f"[PASS] ✓ Storage Upper Bound — Max storage: {max_storage:,.0f} m³ on Day {max_storage_day}\n")
        else:
            f.write(f"[FAIL] ✗ Storage Upper Bound — Max storage: {max_storage:,.0f} m³ > {V_max:,} on Day {max_storage_day}\n")

        violation_days = days[releases < Q_eco]
        if len(violation_days) == 0:
            f.write(f"[PASS] ✓ Ecological Release — All releases >= {Q_eco} m³/s\n")
        else:
            f.write(f"[FAIL] ✗ Ecological Release — Violated on days: {list(violation_days)}\n")

        violation_max = days[releases > Q_max]
        if len(violation_max) == 0:
            f.write(f"[PASS] ✓ Maximum Release — All releases <= {Q_max} m³/s\n")
        else:
            f.write(f"[FAIL] ✗ Maximum Release — Violated on days: {list(violation_max)}\n")

        if mass_balance_pass:
            f.write(f"[PASS] ✓ Mass Balance — All days within ±{tolerance} m³ (accounting for bound cappings)\n")
        else:
            f.write(f"[FAIL] ✗ Mass Balance — Errors exceed ±{tolerance} m³\n")

        calc_revenues = releases * H * eta * g * prices * dt / 3_600_000
        revenue_matches = np.allclose(revenues, calc_revenues, rtol=1e-3)

        if revenue_matches:
            f.write(f"[PASS] ✓ Revenue Calculation — All revenues match (max error < 0.1%)\n")
        else:
            f.write(f"[FAIL] ✗ Revenue Calculation — Revenues do not match\n")

        passed = sum(results)
        f.write("=" * 70 + "\n")
        f.write(f"{passed}/6 checks passed | Total Revenue: ${total_revenue:,.2f}\n")
        f.write("=" * 70 + "\n")

    print(f"\nReport saved to: {output_file}")


if __name__ == "__main__":
    results, total_rev, mb_pass = validate()
    write_report(results, total_rev, mb_pass)