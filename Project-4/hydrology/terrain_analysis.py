"""
Terrain analysis module for DEM-based flood modeling.
"""

import numpy as np
from typing import Tuple, Optional


class TerrainAnalyzer:
    """
    Analyze terrain characteristics from DEM data.
    """

    def __init__(self, dem: np.ndarray, resolution: float = 30.0):
        """
        Initialize terrain analyzer.

        Args:
            dem: 2D numpy array of elevation values in meters.
            resolution: Spatial resolution in meters per cell.
        """
        self.dem = dem
        self.resolution = resolution
        self._validate_dem()

    def _validate_dem(self) -> None:
        """Validate DEM integrity."""
        if np.any(np.isnan(self.dem)):
            raise ValueError("DEM contains NaN values")

        if self.dem.ndim != 2:
            raise ValueError(f"DEM must be 2D, got {self.dem.ndim}D")

        if self.resolution <= 0:
            raise ValueError("Resolution must be positive")

    @property
    def shape(self) -> Tuple[int, int]:
        """Return DEM shape (rows, cols)."""
        return self.dem.shape

    @property
    def cell_area(self) -> float:
        """Return cell area in square meters."""
        return self.resolution ** 2

    def compute_slope(self) -> np.ndarray:
        """
        Compute terrain slope using finite differences.

        Returns:
            2D array of slope values in degrees.
        """
        rows, cols = self.shape

        slope = np.zeros_like(self.dem)

        if rows > 1:
            slope[1:, :] = (self.dem[1:, :] - self.dem[:-1, :]) / self.resolution

        if cols > 1:
            slope[:, 1:] = np.maximum(
                slope[:, 1:],
                (self.dem[:, 1:] - self.dem[:, :-1]) / self.resolution
            )

        slope_degrees = np.degrees(np.arctan(slope))
        return slope_degrees

    def compute_flow_direction(self) -> np.ndarray:
        """
        Compute flow direction using simplified D8 method.
        Each cell flows to the lowest neighbor.

        Returns:
            2D array of flow direction codes (0-8):
            1=E, 2=SE, 3=S, 4=SW, 5=W, 6=NW, 7=N, 8=NE, 0=sink
        """
        rows, cols = self.shape
        flow_dir = np.zeros(self.shape, dtype=np.int8)

        directions = [
            (0, 1, 1),   # E
            (1, 1, 2),   # SE
            (1, 0, 3),   # S
            (1, -1, 4),  # SW
            (0, -1, 5),  # W
            (-1, -1, 6), # NW
            (-1, 0, 7),  # N
            (-1, 1, 8),  # NE
        ]

        for i in range(rows):
            for j in range(cols):
                min_drop = 0
                steepest = 0

                for di, dj, code in directions:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < rows and 0 <= nj < cols:
                        drop = self.dem[i, j] - self.dem[ni, nj]
                        if drop > min_drop:
                            min_drop = drop
                            steepest = code

                flow_dir[i, j] = steepest

        return flow_dir

    def compute_terrain_metrics(self) -> dict:
        """
        Compute comprehensive terrain metrics.

        Returns:
            Dictionary with slope, flow direction, min, max, mean elevation.
        """
        slope = self.compute_slope()
        flow_dir = self.compute_flow_direction()

        return {
            'dem': self.dem,
            'slope': slope,
            'flow_direction': flow_dir,
            'resolution': self.resolution,
            'elevation_min': float(self.dem.min()),
            'elevation_max': float(self.dem.max()),
            'elevation_mean': float(self.dem.mean()),
            'slope_mean': float(slope.mean()),
            'slope_max': float(slope.max())
        }

    def normalize(self) -> np.ndarray:
        """
        Normalize DEM while preserving relative elevation differences.

        Returns:
            Normalized DEM with min=0.
        """
        return self.dem - self.dem.min()


def load_geotiff_dem(filepath: str) -> Tuple[np.ndarray, float]:
    """
    Load DEM from GeoTIFF file.

    Args:
        filepath: Path to GeoTIFF file.

    Returns:
        Tuple of (elevation_array, resolution_meters).
    """
    try:
        import rasterio
        with rasterio.open(filepath) as src:
            dem = src.read(1)
            resolution = abs(src.transform[0])
            return dem, resolution
    except ImportError:
        raise ImportError("rasterio required for GeoTIFF loading: pip install rasterio")


def create_synthetic_terrain(rows: int = 100, cols: int = 100,
                             resolution: float = 30.0) -> np.ndarray:
    """
    Create synthetic DEM for testing.

    Args:
        rows: Number of rows.
        cols: Number of columns.
        resolution: Cell resolution in meters.

    Returns:
        2D elevation array.
    """
    row_grad = np.linspace(30, 80, rows)
    col_grad = np.linspace(30, 80, cols)
    terrain = np.zeros((rows, cols))
    for i in range(rows):
        for j in range(cols):
            terrain[i, j] = (row_grad[i] + col_grad[j]) / 2

    terrain[:, 40:51] -= 10

    np.random.seed(42)
    from scipy import ndimage
    noise = np.random.normal(0, 3, (rows, cols))
    smoothed_noise = ndimage.gaussian_filter(noise, sigma=5)
    terrain = terrain + smoothed_noise

    return np.clip(terrain, 25, 85)