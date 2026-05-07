"""Visualization package for hydrology methods.

This module supports being imported as a package (the normal case) and
provides a small fallback so that executing this file directly (e.g.
``python visualization/__init__.py``) doesn't crash with
"attempted relative import with no known parent package". The recommended
usage remains importing the package or running it with ``python -m``.
"""

import sys

try:
    # Normal package-relative import (preferred)
    from .interactive_plot import (
        HydrographPlotter,
        plot_hydrograph_comparison,
        create_summary_table,
    )
except Exception:
    # Fallback when the file is executed directly as a script. In that case
    # Python sets ``__package__`` to None and relative imports fail. When run
    # as a script the current directory is the package folder, so a plain
    # import of the sibling module will work.
    #
    # This keeps the public API stable while avoiding hard failures during
    # ad-hoc script execution.
    from interactive_plot import (
        HydrographPlotter,
        plot_hydrograph_comparison,
        create_summary_table,
    )


__all__ = [
    "HydrographPlotter",
    "plot_hydrograph_comparison",
    "create_summary_table",
]