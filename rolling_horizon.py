"""
Rolling Horizon (Model Predictive Control) Reservoir Optimization
Compare full horizon vs rolling horizon approaches
"""

import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import csv

# Base parameters
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
POWER_CONV = eta * g * H * dt / 3_600_000


def compute_storage(Q_releases, inflow, V_start):
    """Compute storage values for a given window."""
    n = len(Q_releases)
    storage = np.zeros(n + 1)
    storage[0] = V_start
    for t in range(n):
        storage[t + 1] = storage[t] + (inflow[t] - Q_releases[t]) * dt
    return storage


def compute_revenue(Q_releases, prices):
    """Compute revenue for a given window."""
    power = Q_releases * POWER_CONV
    return np.sum(power * prices)


def solve_window(inflow_window, price_window, V_start):
    """Solve optimization for a single window."""
    n = len(inflow_window)

    def objective(Q):
        storage = compute_storage(Q, inflow_window, V_start)
        if np.any(storage[1:] < V_min) or np.any(storage[1:] > V_max):
            return 1e10
        return -compute_revenue(Q, price_window)

    bounds = [(Q_eco, Q_max) for _ in range(n)]
    x0 = inflow_window.copy()

    result = minimize(
        fun=objective,
        x0=x0,
        method="SLSQP",
        bounds=bounds,
        options={"ftol": 1e-10, "maxiter": 1000},
    )

    if result.success:
        return result.x
    else:
        return None


def rolling_horizon_optimize(horizon=3):
    """
    Rolling horizon optimization (Model Predictive Control).

    At each step, optimize a horizon-length window, execute only day 1,
    then slide forward.

    Args:
        horizon: number of days to optimize ahead (default 3)

    Returns:
        Dictionary with full 7-day schedule
    """
    n_days = 7
    releases = np.zeros(n_days)
    storages = np.zeros(n_days + 1)
    revenues = np.zeros(n_days)

    storages[0] = V0

    for t in range(n_days):
        # Get window slices
        end_idx = min(t + horizon, n_days)
        inflow_window = inflow[t:end_idx]
        price_window = price[t:end_idx]

        # Pad if window shorter than horizon
        if len(inflow_window) < horizon:
            inflow_window = np.pad(
                inflow_window, (0, horizon - len(inflow_window)), mode="edge"
            )
            price_window = np.pad(
                price_window, (0, horizon - len(price_window)), mode="edge"
            )

        # Solve optimization for window
        Q_opt = solve_window(inflow_window, price_window, storages[t])

        if Q_opt is not None:
            releases[t] = Q_opt[0]  # Execute only first day
        else:
            # Fallback: use ecological minimum
            releases[t] = Q_eco

        # Update storage for executed day
        storages[t + 1] = storages[t] + (inflow[t] - releases[t]) * dt

        # Compute revenue
        revenues[t] = releases[t] * POWER_CONV * price[t]

    return {
        "releases": releases,
        "storages": storages,
        "revenues": revenues,
        "total_revenue": np.sum(revenues),
    }


def full_horizon_optimize():
    """Solve full 7-day horizon optimization (original approach)."""
    n_days = 7

    def objective(Q):
        storage = compute_storage(Q, inflow, V0)
        if np.any(storage[1:] < V_min) or np.any(storage[1:] > V_max):
            return 1e10
        return -compute_revenue(Q, price)

    bounds = [(Q_eco, Q_max) for _ in range(n_days)]
    x0 = inflow.copy()

    result = minimize(
        fun=objective,
        x0=x0,
        method="SLSQP",
        bounds=bounds,
        options={"ftol": 1e-10, "maxiter": 1000},
    )

    if result.success:
        Q_opt = result.x
        storages = compute_storage(Q_opt, inflow, V0)
        revenues = Q_opt * POWER_CONV * price
        return {
            "releases": Q_opt,
            "storages": storages,
            "revenues": revenues,
            "total_revenue": np.sum(revenues),
        }
    else:
        return None


def create_comparison_table(full_result, rolling_result):
    """Create side-by-side comparison table."""
    print("\n" + "=" * 90)
    print("COMPARISON TABLE: Full Horizon vs Rolling Horizon (horizon=3)")
    print("=" * 90)
    print(
        f"{'Day':<5} {'Inflow':<10} {'Rel_Full':<12} {'Rel_Rolling':<12} {'Store_Full':<15} {'Store_Rolling':<15}"
    )
    print("-" * 90)

    for t in range(7):
        print(
            f"{t + 1:<5} {inflow[t]:<10.1f} {full_result['releases'][t]:<12.2f} "
            f"{rolling_result['releases'][t]:<12.2f} {full_result['storages'][t + 1]:<15.0f} "
            f"{rolling_result['storages'][t + 1]:<15.0f}"
        )

    print("-" * 90)
    print(f"{'Total':<5} {'':<10} {'':<12} {'':<12} {'':<15} {'':<15}")
    print(
        f"{'Revenue':<5} {'':<10} ${full_result['total_revenue']:<11.2f} ${rolling_result['total_revenue']:<11.2f}"
    )
    print("=" * 90)


def plot_comparison(full_result, rolling_result):
    """Create comparison plots."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    days = np.arange(1, 8)

    # Subplot 1: Daily releases (grouped bar chart)
    ax1 = axes[0]
    width = 0.35
    x = np.arange(7)

    bars1 = ax1.bar(
        x - width / 2,
        full_result["releases"],
        width,
        label="Full Horizon",
        color="steelblue",
        edgecolor="black",
    )
    bars2 = ax1.bar(
        x + width / 2,
        rolling_result["releases"],
        width,
        label="Rolling Horizon",
        color="coral",
        edgecolor="black",
    )

    ax1.axhline(
        y=Q_eco, color="green", linestyle="--", linewidth=1.5, label=f"Q_eco = {Q_eco}"
    )
    ax1.set_xlabel("Day")
    ax1.set_ylabel("Release (m³/s)")
    ax1.set_title("Daily Releases Comparison")
    ax1.set_xticks(x)
    ax1.set_xticklabels(days)
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Subplot 2: Storage trajectory
    ax2 = axes[1]
    storage_days = np.arange(0, 8)

    ax2.plot(
        storage_days,
        full_result["storages"],
        "b-o",
        linewidth=2,
        markersize=6,
        label="Full Horizon",
    )
    ax2.plot(
        storage_days,
        rolling_result["storages"],
        "r-s",
        linewidth=2,
        markersize=6,
        label="Rolling Horizon",
    )
    ax2.axhline(
        y=V_min,
        color="green",
        linestyle="--",
        linewidth=1.5,
        label=f"V_min = {V_min / 1000:.0f}k",
    )
    ax2.axhline(
        y=V_max,
        color="purple",
        linestyle="--",
        linewidth=1.5,
        label=f"V_max = {V_max / 1000:.0f}k",
    )

    ax2.set_xlabel("Day")
    ax2.set_ylabel("Storage (m³)")
    ax2.set_title("Storage Trajectory Comparison")
    ax2.set_xticks(storage_days)
    ax2.legend(loc="upper right")
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim([0, V_max * 1.1])

    plt.tight_layout()
    plt.savefig("rolling_horizon_comparison.png", dpi=150)
    plt.close()
    print("\nPlot saved to: rolling_horizon_comparison.png")


def save_comparison_csv(full_result, rolling_result):
    """Save comparison data to CSV."""
    output_path = "/Users/pasorn/Desktop/Xian-Jiaotong/class/sofware-dev/Assignment-4-Projects/Project-3/rolling_horizon_comparison.csv"

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "Day",
                "Inflow",
                "Release_Full",
                "Release_Rolling",
                "Storage_Full",
                "Storage_Rolling",
                "Revenue_Full",
                "Revenue_Rolling",
            ]
        )

        for t in range(7):
            writer.writerow(
                [
                    t + 1,
                    inflow[t],
                    round(full_result["releases"][t], 2),
                    round(rolling_result["releases"][t], 2),
                    int(full_result["storages"][t + 1]),
                    int(rolling_result["storages"][t + 1]),
                    round(full_result["revenues"][t], 4),
                    round(rolling_result["revenues"][t], 4),
                ]
            )

    print(f"Data saved to: {output_path}")


def main():
    """Run rolling horizon vs full horizon comparison."""
    print("=" * 70)
    print("ROLLING HORIZON OPTIMIZATION")
    print("=" * 70)

    print("\n1. Running Full Horizon Optimization (7-day window)...")
    full_result = full_horizon_optimize()
    print(f"   Total Revenue: ${full_result['total_revenue']:.2f}")

    print("\n2. Running Rolling Horizon Optimization (3-day window)...")
    rolling_result = rolling_horizon_optimize(horizon=3)
    print(f"   Total Revenue: ${rolling_result['total_revenue']:.2f}")

    # Create comparison table
    create_comparison_table(full_result, rolling_result)

    # Plot comparison
    plot_comparison(full_result, rolling_result)

    # Save CSV
    save_comparison_csv(full_result, rolling_result)

    # Print summary
    diff = full_result["total_revenue"] - rolling_result["total_revenue"]
    pct = (diff / full_result["total_revenue"]) * 100
    winner = "Full Horizon" if diff >= 0 else "Rolling Horizon"

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Full Horizon Revenue:    ${full_result['total_revenue']:.2f}")
    print(f"Rolling Horizon Revenue: ${rolling_result['total_revenue']:.2f}")
    print(f"Revenue difference:      ${diff:.2f} ({pct:.2f}%)")
    print(f"Winner: {winner}")
    print("=" * 70)


if __name__ == "__main__":
    main()
