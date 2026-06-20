"""
Uncertainty Analysis for Reservoir Optimization
Monte Carlo simulation with 100 inflow scenarios
"""

import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt

# Base parameters
V0 = 500_000
V_min = 100_000
V_max = 1_000_000
Q_eco = 10
Q_max = 100
dt = 86400
base_inflow = np.array([15, 12, 10, 8, 12, 15, 18])
price = np.array([0.08, 0.08, 0.08, 0.08, 0.10, 0.12, 0.10])
eta = 0.85
g = 9.81
H = 50
POWER_CONV = eta * g * H * dt / 3_600_000


def generate_inflow_scenarios(base_inflow, n_scenarios=100, uncertainty=0.20):
    """
    Generate inflow scenarios with random uncertainty.

    Args:
        base_inflow: array of 7 base inflow values (m³/s)
        n_scenarios: number of scenarios to generate
        uncertainty: standard deviation as fraction of base (default 0.20 = ±20%)

    Returns:
        array of shape (n_scenarios, 7) with uncertain inflows
    """
    np.random.seed(42)

    n_days = len(base_inflow)
    std_dev = base_inflow * uncertainty

    scenarios = np.zeros((n_scenarios, n_days))
    for i in range(n_scenarios):
        random_shocks = np.random.normal(0, std_dev)
        scenarios[i] = base_inflow + random_shocks
        scenarios[i] = np.clip(scenarios[i], 0, None)

    return scenarios


def compute_storage(Q_releases, inflow):
    """Compute storage values V0 to V7."""
    n = len(Q_releases)
    storage = np.zeros(n + 1)
    storage[0] = V0
    for t in range(n):
        storage[t + 1] = storage[t] + (inflow[t] - Q_releases[t]) * dt
    return storage


def compute_revenue(Q_releases):
    """Compute total revenue in dollars."""
    power = Q_releases * POWER_CONV
    revenue = np.sum(power * price)
    return revenue


def objective(Q_releases, inflow):
    """Objective function for a given inflow scenario."""
    storage = compute_storage(Q_releases, inflow)
    if np.any(storage[1:] < V_min) or np.any(storage[1:] > V_max):
        return 1e10  # Penalty for constraint violation
    revenue = compute_revenue(Q_releases)
    return -revenue


def solve_single(inflow):
    """Solve optimization for a single scenario."""
    bounds = [(Q_eco, Q_max) for _ in range(7)]
    x0 = inflow.copy()

    result = minimize(
        fun=lambda x: objective(x, inflow),
        x0=x0,
        method="SLSQP",
        bounds=bounds,
        options={"ftol": 1e-10, "maxiter": 1000},
    )

    if result.success:
        return result.x, compute_revenue(result.x), compute_storage(result.x, inflow)
    else:
        return None, None, None


def optimize_under_uncertainty(scenarios):
    """
    Run optimization for each scenario.

    Args:
        scenarios: array of shape (n_scenarios, 7)

    Returns:
        releases: array (n_scenarios, 7)
        revenues: array (n_scenarios,)
        storages: array (n_scenarios, 8)
    """
    n_scenarios = scenarios.shape[0]
    releases = np.zeros((n_scenarios, 7))
    revenues = np.zeros(n_scenarios)
    storages = np.zeros((n_scenarios, 8))

    for i in range(n_scenarios):
        release, revenue, storage = solve_single(scenarios[i])
        if release is not None:
            releases[i] = release
            revenues[i] = revenue
            storages[i] = storage
        else:
            releases[i] = np.nan
            revenues[i] = np.nan
            storages[i] = np.nan

    valid_mask = ~np.isnan(revenues)
    print(f"Solvable scenarios: {np.sum(valid_mask)}/{n_scenarios}")

    return releases, revenues, storages


def compute_statistics(releases, revenues, storages):
    """Compute mean, 10th, 90th percentile statistics."""
    valid_releases = releases[~np.isnan(revenues)]
    valid_storages = storages[~np.isnan(revenues)]

    release_mean = np.mean(valid_releases, axis=0)
    release_p10 = np.percentile(valid_releases, 10, axis=0)
    release_p90 = np.percentile(valid_releases, 90, axis=0)

    storage_mean = np.mean(valid_storages, axis=0)
    storage_p10 = np.percentile(valid_storages, 10, axis=0)
    storage_p90 = np.percentile(valid_storages, 90, axis=0)

    revenues_valid = revenues[~np.isnan(revenues)]
    revenue_mean = np.mean(revenues_valid)
    revenue_std = np.std(revenues_valid)
    revenue_p10 = np.percentile(revenues_valid, 10)
    revenue_p90 = np.percentile(revenues_valid, 90)

    return {
        "release_mean": release_mean,
        "release_p10": release_p10,
        "release_p90": release_p90,
        "storage_mean": storage_mean,
        "storage_p10": storage_p10,
        "storage_p90": storage_p90,
        "revenue_mean": revenue_mean,
        "revenue_std": revenue_std,
        "revenue_p10": revenue_p10,
        "revenue_p90": revenue_p90,
        "revenues_valid": revenues_valid,
    }


def check_ecological_violations(releases):
    """Count scenarios with any release below Q_eco."""
    violations = np.sum(np.any(releases < Q_eco, axis=1))
    return violations


def plot_uncertainty_analysis(scenarios, storages, stats):
    """Create 3-subplot figure."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Subplot 1: Inflow scenarios
    ax1 = axes[0]
    for i in range(scenarios.shape[0]):
        ax1.plot(range(1, 8), scenarios[i], color="gray", alpha=0.1, linewidth=0.5)
    ax1.plot(range(1, 8), base_inflow, "b-", linewidth=2.5, label="Base Forecast")
    ax1.set_xlabel("Day")
    ax1.set_ylabel("Inflow (m³/s)")
    ax1.set_title("Inflow Forecast Scenarios (±20% uncertainty)")
    ax1.set_xticks(range(1, 8))
    ax1.legend()

    # Subplot 2: Storage trajectory
    ax2 = axes[1]
    days = np.arange(0, 8)
    valid_storages = storages[~np.isnan(storages).any(axis=1)]
    p10 = np.percentile(valid_storages, 10, axis=0)
    p90 = np.percentile(valid_storages, 90, axis=0)
    mean = np.mean(valid_storages, axis=0)

    ax2.fill_between(
        days, p10, p90, color="lightblue", alpha=0.5, label="10th–90th pct"
    )
    ax2.plot(days, mean, "b-", linewidth=2, label="Mean")
    ax2.axhline(
        y=V_min,
        color="red",
        linestyle="--",
        linewidth=1.5,
        label=f"V_min = {V_min / 1000:.0f}k",
    )
    ax2.axhline(
        y=V_max,
        color="red",
        linestyle="--",
        linewidth=1.5,
        label=f"V_max = {V_max / 1000:.0f}k",
    )
    ax2.set_xlabel("Day")
    ax2.set_ylabel("Storage (m³)")
    ax2.set_title("Storage Trajectory Under Uncertainty")
    ax2.set_xticks(days)
    ax2.legend(loc="upper right")
    ax2.set_ylim([0, V_max * 1.1])

    # Subplot 3: Revenue distribution
    ax3 = axes[2]
    ax3.hist(
        stats["revenues_valid"],
        bins=20,
        color="steelblue",
        edgecolor="black",
        alpha=0.7,
    )
    ax3.axvline(
        x=stats["revenue_mean"],
        color="red",
        linestyle="--",
        linewidth=2,
        label=f"Mean = ${stats['revenue_mean']:.2f}",
    )
    ax3.axvline(x=stats["revenue_p10"], color="orange", linestyle=":", linewidth=1.5)
    ax3.axvline(x=stats["revenue_p90"], color="orange", linestyle=":", linewidth=1.5)
    ax3.set_xlabel("Total Revenue ($)")
    ax3.set_ylabel("Frequency")
    ax3.set_title(f"Revenue Distribution (n={len(stats['revenues_valid'])} scenarios)")
    ax3.legend()

    plt.tight_layout()
    plt.savefig("uncertainty_analysis.png", dpi=150)
    plt.close()
    print("\nPlot saved to: uncertainty_analysis.png")


def print_summary(stats, violations, n_scenarios):
    """Print summary statistics."""
    print("\n" + "=" * 70)
    print("UNCERTAINTY ANALYSIS SUMMARY")
    print("=" * 70)
    print(f"Mean Revenue: ${stats['revenue_mean']:.2f}")
    print(f"Std Dev:      ${stats['revenue_std']:.2f}")
    print(f"10th pct:    ${stats['revenue_p10']:.2f}")
    print(f"90th pct:    ${stats['revenue_p90']:.2f}")
    print(f"\nScenarios with ecological violations: {violations}/{n_scenarios}")
    print("=" * 70)


def main():
    """Run full uncertainty analysis."""
    print("Generating 100 inflow scenarios with ±20% uncertainty...")
    scenarios = generate_inflow_scenarios(
        base_inflow, n_scenarios=100, uncertainty=0.20
    )

    print("\nRunning optimization for each scenario...")
    releases, revenues, storages = optimize_under_uncertainty(scenarios)

    print("\nComputing statistics across scenarios...")
    stats = compute_statistics(releases, revenues, storages)

    violations = check_ecological_violations(releases)

    print_summary(stats, violations, 100)
    plot_uncertainty_analysis(scenarios, storages, stats)


if __name__ == "__main__":
    main()
