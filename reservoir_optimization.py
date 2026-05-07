"""
Reservoir Dispatch Optimization using scipy.optimize.minimize
"""

import numpy as np
from scipy.optimize import minimize
import csv

# Parameters
V0 = 500_000  # initial storage m³
V_min = 100_000  # minimum storage m³
V_max = 1_000_000  # maximum storage m³
Q_eco = 10  # min ecological release m³/s
Q_max = 100  # max release m³/s
dt = 86400  # seconds per day
inflow = np.array([15, 12, 10, 8, 12, 15, 18])  # m³/s
price = np.array([0.08, 0.08, 0.08, 0.08, 0.10, 0.12, 0.10])  # $/kWh
eta = 0.85  # turbine efficiency
g = 9.81  # gravity
H = 50  # average head (m)


def compute_storage(Q_releases):
    """
    Compute storage values for all 8 time points (V0 to V7).

    Uses mass balance: V[t+1] = V[t] + (inflow[t] - Q[t]) * dt

    Args:
        Q_releases: array of 7 release values (Q1 to Q7)

    Returns:
        array of 8 storage values (V0 to V7)
    """
    n = len(Q_releases)
    storage = np.zeros(n + 1)
    storage[0] = V0

    for t in range(n):
        storage[t + 1] = storage[t] + (inflow[t] - Q_releases[t]) * dt

    return storage


def objective(Q_releases):
    """
    Compute negative total revenue for minimization.

    Revenue per day = Q[t] * H * eta * g * price[t] * dt / 3_600_000

    Args:
        Q_releases: array of 7 release values

    Returns:
        Negative total revenue (since we want to maximize)
    """
    power_per_day = Q_releases * H * eta * g * price * dt / 3_600_000  # kWh
    total_revenue = np.sum(power_per_day)
    return -total_revenue


def compute_constraints(Q_releases):
    """
    Compute constraint values for scipy.optimize format.

    Returns:
        List of constraint values (storage violations)
    """
    storage = compute_storage(Q_releases)

    # Storage constraints: V_min <= V[t] <= V_max for t=1..7
    # In scipy: constraints are of form fun(x) >= 0 or fun(x) = 0
    # We'll use inequality constraints: g(x) >= 0

    constraints = []

    # Lower bounds: V[t] - V_min >= 0 for t=1..7
    # Upper bounds: V_max - V[t] >= 0 for t=1..7

    return storage


def create_constraints():
    """
    Create scipy-compatible constraints list.
    """
    constraints = []

    # Storage lower bound: V[t] >= V_min  (for t=1..7)
    # This is V[t] - V_min >= 0
    for i in range(1, 8):
        constraints.append(
            {"type": "ineq", "fun": lambda x, idx=i: compute_storage(x)[idx] - V_min}
        )

    # Storage upper bound: V[t] <= V_max  (for t=1..7)
    # This is V_max - V[t] >= 0
    for i in range(1, 8):
        constraints.append(
            {"type": "ineq", "fun": lambda x, idx=i: V_max - compute_storage(x)[idx]}
        )

    return constraints


def create_constraints_efficient():
    """
    Create more efficient constraints using vectorized form.
    """

    def storage_lower_bounds(x):
        storage = compute_storage(x)
        return storage[1:] - V_min  # V1 to V7 >= V_min

    def storage_upper_bounds(x):
        storage = compute_storage(x)
        return V_max - storage[1:]  # V1 to V7 <= V_max

    constraints = [
        {"type": "ineq", "fun": storage_lower_bounds},
        {"type": "ineq", "fun": storage_upper_bounds},
    ]

    return constraints


def create_bounds():
    """
    Create bounds for release variables: Q_eco <= Q[t] <= Q_max
    """
    bounds = [(Q_eco, Q_max) for _ in range(7)]
    return bounds


def solve():
    """
    Solve the reservoir optimization problem.

    Uses SLSQP method with initial guess equal to inflow.
    """
    # Initial guess: neutral release = inflow
    Q_initial = inflow.copy()

    # Create constraints and bounds
    constraints = create_constraints_efficient()
    bounds = create_bounds()

    # Solve
    result = minimize(
        fun=objective,
        x0=Q_initial,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"disp": True, "maxiter": 1000},
    )

    # Extract results
    optimal_releases = result.x
    storage = compute_storage(optimal_releases)

    # Compute revenues per day
    power_per_day = optimal_releases * H * eta * g * price * dt / 3_600_000
    total_revenue = np.sum(power_per_day)

    # Print results
    print("\n" + "=" * 60)
    print("OPTIMAL RESERVOIR DISPATCH RESULTS")
    print("=" * 60)
    print(f"\nOptimization Status: {'Success' if result.success else 'Failed'}")
    print(f"Message: {result.message}")
    print(f"\nTotal Revenue: ${total_revenue:.2f}")

    print("\nDaily Schedule:")
    print("-" * 60)
    print(f"{'Day':<5} {'Inflow':<10} {'Release':<10} {'Storage':<15} {'Revenue':<12}")
    print("-" * 60)
    for t in range(7):
        print(
            f"{t + 1:<5} {inflow[t]:<10.1f} {optimal_releases[t]:<10.2f} {storage[t + 1]:<15.0f} ${power_per_day[t]:<11.2f}"
        )
    print("-" * 60)
    print(f"{'Total':<5} {'':<10} {'':<10} {'':<15} ${total_revenue:<11.2f}")

    # Save to CSV
    save_results(optimal_releases, storage, power_per_day)

    return result, total_revenue


def save_results(releases, storage, revenues):
    """
    Save optimization results to CSV file.

    Args:
        releases: array of optimal release values
        storage: array of storage values (V0 to V7)
        revenues: array of daily revenues
    """
    output_path = "/Users/pasorn/Desktop/Xian-Jiaotong/class/sofware-dev/Assignment-4-Projects/Project-3/optimal_schedule.csv"

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Day", "Inflow", "Release", "Storage", "Revenue", "Price"])

        for t in range(7):
            writer.writerow(
                [
                    t + 1,
                    inflow[t],
                    round(releases[t], 2),
                    int(storage[t + 1]),
                    round(revenues[t], 4),
                    price[t],
                ]
            )

    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    result, total_revenue = solve()
