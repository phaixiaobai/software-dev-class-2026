"""Rational Method module for peak discharge estimation.

This module implements the Rational Method (Q = CIA) for estimating
peak discharge from watershed runoff.

References:
    Chow, V.T., Maidment, D.R., Mays, L.W. (1988). Applied Hydrology
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class RationalResult:
    """Result container for Rational Method calculations."""

    peak_discharge: float  # m³/s
    time_of_concentration: float  # min
    rainfall_intensity: float  # mm/hr
    runoff_coefficient: float
    area: float  # km²


def calculate_time_of_concentration(
    length: float,
    slope: float,
    method: str = "kerpy",
) -> float:
    """Calculate time of concentration using various formulas.

    Args:
        length: Maximum flow path length (m)
        slope: Average watershed slope (m/m)
        method: Formula method ('kerpy', 'scs', 'flight')

    Returns:
        Time of concentration (minutes)
    """
    if length <= 0 or slope <= 0:
        raise ValueError("Length and slope must be positive")

    if method == "kerpy":
        tc = 0.0195 * (length ** 0.77) * (slope ** -0.385)
    elif method == "scs":
        tc = (length ** 0.8) * ((1000 / (slope * 100)) + 9) ** 0.5
    elif method == "flight":
        v = (1.0 / 0.005) * (slope ** 0.5) * (1.0) ** (2.0 / 3.0)
        tc = length / v / 60.0 if v > 0 else 0
    else:
        tc = 0.0195 * (length ** 0.77) * (slope ** -0.385)

    return tc if tc > 0 else 0.1


def calculate_rainfall_intensity(
    rainfall_depth: float,
    duration: float,
) -> float:
    """Calculate average rainfall intensity.

    Args:
        rainfall_depth: Total rainfall depth (mm)
        duration: Storm duration (hours)

    Returns:
        Average rainfall intensity (mm/hr)
    """
    if duration <= 0:
        raise ValueError("Duration must be positive")
    return rainfall_depth / duration


def calculate_runoff_coefficient(
    land_use: str,
    soil_type: str,
    amc: int = 2,
) -> float:
    """Estimate runoff coefficient based on land use and soil type.

    Args:
        land_use: Land use category ('urban', 'agricultural', 'forest', 'commercial')
        soil_type: Soil type ('a', 'b', 'c', 'd' as per SCS)
        amc: AMC condition (1, 2, or 3)

    Returns:
        Runoff coefficient (0-1)
    """
    base_coeffs = {
        "urban": {"a": 0.30, "b": 0.40, "c": 0.50, "d": 0.60},
        "agricultural": {"a": 0.20, "b": 0.30, "c": 0.40, "d": 0.50},
        "forest": {"a": 0.10, "b": 0.15, "c": 0.20, "d": 0.25},
        "commercial": {"a": 0.50, "b": 0.70, "c": 0.80, "d": 0.90},
    }

    coeff = base_coeffs.get(land_use, {}).get(soil_type.lower(), 0.4)

    if amc == 3:
        coeff = min(1.0, coeff * 1.2)
    elif amc == 1:
        coeff = max(0.05, coeff * 0.8)

    return coeff


def calculate_peak_discharge(
    area: float,
    precipitation: float,
    rainfall_duration: float,
    runoff_coefficient: float,
    time_of_concentration: float,
) -> RationalResult:
    """Calculate peak discharge using the Rational Method.

    The Rational Method formula: Q = CIA
    Where:
        Q: Peak discharge (m³/s)
        C: Runoff coefficient
        I: Rainfall intensity (mm/hr)
        A: Watershed area (km² converted to ha)

    Args:
        area: Watershed area (km²)
        precipitation: Total precipitation depth (mm)
        rainfall_duration: Duration of design storm (hours)
        runoff_coefficient: Runoff coefficient (0-1)
        time_of_concentration: Time of concentration (minutes)

    Returns:
        RationalResult containing peak discharge and parameters
    """
    if area <= 0:
        raise ValueError("Area must be positive")
    if precipitation < 0:
        raise ValueError("Precipitation cannot be negative")
    if rainfall_duration <= 0:
        raise ValueError("Duration must be positive")
    if runoff_coefficient < 0 or runoff_coefficient > 1:
        raise ValueError("Coefficient must be between 0 and 1")
    if time_of_concentration <= 0:
        raise ValueError("Time of concentration must be positive")

    intensity = precipitation / rainfall_duration

    area_ha = area * 100
    q_cms = (runoff_coefficient * intensity * area_ha) / 360.0

    return RationalResult(
        peak_discharge=q_cms,
        time_of_concentration=time_of_concentration,
        rainfall_intensity=intensity,
        runoff_coefficient=runoff_coefficient,
        area=area,
    )


def estimate_watershed_response(
    precipitation: float,
    area: float,
    length: float,
    slope: float,
    land_use: str = "agricultural",
    soil_type: str = "b",
    amc: int = 2,
) -> RationalResult:
    """Estimate watershed response using Rational Method.

    Args:
        precipitation: Total precipitation (mm)
        area: Watershed area (km²)
        length: Maximum flow path (m)
        slope: Average slope (m/m)
        land_use: Land use category
        soil_type: Soil type (A, B, C, D)
        amc: AMC condition (1, 2, or 3)

    Returns:
        RationalResult with peak discharge estimate
    """
    tc = calculate_time_of_concentration(length, slope, method="kerpy")
    c = calculate_runoff_coefficient(land_use, soil_type, amc)
    duration = tc / 60.0

    return calculate_peak_discharge(
        area=area,
        precipitation=precipitation,
        rainfall_duration=duration,
        runoff_coefficient=c,
        time_of_concentration=tc,
    )