"""Main script for hydrology methods comparison and analysis.

This script demonstrates and compares three methods for estimating
watershed runoff: SCS-CN, Rational, and Time-Area methods.

Usage:
    python main.py

Author: Hydrology Software Development Course
"""

import sys
import argparse
from typing import Optional

from hydrology.scs_cn import (
    calculate_runoff,
    calculate_runoff_volume,
    adjust_cn_for_amc,
    AMCondition,
)
from hydrology.rational import (
    calculate_peak_discharge,
    calculate_time_of_concentration,
    calculate_runoff_coefficient,
    estimate_watershed_response,
)
from hydrology.time_area import (
    create_hydrograph_from_rainfall,
    create_triangular_time_area,
    route_hydrograph,
)
from visualization.interactive_plot import (
    HydrographPlotter,
    plot_hydrograph_comparison,
    create_summary_table,
)


DEFAULT_PARAMS = {
    "precipitation": 50.0,
    "cn": 70.0,
    "area": 10.0,
    "length": 1000.0,
    "slope": 0.01,
    "amc": 2,
}


def compare_methods(
    precipitation: float = DEFAULT_PARAMS["precipitation"],
    cn: float = DEFAULT_PARAMS["cn"],
    area: float = DEFAULT_PARAMS["area"],
    length: float = DEFAULT_PARAMS["length"],
    slope: float = DEFAULT_PARAMS["slope"],
    amc: int = DEFAULT_PARAMS["amc"],
) -> dict:
    """Compare all three hydrology methods for a watershed.

    Args:
        precipitation: Precipitation depth (mm)
        cn: Curve Number
        area: Watershed area (km²)
        length: Flow path length (m)
        slope: Watershed slope (m/m)
        amc: AMC condition (1, 2, or 3)

    Returns:
        Dictionary containing results from all methods
    """
    print("\n" + "=" * 70)
    print("HYDROLOGY METHODS COMPARISON")
    print("=" * 70)
    print(f"\nInput Parameters:")
    print(f"  Precipitation: {precipitation} mm")
    print(f"  Curve Number: {cn}")
    print(f"  Watershed Area: {area} km²")
    print(f"  Flow Length: {length} m")
    print(f"  Slope: {slope}")
    print(f"  AMC Condition: {amc}")

    amc_enum = AMCondition(amc)
    print(f"\n{'=' * 70}")
    print("1. SCS-CN METHOD")
    print("=" * 70)

    cn_i = adjust_cn_for_amc(cn, AMCondition.I)
    cn_ii = adjust_cn_for_amc(cn, AMCondition.II)
    cn_iii = adjust_cn_for_amc(cn, AMCondition.III)

    print(f"\nCN Adjustment for AMC:")
    print(f"  AMC I: {cn_i:.1f}")
    print(f"  AMC II: {cn_ii:.1f}")
    print(f"  AMC III: {cn_iii:.1f}")

    scs_result = calculate_runoff(precipitation, cn, amc_enum)
    scs_volume = calculate_runoff_volume(precipitation, cn, area, amc_enum)

    print(f"\nSCS-CN Results:")
    print(f"  Runoff Depth: {scs_result.runoff_depth:.2f} mm")
    print(f"  Potential Retention (S): {scs_result.potential_retention:.2f} mm")
    print(f"  Initial Abstraction (Ia): {scs_result.initial_abstraction:.2f} mm")
    print(f"  Effective Precipitation: {scs_result.effective_precipitation:.2f} mm")
    print(f"  Runoff Volume: {scs_volume:,.0f} m³")

    tc = calculate_time_of_concentration(length, slope, method="kerpy")
    c = calculate_runoff_coefficient("agricultural", "b", amc)
    duration = tc / 60

    print(f"\n{'=' * 70}")
    print("2. RATIONAL METHOD")
    print("=" * 70)
    print(f"\nDerived Parameters:")
    print(f"  Time of Concentration (Tc): {tc:.2f} min")
    print(f"  Runoff Coefficient (C): {c:.3f}")
    print(f"  Rainfall Duration: {duration:.2f} hr")

    rational_result = calculate_peak_discharge(
        area=area,
        precipitation=precipitation,
        rainfall_duration=duration,
        runoff_coefficient=c,
        time_of_concentration=tc,
    )

    print(f"\nRational Method Results:")
    print(f"  Rainfall Intensity: {rational_result.rainfall_intensity:.2f} mm/hr")
    print(f"  Peak Discharge: {rational_result.peak_discharge:.2f} m³/s")

    print(f"\n{'=' * 70}")
    print("3. TIME-AREA METHOD")
    print("=" * 70)

    time_area_result = create_hydrograph_from_rainfall(
        precipitation=precipitation,
        cn=cn,
        area=area,
        time_of_concentration=tc,
        amc=amc,
    )

    print(f"\nTime-Area Method Results:")
    print(f"  Peak Discharge: {time_area_result.peak_discharge:.2f} m³/s")
    print(f"  Time to Peak: {time_area_result.time_to_peak:.2f} min")
    print(f"  Total Volume: {time_area_result.total_runoff_volume:,.0f} m³")

    print(f"\n{'=' * 70}")
    print("COMPARISON SUMMARY")
    print("=" * 70)

    print(f"\n{'Method':<15} {'Runoff/Peak Q':<20} {'Unit':<15}")
    print("-" * 50)
    print(f"{'SCS-CN':<15} {scs_result.runoff_depth:<20.2f} {'mm':<15}")
    print(f"{'Rational':<15} {rational_result.peak_discharge:<20.2f} {'m³/s':<15}")
    print(f"{'Time-Area':<15} {time_area_result.peak_discharge:<20.2f} {'m³/s':<15}")
    print("=" * 70)

    return {
        "scs": scs_result,
        "rational": rational_result,
        "time_area": time_area_result,
        "cn_adjustments": {
            "I": cn_i,
            "II": cn_ii,
            "III": cn_iii,
        },
    }


def generate_static_plot(
    precipitation: float = DEFAULT_PARAMS["precipitation"],
    cn: float = DEFAULT_PARAMS["cn"],
    area: float = DEFAULT_PARAMS["area"],
    length: float = DEFAULT_PARAMS["length"],
    slope: float = DEFAULT_PARAMS["slope"],
    amc: int = DEFAULT_PARAMS["amc"],
    save_path: Optional[str] = None,
) -> None:
    """Generate static comparison plot."""
    tc = calculate_time_of_concentration(length, slope, method="kerpy")

    scs, rational, ta = (
        calculate_runoff(precipitation, cn, AMCondition(amc)),
        estimate_watershed_response(
            precipitation=precipitation,
            area=area,
            length=length,
            slope=slope,
            amc=amc,
        ),
        create_hydrograph_from_rainfall(
            precipitation=precipitation,
            cn=cn,
            area=area,
            time_of_concentration=tc,
            amc=amc,
        ),
    )

    plot_title = f"Hydrograph Comparison: P={precipitation}mm, CN={cn}, Area={area}km²"

    plot_hydrograph_comparison(scs, rational, ta, title=plot_title, save_path=save_path)


def main() -> int:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Compare hydrology methods for watershed runoff estimation"
    )

    parser.add_argument(
        "-p", "--precipitation",
        type=float,
        default=DEFAULT_PARAMS["precipitation"],
        help="Precipitation depth (mm)",
    )
    parser.add_argument(
        "-c", "--cn",
        type=float,
        default=DEFAULT_PARAMS["cn"],
        help="Curve Number",
    )
    parser.add_argument(
        "-a", "--area",
        type=float,
        default=DEFAULT_PARAMS["area"],
        help="Watershed area (km²)",
    )
    parser.add_argument(
        "-l", "--length",
        type=float,
        default=DEFAULT_PARAMS["length"],
        help="Flow path length (m)",
    )
    parser.add_argument(
        "-s", "--slope",
        type=float,
        default=DEFAULT_PARAMS["slope"],
        help="Watershed slope (m/m)",
    )
    parser.add_argument(
        "--amc",
        type=int,
        default=DEFAULT_PARAMS["amc"],
        choices=[1, 2, 3],
        help="AMC condition (1=Dry, 2=Normal, 3=Wet)",
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Generate comparison plots",
    )
    parser.add_argument(
        "--save-plot",
        type=str,
        help="Path to save comparison plot",
    )

    args = parser.parse_args()

    try:
        results = compare_methods(
            precipitation=args.precipitation,
            cn=args.cn,
            area=args.area,
            length=args.length,
            slope=args.slope,
            amc=args.amc,
        )

        if args.plot or args.save_plot:
            generate_static_plot(
                precipitation=args.precipitation,
                cn=args.cn,
                area=args.area,
                length=args.length,
                slope=args.slope,
                amc=args.amc,
                save_path=args.save_plot,
            )

        print("\nDone!")
        return 0

    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())