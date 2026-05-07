"""Time-Area Method module for watershed routing and hydrograph generation.

This module implements the Time-Area Method for watershed routing,
which converts effective precipitation to a direct runoff hydrograph
using a time-area histogram representing watershed travel time distribution.

References:
    Chow, V.T., Maidment, D.R., Mays, L.W. (1988). Applied Hydrology
    USDA NRCS: National Engineering Handbook, Part 630 - Hydrology
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class TimeAreaResult:
    """Result container for Time-Area Method calculations."""

    time: List[float]  # minutes
    discharge: List[float]  # m³/s
    total_runoff_volume: float  # m³
    peak_discharge: float  # m³/s
    time_to_peak: float  # minutes


def create_triangular_time_area(
    time_of_concentration: float,
    num_subareas: int = 10,
) -> Tuple[List[float], List[float]]:
    """Create a triangular time-area histogram.

    Args:
        time_of_concentration: Time of concentration (minutes)
        num_subareas: Number of subareas for discretization

    Returns:
        Tuple of (times, areas) where areas sum to 1.0
    """
    if time_of_concentration <= 0:
        raise ValueError("Time of concentration must be positive")
    if num_subareas < 1:
        raise ValueError("Number of subareas must be at least 1")

    dt = time_of_concentration / num_subareas
    times = [i * dt for i in range(num_subareas + 1)]

    half_tc = time_of_concentration / 2
    areas = []
    for i in range(num_subareas + 1):
        t = i * dt
        if t <= half_tc:
            area = t / half_tc
        elif t <= time_of_concentration:
            area = (time_of_concentration - t) / half_tc
        else:
            area = 0.0
        areas.append(area)

    total = sum(areas)
    if total > 0:
        areas = [a / total for a in areas]

    return times, areas


def create_scs_dimensionless_uh(
    num_subareas: int = 10,
) -> Tuple[List[float], List[float]]:
    """Create SCS Dimensionless Unit Hydrograph.

    Args:
        num_subareas: Number of subareas for discretization

    Returns:
        Tuple of (dimensionless times, dimensionless ordinates)
    """
    if num_subareas < 1:
        raise ValueError("Number of subareas must be at least 1")

    times = []
    ordinates = []

    for i in range(num_subareas + 1):
        t_ratio = i / num_subareas * 3.0
        times.append(t_ratio)

        if t_ratio == 0:
            ordinate = 0.0
        elif t_ratio <= 1.0:
            ordinate = t_ratio
        else:
            tau = t_ratio
            if tau <= 3.0:
                ordinate = max(0.0, (2 - tau) ** 2 / (2 * tau))
            else:
                ordinate = 0.0

        ordinates.append(ordinate)

    total = sum(ordinates)
    if total > 0:
        ordinates = [o / total for o in ordinates]

    return times, ordinates


def route_hydrograph(
    effective_precipitation: float,
    time_of_concentration: float,
    area: float,
    time_area_histogram: Optional[Tuple[List[float], List[float]]] = None,
    num_subareas: int = 10,
) -> TimeAreaResult:
    """Route effective precipitation through watershed.

    Args:
        effective_precipitation: Effective precipitation (mm)
        time_of_concentration: Time of concentration (minutes)
        area: Watershed area (km²)
        time_area_histogram: Optional custom time-area histogram
        num_subareas: Number of subareas for discretization

    Returns:
        TimeAreaResult containing hydrograph and summary statistics
    """
    if effective_precipitation < 0:
        raise ValueError("Effective precipitation cannot be negative")
    if time_of_concentration <= 0:
        raise ValueError("Time of concentration must be positive")
    if area <= 0:
        raise ValueError("Area must be positive")

    if time_area_histogram is None:
        times, areas = create_triangular_time_area(time_of_concentration, num_subareas)
    else:
        times, areas = time_area_histogram

    total_volume_m3 = effective_precipitation / 1000.0 * area * 1e6

    n_steps = len(areas)
    if n_steps <= 1:
        return TimeAreaResult(
            time=[0.0],
            discharge=[0.0],
            total_runoff_volume=0.0,
            peak_discharge=0.0,
            time_to_peak=0.0,
        )

    dur = time_of_concentration / 2
    dt_min = dur / num_subareas
    dt_sec = dt_min * 60

    new_times = [i * dt_min for i in range(num_subareas + 1)]

    discharges = []
    for area_fraction in areas:
        vol_for_interval = total_volume_m3 * area_fraction
        q = vol_for_interval / dt_sec if dt_sec > 0 else 0
        discharges.append(q)

    if not discharges:
        discharges = [0.0]

    peak_dis = max(discharges) if discharges else 0.0
    peak_idx = discharges.index(peak_dis) if discharges else 0
    time_to_peak = new_times[peak_idx] if peak_idx < len(new_times) else 0.0

    return TimeAreaResult(
        time=new_times,
        discharge=discharges,
        total_runoff_volume=total_volume_m3,
        peak_discharge=peak_dis,
        time_to_peak=time_to_peak,
    )


def create_hydrograph_from_rainfall(
    precipitation: float,
    cn: float,
    area: float,
    time_of_concentration: float,
    amc: int = 2,
) -> TimeAreaResult:
    """Create hydrograph from rainfall using SCS-CN and Time-Area methods.

    Args:
        precipitation: Total precipitation (mm)
        cn: Curve Number
        area: Watershed area (km²)
        time_of_concentration: Time of concentration (minutes)
        amc: AMC condition (1, 2, or 3)

    Returns:
        TimeAreaResult containing complete hydrograph
    """
    from hydrology.scs_cn import calculate_runoff, AMCondition

    amc_enum = AMCondition(amc)
    scs_result = calculate_runoff(precipitation, cn, amc_enum)

    effective_precip = scs_result.runoff_depth

    times, areas = create_scs_dimensionless_uh()

    return route_hydrograph(
        effective_precipitation=effective_precip,
        time_of_concentration=time_of_concentration,
        area=area,
        time_area_histogram=(times, areas),
    )