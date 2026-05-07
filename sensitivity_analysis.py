"""SCS-CN Sensitivity Analysis and Visualization.

This script performs sensitivity analysis on the SCS-CN runoff method
and generates visualizations for different Curve Number scenarios.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scs_cn_runoff import calculate_runoff


# =============================================================================
# Script 1 — CN Sensitivity Analysis (Fixed Rainfall)
# =============================================================================


def cn_sensitivity_analysis():
    """Perform CN sensitivity analysis with fixed precipitation."""
    P = 50.0  # Fixed rainfall in mm
    cn_values = [60, 70, 80, 90, 95, 100]

    # Compute runoff for each CN value
    results = []
    for cn in cn_values:
        Q = calculate_runoff(P, cn)
        ratio = (Q / P) * 100
        results.append(
            {"CN": cn, "Q (mm)": round(Q, 2), "Runoff Ratio (%)": round(ratio, 2)}
        )

    # Create DataFrame for structured output
    df = pd.DataFrame(results)

    # Print summary table
    print("=" * 55)
    print("CN Sensitivity Analysis (Fixed Rainfall P = 50 mm)")
    print("=" * 55)
    print(df.to_string(index=False))
    print("=" * 55)

    return df, P, cn_values


def plot_cn_sensitivity(df, P, cn_values):
    """Create combined bar + line chart for CN sensitivity."""
    fig, ax = plt.subplots(figsize=(10, 6))

    cn_array = np.array(df["CN"].values)
    Q_array = np.array(df["Q (mm)"].values)

    # Color gradient: green (low CN) to red (high CN)
    colors = plt.cm.RdYlGn_r(np.linspace(0, 1, len(cn_values)))

    # Bar chart
    bars = ax.bar(
        cn_array,
        Q_array,
        color=colors,
        alpha=0.7,
        width=4,
        label="Runoff Q",
        edgecolor="black",
        linewidth=0.5,
    )

    # Annotate each bar with Q value
    for bar, Q_val in zip(bars, Q_array):
        ax.annotate(
            f"{Q_val:.1f}",
            xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    # Overlay line plot
    ax.plot(
        cn_array,
        Q_array,
        "ko-",
        markersize=8,
        linewidth=2,
        markerfacecolor="white",
        markeredgewidth=2,
        label="Trend",
    )

    # Configure axes and title
    ax.set_xlabel("Curve Number (CN)", fontsize=12)
    ax.set_ylabel("Runoff Q (mm)", fontsize=12)
    ax.set_title(f"Runoff Sensitivity to Curve Number (P = {int(P)}mm)", fontsize=14)
    ax.set_xticks(cn_array)
    ax.set_xlim(55, 105)
    ax.grid(True, alpha=0.3, linestyle="--")

    plt.tight_layout()
    plt.savefig("cn_sensitivity.png", dpi=150, bbox_inches="tight")
    plt.close()

    print("Figure saved: cn_sensitivity.png")


# =============================================================================
# Script 2 — Rainfall vs Runoff Curves
# =============================================================================


def rainfall_runoff_analysis():
    """Analyze runoff for range of rainfall values across different CNs."""
    P_range = np.arange(0, 101, 1)  # 0 to 100 mm
    cn_values = [60, 70, 80, 90, 100]

    # Compute Q for each P and CN
    results = {}
    for cn in cn_values:
        Q_values = [calculate_runoff(P, cn) for P in P_range]
        results[cn] = Q_values

    return P_range, cn_values, results


def plot_rainfall_runoff_curves(P_range, cn_values, results):
    """Create multi-line plot for rainfall vs runoff."""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Distinct colors for each CN line
    colors = plt.cm.viridis(np.linspace(0, 0.9, len(cn_values)))

    # Plot lines for each CN
    for cn, color in zip(cn_values, colors):
        ax.plot(P_range, results[cn], linewidth=2, color=color, label=f"CN = {cn}")

    # Diagonal dashed line: Q = P (maximum possible runoff)
    ax.plot(P_range, P_range, "k--", linewidth=1.5, alpha=0.7, label="Q = P (max)")

    # Shade area between Q=P and CN=60 curve
    ax.fill_between(
        P_range, results[60], P_range, alpha=0.2, color="gray", label="_nolegend_"
    )

    # Configure axes and title
    ax.set_xlabel("Rainfall P (mm)", fontsize=12)
    ax.set_ylabel("Runoff Q (mm)", fontsize=12)
    ax.set_title("SCS-CN Runoff vs Rainfall for Different Curve Numbers", fontsize=14)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.legend(loc="upper left", fontsize=10)
    ax.grid(True, alpha=0.3, linestyle="--")

    plt.tight_layout()
    plt.savefig("rainfall_runoff_curves.png", dpi=150, bbox_inches="tight")
    plt.close()

    print("Figure saved: rainfall_runoff_curves.png")


# =============================================================================
# Main Execution
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("SCS-CN SENSITIVITY ANALYSIS AND VISUALIZATION")
    print("=" * 60 + "\n")

    # Script 1: CN Sensitivity Analysis
    print("Running Script 1: CN Sensitivity Analysis...")
    df, P_fixed, cn_values = cn_sensitivity_analysis()
    plot_cn_sensitivity(df, P_fixed, cn_values)

    print("\n" + "-" * 60 + "\n")

    # Script 2: Rainfall vs Runoff Curves
    print("Running Script 2: Rainfall vs Runoff Curves...")
    P_range, cn_values, results = rainfall_runoff_analysis()
    plot_rainfall_runoff_curves(P_range, cn_values, results)

    print("\n" + "=" * 60)
    print("Analysis complete! Check generated PNG files.")
    print("=" * 60 + "\n")
