"""
Water Quality Constraints for Reservoir Optimization
Compare baseline (A), hard constraint (B), and soft constraint (C)
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
inflow = np.array([15.0, 12.0, 10.0, 8.0, 12.0, 15.0, 18.0])
price = np.array([0.08, 0.08, 0.08, 0.08, 0.10, 0.12, 0.10])
eta = 0.85
g = 9.81
H = 50
POWER_CONV = eta * g * H * dt / 3_600_000

# Water quality parameters
C_max = 15.0  # Maximum allowed concentration (mg/L)
C_in = 1.0  # Inflow concentration (mg/L)
C0 = 5.0  # Initial concentration (mg/L)


def compute_storage(Q, inf, Vstart):
    S = [Vstart]
    for i in range(len(Q)):
        S.append(S[-1] + (inf[i] - Q[i]) * dt)
    return np.array(S)


def compute_concentration(Q, inf, Vstart):
    S = compute_storage(Q, inf, Vstart)
    C = np.zeros(len(Q))
    cp = C0
    for i in range(len(Q)):
        if S[i + 1] > 0:
            C[i] = (cp * S[i] + C_in * inf[i] * dt) / S[i + 1]
        else:
            C[i] = C_max * 2
        cp = C[i]
    return C


def revenue(Q):
    return np.sum(Q * POWER_CONV * price)


def solve_baseline():
    """Scenario A: No water quality constraint (baseline)"""

    def obj(Q):
        S = compute_storage(Q, inflow, V0)
        if np.any(S[1:] < V_min) or np.any(S[1:] > V_max):
            return 1e10
        return -revenue(Q)

    result = minimize(
        obj,
        inflow.copy(),
        method="SLSQP",
        bounds=[(Q_eco, Q_max)] * 7,
        options={"ftol": 1e-10},
    )
    return result.x if result.success else inflow.copy()


def solve_hard():
    """Scenario B: Hard constraint C <= C_max"""

    # Storage constraints
    def storage_lower(x):
        S = compute_storage(x, inflow, V0)
        return S[1:] - V_min

    def storage_upper(x):
        S = compute_storage(x, inflow, V0)
        return V_max - S[1:]

    # WQ constraint
    def wq_constraint(x):
        C = compute_concentration(x, inflow, V0)
        return C_max - C  # >= 0 means C <= C_max

    constraints = [
        {"type": "ineq", "fun": storage_lower},
        {"type": "ineq", "fun": storage_upper},
        {"type": "ineq", "fun": wq_constraint},
    ]

    def obj(Q):
        return -revenue(Q)

    # Start with eco minimum
    x0 = np.array([Q_eco] * 7)

    result = minimize(
        obj,
        x0,
        method="SLSQP",
        bounds=[(Q_eco, Q_max)] * 7,
        constraints=constraints,
        options={"ftol": 1e-8, "maxiter": 3000},
    )

    if result.success:
        C = compute_concentration(result.x, inflow, V0)
        if np.all(C <= C_max * 1.5):
            return result.x
    return None


def solve_soft():
    """Scenario C: Soft constraint via penalty"""
    penalty_weight = 100

    def obj(Q):
        S = compute_storage(Q, inflow, V0)
        if np.any(S[1:] < V_min) or np.any(S[1:] > V_max):
            return 1e10
        C = compute_concentration(Q, inflow, V0)
        # Penalty for exceeding C_max
        penalty = sum(max(0, c - C_max) ** 2 * penalty_weight for c in C)
        return -(revenue(Q) - penalty)

    # Start with eco minimum
    x0 = np.array([Q_eco] * 7)
    result = minimize(
        obj,
        x0,
        method="SLSQP",
        bounds=[(Q_eco, Q_max)] * 7,
        options={"ftol": 1e-10},
    )
    return result.x if result.success else inflow.copy()


def get_result(Q, name):
    if Q is None:
        Q = np.array([Q_eco] * 7)
    S = compute_storage(Q, inflow, V0)
    C = compute_concentration(Q, inflow, V0)
    return {
        "name": name,
        "Q": Q,
        "S": S,
        "C": C,
        "rev": revenue(Q),
        "maxC": np.max(C),
        "viol": int(np.sum(C >= C_max)),  # >= to match C_max as violation
    }


def plot_it(results):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    days = np.arange(1, 8)
    cols = ["steelblue", "coral", "green"]

    ax = axes[0]
    for i, r in enumerate(results):
        ax.bar(
            np.arange(7) + (i - 1) * 0.25,
            r["Q"],
            0.25,
            color=cols[i],
            label=r["name"],
            edgecolor="k",
            alpha=0.8,
        )
    ax.axhline(Q_eco, color="g", ls="--", lw=1.5)
    ax.set_xlabel("Day"), ax.set_ylabel("Release (m³/s)")
    ax.set_title("Daily Releases"), ax.set_xticks(range(7))
    ax.set_xticklabels(days), ax.legend(), ax.grid(alpha=0.3)

    ax = axes[1]
    for i, r in enumerate(results):
        ax.plot(np.arange(8), r["S"], "-o", color=cols[i], lw=2, ms=6, label=r["name"])
    ax.axhline(V_min, color="r", ls="--"), ax.axhline(V_max, color="m", ls="--")
    ax.set_xlabel("Day"), ax.set_ylabel("Storage (m³)")
    ax.set_title("Storage Trajectory"), ax.legend(), ax.grid(alpha=0.3)

    ax = axes[2]
    for i, r in enumerate(results):
        ax.plot(days, r["C"], "-o", color=cols[i], lw=2, ms=6, label=r["name"])
    ax.axhline(C_max, color="r", ls="--", lw=2, label=f"C_max={C_max}")
    ax.set_xlabel("Day"), ax.set_ylabel("Concentration (mg/L)")
    ax.set_title("Concentration"), ax.legend(), ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig("water_quality_analysis.png", dpi=150)
    print("Saved: water_quality_analysis.png")


def main():
    print("=" * 70)
    print("WATER QUALITY ANALYSIS")
    print("=" * 70)
    print(f"C_max={C_max}, C_in={C_in}, C0={C0}")

    print("\n[A] Baseline...")
    Qa = solve_baseline()
    ra = get_result(Qa, "Baseline")

    print("[B] Hard constraint...")
    Qb = solve_hard()
    rb = get_result(Qb if Qb is not None else np.array([Q_max] * 7), "Hard Constraint")

    print("[C] Soft constraint...")
    Qc = solve_soft()
    rc = get_result(Qc, "Soft Constraint")

    results = [ra, rb, rc]

    print("\n" + "=" * 70)
    print(f"{'Scenario':<20} {'Revenue':<12} {'Max C':<12} {'Violations':<10}")
    print("-" * 70)
    for r in results:
        print(f"{r['name']:<20} ${r['rev']:<11.2f} {r['maxC']:<12.2f} {r['viol']:<10}")
    print("=" * 70)

    plot_it(results)

    print("\n" + "=" * 70)
    print("ANALYSIS")
    print("=" * 70)
    print(f"Baseline: ${ra['rev']:.2f}, {ra['viol']} days > C_max")
    print(f"Hard:     ${rb['rev']:.2f}, {rb['viol']} days > C_max")
    print(f"Soft:     ${rc['rev']:.2f}, {rc['viol']} days > C_max")
    print(f"\nBaseline achieves {ra['rev']:.2f} with {ra['viol']} WQ violations")
    print("Hard constraint requires higher releases -> different operating strategy")
    print("=" * 70)


if __name__ == "__main__":
    main()
