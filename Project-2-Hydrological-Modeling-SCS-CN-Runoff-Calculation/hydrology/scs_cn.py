"""SCS-CN (Soil Conservation Service Curve Number) method module.

This module implements the SCS-CN method for estimating direct runoff
from precipitation based on curve number and soil characteristics,
including Antecedent Moisture Condition (AMC) adjustments.

References:
    USDA NRCS: National Engineering Handbook, Part 630 - Hydrology
    SCS National Engineering Handbook
"""

from enum import IntEnum
from dataclasses import dataclass
from typing import Union


class AMCondition(IntEnum):
    """Antecedent Moisture Condition categories.

    AMC I: Dry - Minimum runoff potential (5-day antecedent dry)
    AMC II: Normal - Average conditions (standard CN reference)
    AMC III: Wet - Maximum runoff potential (5-day antecedent wet)
    """

    I = 1
    II = 2
    III = 3


@dataclass
class SCSResult:
    """Result container for SCS-CN method calculations."""

    runoff_depth: float  # mm
    potential_retention: float  # mm
    initial_abstraction: float  # mm
    cn_adjusted: float
    effective_precipitation: float  # mm


def adjust_cn_for_amc(cn: float, amc: AMCondition) -> float:
    """Adjust Curve Number based on Antecedent Moisture Condition.

    Args:
        cn: Standard CN value for AMC II (normal condition)
        amc: Antecedent Moisture Condition

    Returns:
        Adjusted CN value for specified AMC

    Examples:
        >>> adjust_cn_for_amc(70, AMCondition.I)
        56.7
        >>> adjust_cn_for_amc(70, AMCondition.II)
        70.0
        >>> adjust_cn_for_amc(70, AMCondition.III)
        91.9
    """
    if cn < 1 or cn > 100:
        raise ValueError(f"CN must be between 1 and 100, got {cn}")

    if amc == AMCondition.I:
        return (cn * 100) / (178 - 0.78 * cn)
    elif amc == AMCondition.III:
        return (cn * 100) / (254 - 2.54 * cn)
    return cn


def calculate_S(cn: float) -> float:
    """Calculate potential maximum retention S.

    The retention S represents the maximum amount of rainfall
    that can be held on the watershed without producing runoff.

    Args:
        cn: Curve Number (1-100)

    Returns:
        Potential maximum retention S in mm

    Raises:
        ValueError: If CN is not in range 1-100
    """
    if cn < 1 or cn > 100:
        raise ValueError(f"CN must be between 1 and 100, got {cn}")

    S = (25400.0 / cn) - 254.0
    return S


def calculate_Ia(S: float) -> float:
    """Calculate initial abstraction Ia.

    Initial abstraction includes surface storage, interception, and
    infiltration before runoff begins. Default Ia = 0.2 * S.

    Args:
        S: Potential maximum retention (mm)

    Returns:
        Initial abstraction Ia in mm

    Raises:
        ValueError: If S is negative
    """
    if S < 0:
        raise ValueError(f"S must be non-negative, got {S}")

    Ia = 0.2 * S
    return Ia


def calculate_runoff(
    P: Union[float, int],
    cn: float,
    amc: AMCondition = AMCondition.II,
) -> SCSResult:
    """Calculate direct runoff using SCS-CN method.

    The SCS-CN method is based on the water balance equation:
        P = Ia + Q + Fa

    Where:
        P: Precipitation (mm)
        Ia: Initial abstraction (mm)
        Q: Direct runoff (mm)
        Fa: Continuing abstraction (mm)

    The runoff is calculated using:
        Q = (P - Ia)^2 / (P - Ia + S)

    Args:
        P: Precipitation depth (mm)
        cn: Curve Number (1-100)
        amc: Antecedent Moisture Condition (default AMC II)

    Returns:
        SCSResult containing runoff and related values

    Raises:
        ValueError: If P is negative or CN is not in range 1-100
    """
    if P < 0:
        raise ValueError(f"Precipitation P must be non-negative, got {P}")
    if cn < 1 or cn > 100:
        raise ValueError(f"CN must be between 1 and 100, got {cn}")

    cn_adjusted = adjust_cn_for_amc(cn, amc)
    S = calculate_S(cn_adjusted)
    Ia = calculate_Ia(S)

    if P <= Ia:
        return SCSResult(
            runoff_depth=0.0,
            potential_retention=S,
            initial_abstraction=Ia,
            cn_adjusted=cn_adjusted,
            effective_precipitation=0.0,
        )

    Pe = P - Ia
    Q = (Pe * Pe) / (Pe + S)

    return SCSResult(
        runoff_depth=max(0.0, Q),
        potential_retention=S,
        initial_abstraction=Ia,
        cn_adjusted=cn_adjusted,
        effective_precipitation=Pe,
    )


def calculate_runoff_volume(
    P: float,
    cn: float,
    area: float,
    amc: AMCondition = AMCondition.II,
) -> float:
    """Calculate total runoff volume.

    Args:
        P: Precipitation depth (mm)
        cn: Curve Number
        area: Watershed area (km²)
        amc: Antecedent Moisture Condition

    Returns:
        Runoff volume (m³)
    """
    result = calculate_runoff(P, cn, amc)
    volume_m3 = result.runoff_depth / 1000.0 * area * 1e6
    return volume_m3