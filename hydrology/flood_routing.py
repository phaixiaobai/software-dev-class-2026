"""
Flood routing module for grid-based inundation modeling.
"""

import numpy as np
from typing import Tuple, Optional, List
from collections import deque


class FloodRouter:
    """
    Grid-based flood spread algorithm using BFS propagation.
    """

    def __init__(self, dem: np.ndarray, resolution: float = 30.0,
                 building_mask: Optional[np.ndarray] = None,
                 connectivity: int = 8):
        """
        Initialize flood router.

        Args:
            dem: 2D elevation array in meters.
            resolution: Cell resolution in meters.
            building_mask: Optional binary mask (1=blocked).
            connectivity: 4 or 8 for neighbor connectivity.
        """
        self.dem = dem
        self.resolution = resolution
        self.building_mask = building_mask
        self.connectivity = connectivity
        self._validate_inputs()

    def _validate_inputs(self) -> None:
        """Validate input parameters."""
        if self.dem.ndim != 2:
            raise ValueError("DEM must be 2D array")

        if self.connectivity not in (4, 8):
            raise ValueError("Connectivity must be 4 or 8")

        if self.building_mask is not None:
            if self.building_mask.shape != self.dem.shape:
                raise ValueError("Building mask must match DEM shape")
            if self.building_mask.dtype != bool:
                raise ValueError("Building mask must be boolean")

    @property
    def cell_area(self) -> float:
        """Return cell area in square meters."""
        return self.resolution ** 2

    def _get_neighbors(self, row: int, col: int) -> List[Tuple[int, int]]:
        """
        Get valid neighboring cells based on connectivity.

        Args:
            row: Row index.
            col: Column index.

        Returns:
            List of valid neighbor coordinates.
        """
        rows, cols = self.shape
        neighbors = []

        if self.connectivity == 4:
            moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        else:
            moves = [(-1, 0), (1, 0), (0, -1), (0, 1),
                     (-1, -1), (-1, 1), (1, -1), (1, 1)]

        for dr, dc in moves:
            nr, nc = row + dr, col + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if self.building_mask is None or not self.building_mask[nr, nc]:
                    neighbors.append((nr, nc))

        return neighbors

    def compute_flood_extent(self, water_level: float) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute flood extent using BFS propagation.

        Args:
            water_level: Water surface elevation in meters.

        Returns:
            Tuple of (flooded_mask, depth_array).
        """
        rows, cols = self.dem.shape
        flooded = np.zeros((rows, cols), dtype=bool)
        depth = np.zeros((rows, cols), dtype=np.float64)

        initial_flooded = self.dem < water_level

        queue = deque()
        visited = np.zeros((rows, cols), dtype=bool)

        for i in range(rows):
            for j in range(cols):
                if initial_flooded[i, j]:
                    if self.building_mask is None or not self.building_mask[i, j]:
                        queue.append((i, j))
                        flooded[i, j] = True
                        visited[i, j] = True

        while queue:
            row, col = queue.popleft()

            for nr, nc in self._get_neighbors(row, col):
                if not visited[nr, nc]:
                    if self.dem[nr, nc] < water_level:
                        if self.building_mask is None or not self.building_mask[nr, nc]:
                            visited[nr, nc] = True
                            flooded[nr, nc] = True
                            queue.append((nr, nc))

        depth = np.where(flooded, water_level - self.dem, 0.0)

        return flooded, depth

    def compute_flood_volume(self, water_level: float) -> dict:
        """
        Compute flood volume and statistics.

        Args:
            water_level: Water surface elevation in meters.

        Returns:
            Dictionary with volume, cell count, mean depth.
        """
        flooded, depth = self.compute_flood_extent(water_level)

        flooded_cells = np.sum(flooded)
        total_volume = np.sum(depth) * self.cell_area
        mean_depth = np.mean(depth[flooded]) if flooded_cells > 0 else 0.0

        return {
            'flooded_cells': int(flooded_cells),
            'total_volume_m3': float(total_volume),
            'mean_depth_m': float(mean_depth),
            'flooded_percentage': float(flooded_cells / self.dem.size * 100)
        }

    def simulate_rising_water(self, levels: np.ndarray) -> dict:
        """
        Simulate flood at multiple water levels.

        Args:
            levels: Array of water level elevations.

        Returns:
            Dictionary with results for each level.
        """
        results = {
            'water_levels': [],
            'flooded_pct': [],
            'max_depth_m': [],
            'volume_m3': []
        }

        for level in levels:
            flooded, depth = self.compute_flood_extent(level)
            stats = self.compute_flood_volume(level)

            results['water_levels'].append(level)
            results['flooded_pct'].append(stats['flooded_percentage'])
            results['max_depth_m'].append(float(depth.max()))
            results['volume_m3'].append(stats['total_volume_m3'])

        return results

    @property
    def shape(self) -> Tuple[int, int]:
        """Return DEM shape."""
        return self.dem.shape


class BuildingGenerator:
    """
    Generate synthetic building footprints as flood barriers.
    """

    def __init__(self, rows: int, cols: int, num_buildings: int = 50,
                 min_size: int = 2, max_size: int = 8, seed: int = 42):
        """
        Initialize building generator.

        Args:
            rows: Number of rows in grid.
            cols: Number of columns in grid.
            num_buildings: Number of buildings to generate.
            min_size: Minimum building size in cells.
            max_size: Maximum building size in cells.
            seed: Random seed for reproducibility.
        """
        self.rows = rows
        self.cols = cols
        self.num_buildings = num_buildings
        self.min_size = min_size
        self.max_size = max_size
        self.seed = seed

    def generate(self) -> np.ndarray:
        """
        Generate random rectangular building footprints.

        Returns:
            Boolean mask where True indicates building.
        """
        mask = np.zeros((self.rows, self.cols), dtype=bool)
        np.random.seed(self.seed)

        for _ in range(self.num_buildings):
            h = np.random.randint(self.min_size, self.max_size + 1)
            w = np.random.randint(self.min_size, self.max_size + 1)
            r = np.random.randint(0, self.rows - h)
            c = np.random.randint(0, self.cols - w)

            mask[r:r+h, c:c+w] = True

        return mask


def compute_flood_volume(dem: np.ndarray, water_level: float,
                         resolution: float = 30.0) -> dict:
    """
    Compute total flood volume, cell count, and mean depth.

    Args:
        dem: 2D elevation array.
        water_level: Water surface elevation.
        resolution: Cell resolution in meters.

    Returns:
        Dictionary with volume, cell count, mean depth.
    """
    router = FloodRouter(dem, resolution=resolution)
    return router.compute_flood_volume(water_level)