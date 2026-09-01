from __future__ import annotations

from pathlib import Path
from typing import Any

from mundasense.ml.registry import load_bundle


def load_evaluation_bundle(model_path: Path, trusted_directory: Path) -> dict[str, Any]:
    """Load and validate an existing bundle for technical evaluation views."""
    return load_bundle(model_path, trusted_directory=trusted_directory)
