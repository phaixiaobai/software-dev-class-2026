import numpy as np
import csv

V0 = 500_000
V_min = 100_000
V_max = 1_000_000
Q_eco = 10
Q_max = 100
dt = 86400
inflow = np.array([15, 12, 10, 8, 12, 15, 18])
price = np.array([0.08, 0.08, 0.08, 0.08, 0.10, 0.12, 0.10])
eta = 0.85
g = 9.81
H = 50


def compute_storage(Q_releases):
    """
    Compute storage values V0 to V7 using mass balance.
    V[t+1] = V[t] + (inflow[t] - Q[t]) * dt

    Args:
        Q_releases: array of 7 release values (Q1 to Q7)

    Returns:
        array of 8 storage values (V0 to V7)
    """
    Q = np.asarray(Q_releases)
    storage = np.zeros(8)
    storage[0] = V0

    for t in range(7):
        storage[t + 1] = storage[t] + (inflow[t] - Q[t]) * dt

    return storage


def objective(Q_releases):
    """
    Calculate negative total revenue for minimization.

    Revenue per day = Q[t] * H * eta * g * price[t] * dt / 3_600_000

    Args:
        Q_releases: array of 7 release values

    Returns:
        negative total revenue
    """
    Q = np.asarray(Q_releases)
    power_coefficient = H * eta * g / 3_600_000
    daily_revenue = Q * power_coefficient * price * dt
    total_revenue = np.sum(daily_revenue)
    return -total_revenue


def compute_constraints(Q_releases):
    """
    Compute constraint values for storage bounds.

    Returns:
        array of constraint values [V1-V_min, V_max-V1, V2-V_min, ...]
    """
    storage = compute_storage(Q_releases)
    constraints = []

    for t in range(1, 8):
        constraints.append(storage[t] - V_min)
        constraints.append(V_max - storage[t])

    return np.array(constraints)


def create_bounds():
    """Create bounds for release variables: Q_eco <= Q[t] <= Q_max"""
    return [(Q_eco, Q_max) for _ in range(7)]


def create_constraints():
    """Create constraint dictionary for scipy.optimize"""
    constraints = []

    for t in range(1, 8):
        lower = {'type': 'ineq', 'fun': lambda Q, t_idx=t: compute_storage(Q)[t_idx] - V_min}
        upper = {'type': 'ineq', 'fun': lambda Q, t_idx=t: V_max - compute_storage(Q)[t_idx]}
        constraints.append(lower)
        constraints.append(upper)

    return constraints


def solve():
    """Solve the reservoir optimization problem using SLSQP."""
    from scipy.optimize import minimize

    x0 = inflow.copy()

    bounds = create_bounds()
    constraints = create_constraints()

    result = minimize(
        objective,
        x0,
        method='SLSQP',
        bounds=bounds,
        constraints=constraints,
        options={'maxiter': 1000, 'ftol': 1e-10}
    )

    optimal_releases = result.x
    optimal_storage = compute_storage(optimal_releases)

    power_coefficient = H * eta * g / 3_600_000
    daily_revenue = optimal_releases * power_coefficient * price * dt
    total_revenue = np.sum(daily_revenue)

    print("=" * 60)
    print("OPTIMAL RESERVOIR DISPATCH SOLUTION")
    print("=" * 60)
    print(f"\nOptimal Releases (m³/s): {optimal_releases.round(2)}")
    print(f"Optimal Storage (m³):    {optimal_storage.round(0)}")
    print(f"\nTotal Revenue: ${total_revenue:.2f}")
    print(f"Optimization Status: {result.message}")
    print(f"Iterations: {result.nit}")

    return result, optimal_releases, optimal_storage, total_revenue, daily_revenue


def save_results(optimal_releases, optimal_storage, daily_revenue, price):
    """Save optimization results to CSV file."""
    output_path = "/Users/pasorn/Desktop/Xian-Jiaotong/class/sofware-dev/Assignment-4-Projects/Project-3/optimal_schedule.csv"

    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Day', 'Inflow', 'Release', 'Storage', 'Revenue', 'Price'])

        for t in range(7):
            writer.writerow([
                t + 1,
                inflow[t],
                round(optimal_releases[t], 2),
                round(optimal_storage[t + 1], 0),
                round(daily_revenue[t], 2),
                price[t]
            ])

    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    result, releases, storage, total_rev, daily_rev = solve()
    save_results(releases, storage, daily_rev, price)