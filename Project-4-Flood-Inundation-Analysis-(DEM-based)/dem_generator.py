import numpy as np
try:
    from scipy import ndimage
except Exception as e:  # ImportError or other import-time issues
    msg = (
        "SciPy is not available in this Python environment.\n"
        "This project expects SciPy to be installed. Recommended options:\n"
        "  1) Use the provided venv: run './run.sh' in the project root.\n"
        "  2) Create and activate a venv yourself and install requirements.txt.\n"
        "  3) Use conda and install scipy from conda-forge.\n\n"
        f"Original import error: {e!s}\n"
    )
    raise SystemExit(msg)


def load_dem(filepath: str | None = None) -> np.ndarray:
    """
    Load or generate a synthetic DEM.

    Args:
        filepath (str | None): Path to a .npy DEM file. If provided, load DEM from file.

    Returns:
        np.ndarray: 2D array of shape (100, 100) representing elevation in meters.
    """
    if filepath is not None:
        dem = np.load(filepath)
        if not isinstance(dem, np.ndarray):
            raise ValueError("DEM must be a numpy array")
        if dem.shape != (100, 100):
            raise ValueError(f"DEM must have shape (100, 100), got {dem.shape}")
        return dem

    row_gradient = np.linspace(30, 80, 100)
    col_gradient = np.linspace(30, 80, 100)
    terrain = np.zeros((100, 100))
    for i in range(100):
        for j in range(100):
            terrain[i, j] = (row_gradient[i] + col_gradient[j]) / 2

    terrain[:, 40:51] = terrain[:, 40:51] - 10

    np.random.seed(42)
    noise = np.random.normal(0, 3, (100, 100))
    smoothed_noise = ndimage.gaussian_filter(noise, sigma=5)
    terrain = terrain + smoothed_noise

    terrain = np.clip(terrain, 25, 85)

    np.save("dem_data.npy", terrain)

    print(f"Shape: {terrain.shape}")
    print(f"Min elevation: {terrain.min():.1f} m")
    print(f"Max elevation: {terrain.max():.1f} m")
    print(f"Mean elevation: {terrain.mean():.1f} m")
    print(f"Std deviation: {terrain.std():.1f} m")

    return terrain