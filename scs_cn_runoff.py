"""SCS-CN Runoff Model Implementation.

This module implements the Soil Conservation Service Curve Number (SCS-CN) method
for estimating direct runoff from rainfall events.
"""


def calculate_S(CN: float) -> float:
    """Calculate potential maximum retention (S) in mm.

    Parameters
    ----------
    CN : float
        Curve Number (dimensionless), must be in range 1-100.

    Returns
    -------
    float
        Potential maximum retention S in mm.

    Notes
    -----
    Formula: S = (25400 / CN) - 254
    This represents the maximum amount of precipitation that can be retained
    on the watershed surface without generating runoff.
    """
    return (25400 / CN) - 254


def calculate_Ia(S: float) -> float:
    """Calculate initial abstraction (Ia) in mm.

    Parameters
    ----------
    S : float
        Potential maximum retention in mm.

    Returns
    -------
    float
        Initial abstraction Ia in mm.

    Notes
    -----
    Formula: Ia = 0.2 * S
    Initial abstraction includes surface storage, interception, and infiltration
    before runoff begins.
    """
    return 0.2 * S


def calculate_runoff(P: float, CN: float) -> float:
    """Calculate direct runoff using the SCS-CN method.

    Parameters
    ----------
    P : float
        Precipitation (rainfall) amount in mm. Must be non-negative.
    CN : float
        Curve Number (dimensionless), must be in range 1-100.

    Returns
    -------
    float
        Direct runoff Q in mm.

    Raises
    ------
    ValueError
        If CN is outside the valid range 1-100.
        If P is negative.

    Notes
    -----
    The SCS-CN method calculates runoff as:
    1. If P <= Ia: Q = 0 (no runoff occurs)
    2. Otherwise: Q = (P - Ia)^2 / (P - Ia + S)

    Where:
    - S = potential maximum retention
    - Ia = initial abstraction (typically 0.2 * S)
    """
    # Validate CN range
    if CN < 1 or CN > 100:
        raise ValueError(f"CN must be in range 1-100, got {CN}")

    # Validate precipitation
    if P < 0:
        raise ValueError(f"P (precipitation) cannot be negative, got {P}")

    # Step 1: Calculate potential maximum retention
    S = calculate_S(CN)

    # Step 2: Calculate initial abstraction
    Ia = calculate_Ia(S)

    # Step 3: Apply runoff condition
    if P <= Ia:
        Q = 0.0
    else:
        # SCS-CN runoff formula
        numerator = (P - Ia) ** 2
        denominator = P - Ia + S
        Q = numerator / denominator

    # Step 4: Ensure runoff does not exceed precipitation
    if Q > P:
        Q = P

    return Q


if __name__ == "__main__":
    # Test example from requirements
    P_test = 50.0  # mm
    CN_test = 80

    Q_result = calculate_runoff(P_test, CN_test)

    print(f"SCS-CN Runoff Calculation")
    print(f"-" * 30)
    print(f"Precipitation (P): {P_test} mm")
    print(f"Curve Number (CN): {CN_test}")
    print(f"-" * 30)
    print(f"Calculated Runoff (Q): {Q_result:.2f} mm")
    print(f"-" * 30)

    # Verify against expected value
    expected = 13.8
    if abs(Q_result - expected) < 0.1:
        print(f"Verification: PASSED (expected ~{expected} mm)")
    else:
        print(f"Verification: FAILED (expected ~{expected} mm)")
