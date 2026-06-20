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

inflow_full = np.array([15, 12, 10, 8, 12, 15, 18])
price_full = np.array([0.08, 0.08, 0.08, 0.08, 0.10, 0.12, 0.10])

eta = 0.85
g = 9.81
H = 50


def pad_arrays(arr, horizon):
    """Pad array to horizon length by repeating last value."""
    if len(arr) < horizon:
        padded = np.concatenate([arr, np.full(horizon - len(arr), arr[-1])])
        return padded
    return arr[:horizon]


def solve_window(inflow_window, price_window, V_start):
    """Solve optimization for a single window."""
    n = len(inflow_window)

    def compute_storage(Q):
        V = np.zeros(n + 1)
        V[0] = V_start
        for t in range(n):
            V[t + 1] = V[t] + (inflow_window[t] - Q[t]) * dt
        return V

    def objective(Q):
        power_coeff = H * eta * g / 3_600_000
        revenue = np.sum(Q * power_coeff * price_window * dt)
        return -revenue

    bounds = [(Q_eco, Q_max) for _ in range(n)]

    constraints = []
    for t in range(1, n + 1):
        constraints.append(
            {'type': 'ineq', 'fun': lambda Q, ti=t: compute_storage(Q)[ti] - V_min}
        )
        constraints.append(
            {'type': 'ineq', 'fun': lambda Q, ti=t: V_max - compute_storage(Q)[ti]}
        )

    x0 = np.full(n, Q_eco)

    result = minimize(
        objective,
        x0,
        method='SLSQP',
        bounds=bounds,
        constraints=constraints,
        options={'maxiter': 1000, 'ftol': 1e-10}
    )

    return result.x, compute_storage(result.x)


def full_horizon_optimize():
    """Solve full 7-day horizon at once."""
    n = 7

    def compute_storage(Q):
        V = np.zeros(n + 1)
        V[0] = V0
        for t in range(n):
            V[t + 1] = V[t] + (inflow_full[t] - Q[t]) * dt
        return V

    def objective(Q):
        power_coeff = H * eta * g / 3_600_000
        revenue = np.sum(Q * power_coeff * price_full * dt)
        return -revenue

    bounds = [(Q_eco, Q_max) for _ in range(n)]

    constraints = []
    for t in range(1, n + 1):
        constraints.append(
            {'type': 'ineq', 'fun': lambda Q, ti=t: compute_storage(Q)[ti] - V_min}
        )
        constraints.append(
            {'type': 'ineq', 'fun': lambda Q, ti=t: V_max - compute_storage(Q)[ti]}
        )

    x0 = inflow_full.copy()

    result = minimize(
        objective,
        x0,
        method='SLSQP',
        bounds=bounds,
        constraints=constraints,
        options={'maxiter': 1000, 'ftol': 1e-10}
    )

    Q_opt = result.x
    V_opt = compute_storage(Q_opt)

    power_coeff = H * eta * g / 3_600_000
    revenue = np.sum(Q_opt * power_coeff * price_full * dt)

    return Q_opt, V_opt, revenue


def rolling_horizon_optimize(horizon=3):
    """Rolling horizon (MPC) optimization."""
    n = 7
    releases = []
    storages = []
    revenues = []

    V_current = V0

    for t in range(n):
        inflow_window = pad_arrays(inflow_full[t:], horizon)
        price_window = pad_arrays(price_full[t:], horizon)

        Q_window, V_window = solve_window(inflow_window, price_window, V_current)

        Q_execute = Q_window[0]
        releases.append(Q_execute)

        V_current = V_current + (inflow_full[t] - Q_execute) * dt

        if V_current > V_max:
            V_current = V_max
        if V_current < V_min:
            V_current = V_min

        storages.append(V_current)

        power_coeff = H * eta * g / 3_600_000
        daily_rev = Q_execute * power_coeff * price_full[t] * dt
        revenues.append(daily_rev)

    total_revenue = np.sum(revenues)

    return np.array(releases), np.array(storages), np.array(revenues), total_revenue


def compare_results():
    """Compare full horizon vs rolling horizon."""
    print("Running Full Horizon Optimization...")
    Q_full, V_full, rev_full = full_horizon_optimize()

    print("Running Rolling Horizon Optimization (horizon=3)...")
    Q_rolling, V_rolling, _, rev_rolling = rolling_horizon_optimize(horizon=3)

    print("\n" + "=" * 90)
    print("COMPARISON TABLE: Full Horizon vs Rolling Horizon")
    print("=" * 90)
    print(f"{'Day':<5} {'Inflow':<8} {'Rel_Full':<10} {'Rel_Roll':<10} {'Sto_Full':<12} {'Sto_Roll':<12}")
    print("-" * 90)

    for i in range(7):
        print(f"{i+1:<5} {inflow_full[i]:<8} {Q_full[i]:<10.2f} {Q_rolling[i]:<10.2f} {V_full[i+1]:<12.0f} {V_rolling[i]:<12.0f}")

    print("=" * 90)

    diff = rev_full - rev_rolling
    diff_pct = (diff / rev_full) * 100

    winner = "Full Horizon" if rev_full > rev_rolling else "Rolling Horizon"

    print(f"\nFull Horizon Revenue:    ${rev_full:.2f}")
    print(f"Rolling Horizon Revenue: ${rev_rolling:.2f}")
    print(f"Revenue difference:      ${abs(diff):.2f} ({abs(diff_pct):.2f}%)")
    print(f"Winner: {winner}")

    return Q_full, V_full, Q_rolling, V_rolling, rev_full, rev_rolling


def plot_comparison(Q_full, V_full, Q_rolling, V_rolling):
    """Create side-by-side comparison plots."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    days = np.arange(1, 8)
    width = 0.35

    ax1.bar(days - width/2, Q_full, width, label='Full Horizon', color='steelblue', alpha=0.8)
    ax1.bar(days + width/2, Q_rolling, width, label='Rolling Horizon', color='coral', alpha=0.8)
    ax1.axhline(y=Q_eco, color='green', linestyle='--', label='Q_eco', alpha=0.7)
    ax1.axhline(y=Q_max, color='red', linestyle='--', label='Q_max', alpha=0.7)
    ax1.set_xlabel('Day')
    ax1.set_ylabel('Release (m³/s)')
    ax1.set_title('Daily Releases Comparison')
    ax1.set_xticks(days)
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2.plot(days, V_full[1:], 'o-', color='steelblue', linewidth=2, markersize=8, label='Full Horizon')
    ax2.plot(days, V_rolling, 's-', color='coral', linewidth=2, markersize=8, label='Rolling Horizon')
    ax2.axhline(y=V_min, color='green', linestyle='--', label='V_min', alpha=0.7)
    ax2.axhline(y=V_max, color='red', linestyle='--', label='V_max', alpha=0.7)
    ax2.set_xlabel('Day')
    ax2.set_ylabel('Storage (m³)')
    ax2.set_title('Storage Trajectory Comparison')
    ax2.set_xticks(days)
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.suptitle('Full Horizon vs Rolling Horizon', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('/Users/pasorn/Desktop/Xian-Jiaotong/class/sofware-dev/Assignment-4-Projects/Project-3/rolling_horizon_comparison.png', dpi=150)
    plt.close()
    print("\nPlot saved to: rolling_horizon_comparison.png")


if __name__ == "__main__":
    Q_full, V_full, Q_rolling, V_rolling, rev_full, rev_rolling = compare_results()
    plot_comparison(Q_full, V_full, Q_rolling, V_rolling)