"""Hydrology methods package."""

from .scs_cn import (
    calculate_runoff,
    calculate_runoff_volume,
    calculate_S,
    calculate_Ia,
    adjust_cn_for_amc,
    AMCondition,
    SCSResult,
)
from .rational import (
    calculate_peak_discharge,
    calculate_time_of_concentration,
    calculate_runoff_coefficient,
    estimate_watershed_response,
    RationalResult,
)
from .time_area import (
    create_hydrograph_from_rainfall,
    create_triangular_time_area,
    route_hydrograph,
    TimeAreaResult,
)

__all__ = [
    "calculate_runoff",
    "calculate_runoff_volume",
    "calculate_S",
    "calculate_Ia",
    "adjust_cn_for_amc",
    "AMCondition",
    "SCSResult",
    "calculate_peak_discharge",
    "calculate_time_of_concentration",
    "calculate_runoff_coefficient",
    "estimate_watershed_response",
    "RationalResult",
    "create_hydrograph_from_rainfall",
    "create_triangular_time_area",
    "route_hydrograph",
    "TimeAreaResult",
]