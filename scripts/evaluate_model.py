from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mundasense.config import AppConfig  # noqa: E402
from mundasense.ml.registry import load_bundle  # noqa: E402


def main() -> None:
    config = AppConfig.from_env()
    bundle = load_bundle(config.model_path, trusted_directory=config.trusted_models_dir)
    print(
        json.dumps(
            {
                "model_version": bundle["model_version"],
                "created_at": bundle["created_at"],
                "is_synthetic": bundle["is_synthetic"],
                "split_strategy": bundle["split_strategy"],
                "metrics": bundle["metrics"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
