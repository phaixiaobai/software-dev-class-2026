"""Interactive visualization module for hydrology calculations.

This module provides interactive visualization capabilities for comparing
different runoff methods and adjusting parameters with sliders.

Requires: matplotlib, numpy
"""

from typing import Optional, Tuple
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider


class HydrographPlotter:
    """Interactive hydrograph plotter with parameter adjustment."""

    def __init__(
        self,
        precipitation: float = 50.0,
        cn: float = 70.0,
        area: float = 10.0,
        time_of_concentration: float = 30.0,
        amc: int = 2,
    ):
        """Initialize the plotter with default parameters.

        Args:
            precipitation: Precipitation depth (mm)
            cn: Curve Number
            area: Watershed area (km²)
            time_of_concentration: Time of concentration (minutes)
            amc: AMC condition (1, 2, or 3)
        """
        self.precipitation = precipitation
        self.cn = cn
        self.area = area
        self.time_of_concentration = time_of_concentration
        self.amc = amc
        self.fig = None
        self.ax = None

    def calculate_methods(self) -> Tuple[dict, dict, dict]:
        """Calculate outputs from all three methods.

        Returns:
            Tuple of (scs_result, rational_result, time_area_result)
        """
        from hydrology.scs_cn import calculate_runoff, AMCondition
        from hydrology.rational import estimate_watershed_response
        from hydrology.time_area import create_hydrograph_from_rainfall

        amc_enum = AMCondition(self.amc)
        scs_result = calculate_runoff(self.precipitation, self.cn, amc_enum)

        length = 1000
        slope = 0.01
        rational_result = estimate_watershed_response(
            precipitation=self.precipitation,
            area=self.area,
            length=length,
            slope=slope,
            land_use="agricultural",
            soil_type="b",
            amc=self.amc,
        )

        time_area_result = create_hydrograph_from_rainfall(
            precipitation=self.precipitation,
            cn=self.cn,
            area=self.area,
            time_of_concentration=self.time_of_concentration,
            amc=self.amc,
        )

        return scs_result, rational_result, time_area_result

    def plot_comparison(self, save_path: Optional[str] = None) -> None:
        """Create comparison plot of all methods.

        Args:
            save_path: Optional path to save figure
        """
        scs, rational, ta = self.calculate_methods()

        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle(
            f"Hydrology Methods Comparison\nP={self.precipitation}mm, CN={self.cn}, "
            f"Area={self.area}km², AMC={self.amc}",
            fontsize=12,
        )

        ax1 = axes[0, 0]
        x_ta = ta.time
        y_ta = ta.discharge
        ax1.fill_between(x_ta, y_ta, alpha=0.3, label='Time-Area')
        ax1.plot(x_ta, y_ta, 'b-', linewidth=2, label=f'Peak: {ta.peak_discharge:.2f} m³/s')
        ax1.set_xlabel("Time (min)")
        ax1.set_ylabel("Discharge (m³/s)")
        ax1.set_title("Hydrograph (Time-Area Method)")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        ax2 = axes[0, 1]
        ax2.plot(ta.time, ta.discharge, 'b-', linewidth=2, label='Time-Area')
        ax2.axhline(
            y=rational.peak_discharge,
            color='r',
            linestyle='--',
            label=f'Rational: {rational.peak_discharge:.2f} m³/s'
        )
        ax2.set_xlabel("Time (min)")
        ax2.set_ylabel("Discharge (m³/s)")
        ax2.set_title("Method Comparison")
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        ax3 = axes[1, 0]
        methods = ["SCS-CN", "Rational", "Time-Area"]
        runoff_volumes = [
            scs.runoff_depth * self.area * 1000,
            (rational.runoff_coefficient * self.precipitation * self.area * 1000),
            ta.total_runoff_volume / (self.area * 1e6) * 1000,
        ]
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
        bars = ax3.bar(methods, runoff_volumes, color=colors)
        ax3.set_ylabel("Runoff Volume (m³ × 1000)")
        ax3.set_title("Runoff Volume Comparison")
        for bar, vol in zip(bars, runoff_volumes):
            ax3.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.5,
                f"{vol:.1f}",
                ha="center",
                va="bottom",
            )
        ax3.grid(True, alpha=0.3, axis='y')

        ax4 = axes[1, 1]
        peak_qs = [
            scs.effective_precipitation * self.area / (self.time_of_concentration / 60),
            rational.peak_discharge,
            ta.peak_discharge,
        ]
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
        bars = ax4.bar(methods, peak_qs, color=colors)
        ax4.set_ylabel("Peak Discharge (m³/s)")
        ax4.set_title("Peak Discharge Comparison")
        for bar, q in zip(bars, peak_qs):
            ax4.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.1,
                f"{q:.2f}",
                ha="center",
                va="bottom",
            )
        ax4.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')

        plt.show()

    def create_interactive_plot(self) -> None:
        """Create interactive plot with sliders for parameter adjustment."""
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        plt.subplots_adjust(bottom=0.35)

        scs, rational, ta = self.calculate_methods()

        self.line, = self.ax.plot([], [], 'b-', linewidth=2, label='Hydrograph')
        self.ax.set_xlim(0, self.time_of_concentration * 2)
        self.ax.set_ylim(0, max(ta.peak_discharge * 1.2, 1))
        self.ax.set_xlabel("Time (min)")
        self.ax.set_ylabel("Discharge (m³/s)")
        self.ax.set_title(
            f"Hydrograph: P={self.precipitation}mm, CN={self.cn}, "
            f"Area={self.area}km², AMC={self.amc}"
        )
        self.ax.grid(True, alpha=0.3)

        ax_precip = plt.axes([0.2, 0.20, 0.65, 0.03])
        ax_cn = plt.axes([0.2, 0.15, 0.65, 0.03])
        ax_area = plt.axes([0.2, 0.10, 0.65, 0.03])

        self.slider_precip = Slider(
            ax_precip,
            "Precipitation (mm)",
            0,
            200,
            valinit=self.precipitation,
        )
        self.slider_cn = Slider(
            ax_cn,
            "Curve Number",
            10,
            100,
            valinit=self.cn,
        )
        self.slider_area = Slider(
            ax_area,
            "Area (km²)",
            0.1,
            100,
            valinit=self.area,
        )

        self.slider_precip.on_changed(self._update)
        self.slider_cn.on_changed(self._update)
        self.slider_area.on_changed(self._update)

        plt.show()

    def _update(self, val) -> None:
        """Update plot when sliders change."""
        self.precipitation = self.slider_precip.val
        self.cn = self.slider_cn.val
        self.area = self.slider_area.val

        scs, rational, ta = self.calculate_methods()

        self.ax.set_title(
            f"Hydrograph: P={self.precipitation:.1f}mm, CN={self.cn:.1f}, "
            f"Area={self.area:.1f}km², AMC={self.amc}"
        )
        self.ax.set_xlim(0, self.time_of_concentration * 2)
        self.ax.set_ylim(0, max(ta.peak_discharge * 1.2, 1))

        self.line.set_data(ta.time, ta.discharge)
        self.fig.canvas.draw_idle()


def plot_hydrograph_comparison(
    scs_result,
    rational_result,
    time_area_result,
    title: str = "Hydrograph Comparison",
    save_path: Optional[str] = None,
) -> None:
    """Create static comparison plot of hydrographs."""
    fig, ax = plt.subplots(figsize=(10, 6))

    ta = time_area_result
    ax.fill_between(ta.time, ta.discharge, alpha=0.3, color='blue')
    ax.plot(
        ta.time, ta.discharge,
        'b-', linewidth=2,
        label=f'Time-Area (Peak: {ta.peak_discharge:.2f} m³/s)'
    )

    ax.axhline(
        y=rational_result.peak_discharge,
        color='red', linestyle='--', linewidth=1.5,
        label=f'Rational (Qp: {rational_result.peak_discharge:.2f} m³/s)'
    )

    ax.set_xlabel("Time (minutes)", fontsize=12)
    ax.set_ylabel("Discharge (m³/s)", fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')

    plt.show()


def create_summary_table(results: dict, title: str = "Hydrology Methods Comparison") -> str:
    """Create summary table of results."""
    lines = [
        "=" * 60,
        title,
        "=" * 60,
        f"{'Method':<20} {'Runoff (mm)':<15} {'Peak Q (m³/s)':<15} {'Volume (m³)':<15}",
        "-" * 60,
    ]

    for name, result in results.items():
        lines.append(
            f"{name:<20} {result.get('runoff', 0):<15.2f} "
            f"{result.get('peak_q', 0):<15.2f} {result.get('volume', 0):<15.2f}"
        )

    lines.append("=" * 60)
    return "\n".join(lines)