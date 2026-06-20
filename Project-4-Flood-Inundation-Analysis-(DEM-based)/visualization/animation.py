"""
Animation module for flood simulation visualization.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, List
import os


class FloodAnimator:
    """
    Create animated flood simulation visualizations.
    """

    def __init__(self, dem: np.ndarray, resolution: float = 30.0,
                 building_mask: Optional[np.ndarray] = None):
        """
        Initialize flood animator.

        Args:
            dem: 2D elevation array in meters.
            resolution: Cell resolution in meters.
            building_mask: Optional binary mask for buildings.
        """
        self.dem = dem
        self.resolution = resolution
        self.building_mask = building_mask
        self.vmin = dem.min()
        self.vmax = dem.max()

    def _create_frame(self, water_level: float, flooded: np.ndarray,
                      depth: np.ndarray, ax: plt.Axes) -> None:
        """
        Create a single animation frame.

        Args:
            water_level: Current water level.
            flooded: Flooded cell mask.
            depth: Depth array.
            ax: Matplotlib axis.
        """
        ax.imshow(self.dem, cmap='terrain', vmin=self.vmin, vmax=self.vmax,
                  alpha=0.7)

        flood_display = np.ma.masked_where(~flooded, flooded)
        ax.imshow(flood_display, cmap='Blues', alpha=0.6, vmin=0, vmax=1)

        if self.building_mask is not None:
            building_display = np.ma.masked_where(~self.building_mask,
                                                   self.building_mask)
            ax.imshow(building_display, cmap='Reds', alpha=0.5, vmin=0, vmax=1)

        ax.set_title(f'Water Level: {water_level:.1f}m', fontsize=14)
        ax.set_xlabel('Column')
        ax.set_ylabel('Row')

        flooded_pct = np.sum(flooded) / flooded.size * 100
        ax.text(0.02, 0.98, f'Flooded: {flooded_pct:.1f}%',
                transform=ax.transAxes, fontsize=12, va='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    def create_animation(self, levels: np.ndarray, output_path: str,
                         fps: int = 2, dpi: int = 100) -> None:
        """
        Create animated GIF of rising water.

        Args:
            levels: Array of water level values.
            output_path: Path to save GIF.
            fps: Frames per second.
            dpi: Image resolution.
        """
        from hydrology.flood_routing import FloodRouter

        router = FloodRouter(self.dem, self.resolution, self.building_mask)

        frames = []
        temp_dir = '/var/folders/50/1fqmkqcd6sqdk1q3g6kl2lsm0000gn/T/opencode'

        for i, level in enumerate(levels):
            fig, ax = plt.subplots(figsize=(10, 8))
            flooded, depth = router.compute_flood_extent(level)
            self._create_frame(level, flooded, depth, ax)
            plt.tight_layout()

            frame_path = os.path.join(temp_dir, f'frame_{i:03d}.png')
            fig.savefig(frame_path, dpi=dpi, bbox_inches='tight')
            plt.close(fig)

            frame = plt.imread(frame_path)
            if frame.dtype == np.float32 or frame.dtype == np.float64:
                frame = (np.clip(frame, 0, 1) * 255).astype(np.uint8)
            frames.append(frame)

            if os.path.exists(frame_path):
                os.remove(frame_path)

        try:
            import imageio
            imageio.mimsave(output_path, frames, fps=fps)
            print(f"Animation saved to {output_path}")
        except ImportError:
            print("imageio not available, skipping animation")


def create_static_visualization(dem: np.ndarray, levels: np.ndarray,
                                 resolution: float = 30.0,
                                 building_mask: Optional[np.ndarray] = None,
                                 save_path: str = 'flood_stages.png') -> None:
    """
    Create multi-panel static visualization of flood stages.

    Args:
        dem: 2D elevation array.
        levels: Array of water levels.
        resolution: Cell resolution.
        building_mask: Optional building mask.
        save_path: Path to save figure.
    """
    from hydrology.flood_routing import FloodRouter

    router = FloodRouter(dem, resolution, building_mask)
    n_levels = len(levels)

    fig, axes = plt.subplots(1, n_levels, figsize=(4*n_levels, 5))
    if n_levels == 1:
        axes = [axes]

    for ax, level in zip(axes, levels):
        flooded, depth = router.compute_flood_extent(level)

        ax.imshow(dem, cmap='terrain', alpha=0.7)
        flood_display = np.ma.masked_where(~flooded, flooded)
        ax.imshow(flood_display, cmap='Blues', alpha=0.6, vmin=0, vmax=1)

        if building_mask is not None:
            bldg_display = np.ma.masked_where(~building_mask, building_mask)
            ax.imshow(bldg_display, cmap='Reds', alpha=0.5, vmin=0, vmax=1)

        pct = np.sum(flooded) / flooded.size * 100
        ax.set_title(f'{level}m\n({pct:.1f}% flooded)')
        ax.set_xticks([])
        ax.set_yticks([])

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"Static visualization saved to {save_path}")
    plt.show()


def create_depth_animation(dem: np.ndarray, levels: np.ndarray,
                            resolution: float = 30.0,
                            save_path: str = 'flood_depth.gif') -> None:
    """
    Create animation showing depth progression.

    Args:
        dem: 2D elevation array.
        levels: Array of water levels.
        resolution: Cell resolution.
        save_path: Path to save GIF.
    """
    from hydrology.flood_routing import FloodRouter

    router = FloodRouter(dem, resolution)
    frames = []
    temp_dir = '/var/folders/50/1fqmkqcd6sqdk1q3g6kl2lsm0000gn/T/opencode'

    for i, level in enumerate(levels):
        fig, ax = plt.subplots(figsize=(8, 6))
        _, depth = router.compute_flood_extent(level)

        depth_display = np.ma.masked_where(depth == 0, depth)
        im = ax.imshow(depth_display, cmap='Blues', vmin=0)
        plt.colorbar(im, ax=ax, label='Depth (m)')

        ax.set_title(f'Inundation Depth at {level}m')
        plt.tight_layout()

        frame_path = os.path.join(temp_dir, f'depth_{i:03d}.png')
        fig.savefig(frame_path, bbox_inches='tight')
        plt.close(fig)

        frame = plt.imread(frame_path)
        if frame.dtype == np.float32 or frame.dtype == np.float64:
            frame = (np.clip(frame, 0, 1) * 255).astype(np.uint8)
        frames.append(frame)

        if os.path.exists(frame_path):
            os.remove(frame_path)

    try:
        import imageio
        imageio.mimsave(save_path, frames, fps=2)
        print(f"Depth animation saved to {save_path}")
    except ImportError:
        print("imageio not available, skipping animation")