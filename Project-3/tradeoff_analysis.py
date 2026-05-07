import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
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
    """Compute storage V0 to V7 using mass balance."""
    Q = np.asarray(Q_releases)
    storage = np.zeros(8)
    storage[0] = V0
    for t in range(7):
        storage[t + 1] = storage[t] + (inflow[t] - Q[t]) * dt
    return storage


def compute_revenue(Q_releases):
    """Calculate total revenue in dollars."""
    Q = np.asarray(Q_releases)
    power_coeff = H * eta * g / 3_600_000
    daily_rev = Q * power_coeff * price * dt
    return np.sum(daily_rev)


def compute_eco_deficit(Q_releases):
    """Calculate ecological deficit: sum of max(0, Q_eco - Q[t])."""
    Q = np.asarray(Q_releases)
    return np.sum(np.maximum(0, Q_eco - Q))


def combined_objective(Q_releases, w):
    """
    Combined objective for weighted-sum method.
    f = -w * revenue + (1-w) * ecological_deficit
    """
    revenue = compute_revenue(Q_releases)
    eco_deficit = compute_eco_deficit(Q_releases)
    return -w * revenue + (1 - w) * eco_deficit


def solve_for_weight(w):
    """Solve optimization for a given weight w."""
    x0 = np.full(7, 10.0)

    bounds = [(0, Q_max) for _ in range(7)]

    storage_constr = []
    for t in range(1, 8):
        storage_constr.append(
            {'type': 'ineq', 'fun': lambda Q, ti=t: compute_storage(Q)[ti] - V_min}
        )
        storage_constr.append(
            {'type': 'ineq', 'fun': lambda Q, ti=t: V_max - compute_storage(Q)[ti]}
        )

    result = minimize(
        lambda Q: combined_objective(Q, w),
        x0,
        method='SLSQP',
        bounds=bounds,
        constraints=storage_constr,
        options={'maxiter': 1000, 'ftol': 1e-10}
    )

    if not result.success:
        return None

    return {
        'w': w,
        'revenue': compute_revenue(result.x),
        'eco_deficit': compute_eco_deficit(result.x),
        'releases': result.x.copy(),
        'storage': compute_storage(result.x)
    }


def run_pareto_analysis():
    """Run Pareto frontier analysis with varying weights."""
    weights = np.arange(0.0, 1.05, 0.05)
    results = []

    print("Running Pareto analysis...")
    for w in weights:
        res = solve_for_weight(w)
        if res is not None:
            results.append(res)
            feasible = "Yes" if res['eco_deficit'] < 1e-6 else "No"
            print(f"w={w:.2f}: Revenue=${res['revenue']:.2f}, Eco Deficit={res['eco_deficit']:.2f} m³/s, Feasible={feasible}")
        else:
            print(f"w={w:.2f}: Infeasible")

    return results


def plot_pareto_frontier(results):
    """Plot the Pareto frontier."""
    revenues = [r['revenue'] for r in results]
    deficits = [r['eco_deficit'] for r in results]

    fig, ax = plt.subplots(figsize=(10, 7))

    ax.plot(deficits, revenues, 'b-', linewidth=2, label='Pareto Frontier')
    ax.scatter(deficits, revenues, c='blue', s=50, zorder=5)

    w_1 = next((r for r in results if abs(r['w'] - 1.0) < 1e-6), None)
    w_0 = next((r for r in results if abs(r['w'] - 0.0) < 1e-6), None)
    w_05 = next((r for r in results if abs(r['w'] - 0.5) < 1e-6), None)

    if w_1:
        ax.scatter([w_1['eco_deficit']], [w_1['revenue']], c='red', marker='*', s=300, zorder=10, label=f'Pure Revenue (w=1.0)')
    if w_0:
        ax.scatter([w_0['eco_deficit']], [w_0['revenue']], c='green', marker='*', s=300, zorder=10, label=f'Pure Ecology (w=0.0)')
    if w_05:
        ax.scatter([w_05['eco_deficit']], [w_05['revenue']], c='blue', marker='D', s=200, zorder=10, label=f'Balanced (w=0.5)')

    ax.set_xlabel('Ecological Deficit (m³/s total)', fontsize=12)
    ax.set_ylabel('Total Revenue ($)', fontsize=12)
    ax.set_title('Pareto Frontier: Revenue vs Ecological Flow', fontsize=14)
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('/Users/pasorn/Desktop/Xian-Jiaotong/class/sofware-dev/Assignment-4-Projects/Project-3/tradeoff_analysis.png', dpi=150)
    plt.close()
    print("\nPlot saved to: tradeoff_analysis.png")


def print_summary_table(results):
    """Print summary table of all results."""
    print("\n" + "=" * 70)
    print("SUMMARY TABLE: Pareto Frontier Analysis")
    print("=" * 70)
    print(f"{'Weight':<10} {'Revenue ($)':<15} {'Eco Deficit (m³/s)':<22} {'Feasible?':<10}")
    print("-" * 70)

    for r in results:
        feasible = "Yes" if r['eco_deficit'] < 1e-6 else "No"
        print(f"{r['w']:<10.2f} {r['revenue']:<15.2f} {r['eco_deficit']:<22.2f} {feasible:<10}")

    print("=" * 70)


def analyze_results(results):
    """Analyze results and answer key questions."""
    print("\n" + "=" * 70)
    print("ANALYSIS")
    print("=" * 70)

    pure_revenue = next((r for r in results if abs(r['w'] - 1.0) < 1e-6), None)
    pure_ecology = next((r for r in results if abs(r['w'] - 0.0) < 1e-6), None)

    if pure_revenue and pure_ecology:
        revenue_at_pure_eco = pure_ecology['revenue']
        revenue_at_pure_rev = pure_revenue['revenue']

        cost_of_zero_deficit = revenue_at_pure_rev - revenue_at_pure_eco

        print(f"\nQ1: What is the cost (revenue loss) of achieving zero ecological deficit?")
        print(f"   Revenue at pure ecology (w=0.0): ${revenue_at_pure_eco:.2f}")
        print(f"   Revenue at pure revenue (w=1.0): ${revenue_at_pure_rev:.2f}")
        print(f"   Cost of zero deficit: ${cost_of_zero_deficit:.2f}")

    zero_deficit_weight = None
    for r in results:
        if r['eco_deficit'] < 1e-6:
            zero_deficit_weight = r['w']
            break

    print(f"\nQ2: At what weight does ecological deficit first reach zero?")
    print(f"   First weight with zero deficit: w = {zero_deficit_weight:.2f}")

    balanced = next((r for r in results if abs(r['w'] - 0.5) < 1e-6), None)
    if balanced:
        print(f"\nBalanced solution (w=0.5):")
        print(f"   Revenue: ${balanced['revenue']:.2f}")
        print(f"   Eco Deficit: {balanced['eco_deficit']:.2f} m³/s")
        print(f"   Releases: {balanced['releases'].round(2)}")


if __name__ == "__main__":
    results = run_pareto_analysis()
    print_summary_table(results)
    plot_pareto_frontier(results)
    analyze_results(results)