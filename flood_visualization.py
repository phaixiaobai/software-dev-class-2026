import numpy as np
import matplotlib.pyplot as plt
from flood_analysis import calculate_flood


def visualize_flood(dem: np.ndarray, water_level: float, save_path: str | None = None):
    """
    Visualize flood inundation analysis for a given DEM and water level.

    Parameters
    ----------
    dem : np.ndarray
        100x100 Digital Elevation Model (elevation in meters).
    water_level : float
        Water level elevation in meters.
    save_path : str | None, optional
        Path to save the figure. If None, displays interactively.
    """
    flooded_mask, depth_array, percentage, max_depth, total_volume = calculate_flood(
        dem, water_level
    )
    mean_depth = depth_array[flooded_mask].mean() if flooded_mask.sum() > 0 else 0

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    ax1 = axes[0, 0]
    im1 = ax1.imshow(dem, cmap="terrain")
    plt.colorbar(im1, ax=ax1, label="Elevation (m)")
    ax1.set_title("Digital Elevation Model")
    contour_levels = np.arange(int(dem.min()), int(dem.max()) + 5, 5)
    ax1.contour(dem, levels=contour_levels, colors="white", linewidths=0.5)

    ax2 = axes[0, 1]
    ax2.imshow(dem, cmap="gray", alpha=0.6)
    flood_display = np.ma.masked_where(~flooded_mask, flooded_mask)
    ax2.imshow(flood_display, cmap="Blues", alpha=0.7, vmin=0, vmax=1)
    ax2.set_title(f"Flood Extent at {water_level}m Water Level")
    ax2.text(
        0.95,
        0.95,
        f"Flooded: {percentage:.1f}%",
        transform=ax2.transAxes,
        fontsize=12,
        color="white",
        ha="right",
        va="top",
        bbox=dict(boxstyle="round", facecolor="blue", alpha=0.7),
    )

    ax3 = axes[1, 0]
    depth_display = np.ma.masked_where(depth_array == 0, depth_array)
    im3 = ax3.imshow(depth_display, cmap="Blues", vmin=0)
    plt.colorbar(im3, ax=ax3, label="Inundation Depth (m)")
    ax3.set_title("Inundation Depth Map")

    ax4 = axes[1, 1]
    flooded_depths = depth_array[flooded_mask]
    if flooded_depths.size > 0:
        ax4.hist(flooded_depths, bins=30, color="steelblue", edgecolor="white")
        ax4.axvline(
            mean_depth,
            color="red",
            linestyle="--",
            linewidth=2,
            label=f"Mean: {mean_depth:.2f}m",
        )
        ax4.text(
            0.95,
            0.95,
            f"Mean depth: {mean_depth:.2f}m\nMax depth: {max_depth:.2f}m",
            transform=ax4.transAxes,
            fontsize=11,
            color="black",
            ha="right",
            va="top",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
        )
    else:
        ax4.text(
            0.5,
            0.5,
            "No flooded cells",
            ha="center",
            va="center",
            transform=ax4.transAxes,
        )
    ax4.set_xlabel("Inundation Depth (m)")
    ax4.set_ylabel("Number of Cells")
    ax4.set_title("Distribution of Flood Depths")

    fig.suptitle(
        f"Flood Inundation Analysis — Water Level: {water_level}m",
        fontsize=14,
        fontweight="bold",
    )
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Saved: {save_path}")
    else:
        plt.show()

    plt.close()


if __name__ == "__main__":
    dem = np.load("dem_data.npy")

    visualize_flood(dem, 40, "flood_extent_40m.png")
    visualize_flood(dem, 50, "flood_extent_50m.png")
