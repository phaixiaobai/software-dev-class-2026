"""
Trade-off Analysis: Revenue vs Ecological Flow
Pareto Frontier using Weighted-Sum Method
"""

import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt

# Parameters (same as original)
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


def compute_storage(Q_releases):
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


def compute_eco_deficit(Q_releases):
    """Compute ecological deficit: sum of max(0, Q_eco - Q[t])."""
    deficit = np.sum(np.maximum(0, Q_eco - Q_releases))
    return deficit


def objective_combined(Q_releases, w):
    """Combined objective: f = -w * revenue + (1-w) * eco_deficit"""
    revenue = compute_revenue(Q_releases)
    eco_deficit = compute_eco_deficit(Q_releases)
    # Scale eco_deficit to comparable magnitude with revenue
    # Max possible eco deficit = 7 days * Q_eco = 70 m³/s
    # Scale factor: ~$1 per m³/s to make comparable to ~$90 revenue
    eco_scaled = eco_deficit * 1.0  # Keep as-is, weight will balance
    return -w * revenue + (1 - w) * eco_scaled


def create_constraints():
    """Storage bounds only - allow releases below Q_eco for trade-off analysis."""

    def storage_lower(x):
        return compute_storage(x)[1:] - V_min

    def storage_upper(x):
        return V_max - compute_storage(x)[1:]

    return [
        {"type": "ineq", "fun": storage_lower},
        {"type": "ineq", "fun": storage_upper},
    ]


def create_bounds():
    """Allow releases from 0 to Q_max to explore eco deficit trade-off."""
    return [(0, Q_max) for _ in range(7)]


def solve_for_weight(w):
    """Solve optimization for a given weight."""
    constraints = create_constraints()
    bounds = create_bounds()
    x0 = np.array([10.0] * 7)  # Start at ecological minimum

    result = minimize(
        fun=lambda x: objective_combined(x, w),
        x0=x0,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"ftol": 1e-10, "maxiter": 2000},
    )

    if result.success:
        revenue = compute_revenue(result.x)
        eco_deficit = compute_eco_deficit(result.x)
    else:
        revenue = None
        eco_deficit = None

    return result, revenue, eco_deficit


def run_pareto_analysis():
    """Run Pareto frontier analysis."""
    weights = np.arange(0.0, 1.05, 0.05)

    results = []
    for w in weights:
        result, revenue, eco_deficit = solve_for_weight(w)
        feasible = result.success and revenue is not None
        results.append(
            {
                "w": w,
                "revenue": revenue if feasible else None,
                "eco_deficit": eco_deficit if feasible else None,
                "feasible": feasible,
                "releases": result.x if feasible else None,
            }
        )

    return results


def print_summary_table(results):
    """Print summary table."""
    print("\n" + "=" * 70)
    print("PARETO FRONTIER ANALYSIS SUMMARY")
    print("=" * 70)
    print(
        f"{'Weight':<10} {'Revenue ($)':<15} {'Eco Deficit (m³/s)':<22} {'Feasible?':<10}"
    )
    print("-" * 70)

    for r in results:
        w = r["w"]
        rev = f"{r['revenue']:.2f}" if r["revenue"] is not None else "N/A"
        eco = f"{r['eco_deficit']:.2f}" if r["eco_deficit"] is not None else "N/A"
        feas = "Yes" if r["feasible"] else "No"
        print(f"{w:<10.2f} {rev:<15} {eco:<22} {feas:<10}")

    print("=" * 70)


def plot_pareto_frontier(results):
    """Plot the Pareto frontier."""
    feasible = [r for r in results if r["feasible"]]

    if not feasible:
        print("No feasible solutions to plot!")
        return

    # Sort by eco_deficit for proper line plot
    feasible_sorted = sorted(feasible, key=lambda x: x["eco_deficit"])

    eco_deficits = [r["eco_deficit"] for r in feasible_sorted]
    revenues = [r["revenue"] for r in feasible_sorted]

    # Find special points
    rev_point = next((r for r in feasible if r["w"] == 1.0), None)
    eco_point = next((r for r in feasible if r["w"] == 0.0), None)
    balanced = next(
        (r for r in feasible if abs(r["w"] - 0.5) < 0.01 and r["feasible"]), None
    )

    plt.figure(figsize=(10, 7))

    # Plot Pareto curve
    plt.plot(eco_deficits, revenues, "b-", linewidth=2, label="Pareto Frontier")
    plt.scatter(eco_deficits, revenues, c="blue", s=30, alpha=0.6)

    # Mark pure revenue (w=1.0) - red star
    if rev_point:
        plt.scatter(
            [rev_point["eco_deficit"]],
            [rev_point["revenue"]],
            c="red",
            marker="*",
            s=300,
            zorder=5,
            label="Pure Revenue (w=1.0)",
        )

    # Mark pure ecology (w=0.0) - green star
    if eco_point:
        plt.scatter(
            [eco_point["eco_deficit"]],
            [eco_point["revenue"]],
            c="green",
            marker="*",
            s=300,
            zorder=5,
            label="Pure Ecology (w=0.0)",
        )

    # Mark balanced (w=0.5) - blue diamond
    if balanced:
        plt.scatter(
            [balanced["eco_deficit"]],
            [balanced["revenue"]],
            c="blue",
            marker="D",
            s=200,
            zorder=5,
            label="Balanced (w=0.5)",
        )

    plt.xlabel("Ecological Deficit (m³/s total)", fontsize=12)
    plt.ylabel("Total Revenue ($)", fontsize=12)
    plt.title("Pareto Frontier: Revenue vs Ecological Flow", fontsize=14)
    plt.legend(loc="best")
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("tradeoff_analysis.png", dpi=150)
    plt.close()
    print("\nPlot saved to: tradeoff_analysis.png")


def analyze_results(results):
    """Analyze and answer key questions."""
    print("\n" + "=" * 70)
    print("ANALYSIS ANSWERS")
    print("=" * 70)

    feasible = [r for r in results if r["feasible"]]

    if not feasible:
        print("No feasible solutions found!")
        return

    # Find pure revenue (w=1.0)
    rev_point = next((r for r in feasible if r["w"] == 1.0), None)
    # Find pure ecology (w=0.0)
    eco_point = next((r for r in feasible if r["w"] == 0.0), None)
    # Find balanced (w=0.5)
    balanced = next((r for r in feasible if abs(r["w"] - 0.5) < 0.01), None)

    if rev_point and eco_point:
        max_revenue = rev_point["revenue"]
        min_revenue = eco_point["revenue"]

        print(f"\n1. Pure Revenue Point (w=1.0):")
        print(f"   - Revenue: ${max_revenue:.2f}")
        print(f"   - Eco Deficit: {rev_point['eco_deficit']:.2f} m³/s")

        print(f"\n2. Pure Ecology Point (w=0.0):")
        print(f"   - Revenue: ${min_revenue:.2f}")
        print(f"   - Eco Deficit: {eco_point['eco_deficit']:.2f} m³/s")

        print(f"\n3. Cost of achieving zero ecological deficit:")
        # Find solution with zero eco deficit
        zero_eco_solutions = [r for r in feasible if r["eco_deficit"] < 0.1]
        if zero_eco_solutions:
            zero_eco_max_rev = max(r["revenue"] for r in zero_eco_solutions)
            revenue_loss = max_revenue - zero_eco_max_rev
            print(f"   - Max revenue (any): ${max_revenue:.2f}")
            print(f"   - Max revenue with zero deficit: ${zero_eco_max_rev:.2f}")
            print(
                f"   - Revenue loss: ${revenue_loss:.2f} ({(revenue_loss / max_revenue) * 100:.1f}%)"
            )
        else:
            print("   - Cannot achieve zero deficit within constraints")

    # Find first weight where eco deficit reaches zero
    zero_deficit_solutions = [r for r in feasible if r["eco_deficit"] < 0.1]
    if zero_deficit_solutions:
        first_zero = min(zero_deficit_solutions, key=lambda x: x["w"])
        print(f"\n4. At what weight does ecological deficit first reach zero?")
        print(f"   - First zero deficit at w = {first_zero['w']:.2f}")
        print(f"   - Revenue at this point: ${first_zero['revenue']:.2f}")

    if balanced:
        print(f"\n5. Balanced point (w=0.5):")
        print(f"   - Revenue: ${balanced['revenue']:.2f}")
        print(f"   - Eco Deficit: {balanced['eco_deficit']:.2f} m³/s")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    results = run_pareto_analysis()
    print_summary_table(results)
    plot_pareto_frontier(results)
    analyze_results(results)
