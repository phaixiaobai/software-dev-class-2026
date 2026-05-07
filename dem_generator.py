import numpy as np
from scipy.ndimage import gaussian_filter


def load_dem(filepath: str | None = None) -> np.ndarray:
    """
    Load or generate a 100x100 Digital Elevation Model (DEM).

    Parameters
    ----------
    filepath : str | None, optional
        Path to a .npy file. If None, generates synthetic DEM.

    Returns
    -------
    np.ndarray
        100x100 elevation array in meters.
    """
    if filepath is not None:
        return np.load(filepath)

    row_gradient = np.linspace(30, 80, 100)
    col_gradient = np.linspace(30, 80, 100)
    terrain = (row_gradient[:, np.newaxis] + col_gradient[np.newaxis, :]) / 2

    terrain[:, 40:50] -= 10

    np.random.seed(42)
    noise = np.random.normal(0, 3, (100, 100))
    noise = gaussian_filter(noise, sigma=5)
    terrain = terrain + noise

    terrain = np.clip(terrain, 25, 85)

    np.save("dem_data.npy", terrain)

    print(f"Shape: {terrain.shape}")
    print(f"Min elevation: {terrain.min():.1f} m")
    print(f"Max elevation: {terrain.max():.1f} m")
    print(f"Mean elevation: {terrain.mean():.1f} m")
    print(f"Std deviation: {terrain.std():.1f} m")

    return terrain


if __name__ == "__main__":
    dem = load_dem()
