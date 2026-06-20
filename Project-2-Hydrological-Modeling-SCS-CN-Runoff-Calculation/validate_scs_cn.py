"""SCS-CN Model Validation Script.

This script validates key physical constraints of the SCS-CN runoff model
and prints a structured PASS/FAIL report.
"""

import numpy as np
from scs_cn_runoff import calculate_runoff, calculate_S, calculate_Ia


def check_1_zero_rainfall():
    """Check: Zero rainfall produces zero runoff for all CN values."""
    cn_values = [60, 70, 80, 90, 100]
    all_passed = True
    failed_cases = []

    for cn in cn_values:
        Q = calculate_runoff(0, cn)
        if Q != 0:
            all_passed = False
            failed_cases.append((cn, Q))

    if all_passed:
        return True, "Zero rainfall (P=0) always produces Q=0"
    else:
        return False, f"Failed for CN={failed_cases[0][0]}: got Q={failed_cases[0][1]}"


def check_2_below_initial_abstraction():
    """Check: Precipitation below Ia produces zero runoff."""
    cn_values = [60, 70, 80, 90, 100]
    all_passed = True
    failed_cases = []

    for cn in cn_values:
        S = calculate_S(cn)
        Ia = calculate_Ia(S)
        P = Ia * 0.5  # Use 50% of Ia
        Q = calculate_runoff(P, cn)
        if Q != 0:
            all_passed = False
            failed_cases.append((cn, P, Ia, Q))

    if all_passed:
        return True, "Precipitation below Ia produces Q=0"
    else:
        case = failed_cases[0]
        return (
            False,
            f"Failed for CN={case[0]}: P={case[1]:.2f} < Ia={case[2]:.2f} but Q={case[3]:.2f}",
        )


def check_3_physical_constraint_Q_le_P():
    """Check: Runoff never exceeds precipitation (Q <= P)."""
    np.random.seed(42)
    n_samples = 1000
    P_samples = np.random.uniform(0, 200, n_samples)
    CN_samples = np.random.uniform(1, 100, n_samples)

    failed_cases = []
    for P, CN in zip(P_samples, CN_samples):
        Q = calculate_runoff(P, CN)
        if Q > P:
            failed_cases.append((P, CN, Q))

    if not failed_cases:
        return True, "Q <= P holds for all 1000 random samples"
    else:
        case = failed_cases[0]
        return (
            False,
            f"Violated: P={case[0]:.2f}, CN={case[1]:.2f}, Q={case[2]:.2f} > P",
        )


def check_4_monotonicity():
    """Check: Runoff increases as CN increases (with fixed P)."""
    P = 50
    previous_Q = None
    failed = None

    for cn in range(60, 101):
        Q = calculate_runoff(P, cn)
        if previous_Q is not None and Q < previous_Q:
            failed = (cn - 1, previous_Q, cn, Q)
            break
        previous_Q = Q

    if failed is None:
        return True, "Q increases monotonically as CN goes from 60 to 100"
    else:
        return (
            False,
            f"Non-monotonic: CN={failed[0]} gave Q={failed[1]:.2f}, CN={failed[2]} gave Q={failed[3]:.2f}",
        )


def check_5_known_reference():
    """Check: P=50mm, CN=80 produces Q between 13.5 and 14.1 mm."""
    Q = calculate_runoff(50, 80)
    if 13.5 <= Q <= 14.1:
        return True, f"P=50mm, CN=80: Q={Q:.2f} mm (within expected range)"
    else:
        return False, f"P=50mm, CN=80: Q={Q:.2f} mm (expected 13.5-14.1)"


def check_6_impervious_surface():
    """Check: CN=100 produces Q approximately equal to P."""
    test_precipitations = [100, 150, 200]
    all_passed = True
    failed_cases = []

    for P in test_precipitations:
        Q = calculate_runoff(P, 100)
        if abs(Q - P) > 1:
            all_passed = False
            failed_cases.append((P, Q))

    if all_passed:
        return True, "CN=100 behaves as impervious (Q ≈ P within 1mm)"
    else:
        case = failed_cases[0]
        return False, f"CN=100 not impervious: P={case[0]}, Q={case[1]:.2f}, diff > 1mm"


def run_all_checks():
    """Run all validation checks and print structured report."""
    checks = [
        ("Zero Rainfall", check_1_zero_rainfall),
        ("Below Initial Abstraction", check_2_below_initial_abstraction),
        ("Physical Constraint (Q <= P)", check_3_physical_constraint_Q_le_P),
        ("Monotonicity", check_4_monotonicity),
        ("Known Reference Value", check_5_known_reference),
        ("Impervious Surface Behavior", check_6_impervious_surface),
    ]

    passed_count = 0

    print("\n" + "=" * 60)
    print("SCS-CN MODEL VALIDATION REPORT")
    print("=" * 60 + "\n")

    for name, check_func in checks:
        passed, message = check_func()
        status = "[PASS]" if passed else "[FAIL]"
        symbol = "✓" if passed else "✗"
        print(f"{status} {symbol} {name}")
        print(f"      {message}\n")
        if passed:
            passed_count += 1

    print("=" * 60)
    print(f"{passed_count}/6 checks passed")
    print("=" * 60 + "\n")

    return passed_count


if __name__ == "__main__":
    run_all_checks()
