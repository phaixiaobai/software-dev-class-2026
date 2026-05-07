import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

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

C_max = 50.0
C_inflow = 5.0
C0 = 10.0
penalty_weight = 1000


def compute_storage(Q_releases):
    """Compute storage V0 to V7."""
    Q = np.asarray(Q_releases)
    storage = np.zeros(8)
    storage[0] = V0
    for t in range(7):
        storage[t + 1] = storage[t] + (inflow[t] - Q[t]) * dt
    return storage


def compute_concentration_direct(Q, storage):
    """Compute concentration directly given Q and storage arrays."""
    concentration = np.zeros(7)
    C_current = C0

    for t in range(7):
        V_current = storage[t]
        if V_current < 1000:
            concentration[t] = C_max * 2
            C_current = C_max * 2
            continue

        pollutant_mass_in = C_inflow * inflow[t] * dt
        concentration[t] = (C_current * V_current + pollutant_mass_in) / V_current
        C_current = concentration[t]

    return concentration


def compute_revenue(Q_releases):
    """Calculate total revenue."""
    Q = np.asarray(Q_releases)
    power_coeff = H * eta * g / 3_600_000
    return np.sum(Q * power_coeff * price * dt)


def compute_wq_penalty(Q_releases):
    """Compute penalty for water quality violations."""
    storage = compute_storage(Q_releases)
    concentration = compute_concentration_direct(Q_releases, storage)
    penalty = 0
    for t in range(7):
        if concentration[t] > C_max:
            penalty += (concentration[t] - C_max) ** 2 * penalty_weight
    return penalty


def solve_optimization(use_hard_constraint=False, use_penalty=False):
    """Solve optimization with optional water quality constraints."""
    n = 7

    def get_storage_constraint(t):
        def constraint(Q):
            storage = compute_storage(Q)
            return storage[t] - V_min
        return constraint

    def get_storage_upper_constraint(t):
        def constraint(Q):
            storage = compute_storage(Q)
            return V_max - storage[t]
        return constraint

    def get_wq_constraint(t):
        def constraint(Q):
            storage = compute_storage(Q)
            conc = compute_concentration_direct(Q, storage)
            return C_max - conc[t]
        return constraint

    def objective(Q):
        rev = compute_revenue(Q)
        if use_penalty:
            storage = compute_storage(Q)
            conc = compute_concentration_direct(Q, storage)
            pen = 0
            for t in range(n):
                if conc[t] > C_max:
                    pen += (conc[t] - C_max) ** 2 * penalty_weight
            return -(rev + pen)
        return -rev

    bounds = [(Q_eco, Q_max) for _ in range(n)]

    constraints = []
    for t in range(1, n + 1):
        constraints.append({'type': 'ineq', 'fun': get_storage_constraint(t)})
        constraints.append({'type': 'ineq', 'fun': get_storage_upper_constraint(t)})

    if use_hard_constraint:
        for t in range(n):
            constraints.append({'type': 'ineq', 'fun': get_wq_constraint(t)})

    x0 = inflow.copy()

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
    C_opt = compute_concentration_direct(Q_opt, V_opt)
    rev = compute_revenue(Q_opt)

    return Q_opt, V_opt, C_opt, rev


def run_scenarios():
    """Run all three scenarios."""
    print("Running Scenario A: No WQ constraint (baseline)...")
    Q_A, V_A, C_A, rev_A = solve_optimization(use_hard_constraint=False, use_penalty=False)

    print("Running Scenario B: Hard constraint C <= 50 mg/L...")
    Q_B, V_B, C_B, rev_B = solve_optimization(use_hard_constraint=True, use_penalty=False)

    print("Running Scenario C: Soft constraint via penalty...")
    Q_C, V_C, C_C, rev_C = solve_optimization(use_hard_constraint=False, use_penalty=True)

    return (Q_A, V_A, C_A, rev_A), (Q_B, V_B, C_B, rev_B), (Q_C, V_C, C_C, rev_C)


def print_summary(scenarios):
    """Print summary table."""
    scenario_names = ['A: Baseline', 'B: Hard Constraint', 'C: Soft Penalty']

    print("\n" + "=" * 80)
    print("SUMMARY TABLE")
    print("=" * 80)
    print(f"{'Scenario':<25} {'Revenue ($)':<15} {'Max Conc (mg/L)':<20} {'WQ Violations':<15}")
    print("-" * 80)

    for name, (Q, V, C, rev) in zip(scenario_names, scenarios):
        max_c = np.max(C)
        violations = np.sum(C > C_max)
        print(f"{name:<25} {rev:<15.2f} {max_c:<20.2f} {violations:<15}")

    print("=" * 80)

    print(f"\nScenario A (Baseline) Revenue:   ${scenarios[0][3]:.2f}")
    print(f"Scenario B (Hard Constraint):     ${scenarios[1][3]:.2f}")
    print(f"Scenario C (Soft Penalty):        ${scenarios[2][3]:.2f}")


def plot_comparison(scenarios):
    """Create 3-subplot comparison."""
    (Q_A, V_A, C_A, _), (Q_B, V_B, C_B, _), (Q_C, V_C, C_C, _) = scenarios

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    days = np.arange(1, 8)

    axes[0].bar(days - 0.25, Q_A, 0.25, label='A: Baseline', color='steelblue', alpha=0.8)
    axes[0].bar(days, Q_B, 0.25, label='B: Hard Constraint', color='coral', alpha=0.8)
    axes[0].bar(days + 0.25, Q_C, 0.25, label='C: Soft Penalty', color='green', alpha=0.8)
    axes[0].axhline(y=Q_eco, color='gray', linestyle='--', alpha=0.5, label='Q_eco')
    axes[0].set_xlabel('Day')
    axes[0].set_ylabel('Release (m³/s)')
    axes[0].set_title('Daily Releases')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(days, V_A[1:], 'o-', color='steelblue', linewidth=2, label='A: Baseline')
    axes[1].plot(days, V_B[1:], 's-', color='coral', linewidth=2, label='B: Hard Constraint')
    axes[1].plot(days, V_C[1:], '^-', color='green', linewidth=2, label='C: Soft Penalty')
    axes[1].axhline(y=V_min, color='gray', linestyle='--', alpha=0.5)
    axes[1].axhline(y=V_max, color='gray', linestyle='--', alpha=0.5)
    axes[1].set_xlabel('Day')
    axes[1].set_ylabel('Storage (m³)')
    axes[1].set_title('Storage Trajectory')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(days, C_A, 'o-', color='steelblue', linewidth=2, label='A: Baseline')
    axes[2].plot(days, C_B, 's-', color='coral', linewidth=2, label='B: Hard Constraint')
    axes[2].plot(days, C_C, '^-', color='green', linewidth=2, label='C: Soft Penalty')
    axes[2].axhline(y=C_max, color='red', linestyle='--', linewidth=2, label=f'C_max = {C_max}')
    axes[2].set_xlabel('Day')
    axes[2].set_ylabel('Concentration (mg/L)')
    axes[2].set_title('Pollutant Concentration')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)

    plt.suptitle('Water Quality Analysis: 3 Scenarios', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('/Users/pasorn/Desktop/Xian-Jiaotong/class/sofware-dev/Assignment-4-Projects/Project-3/water_quality_analysis.png', dpi=150)
    plt.close()
    print("\nPlot saved to: water_quality_analysis.png")


if __name__ == "__main__":
    scenarios = run_scenarios()
    print_summary(scenarios)
    plot_comparison(scenarios)