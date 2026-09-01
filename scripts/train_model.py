from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mundasense.config import AppConfig  # noqa: E402
from mundasense.data.demo_data import write_demo_data  # noqa: E402
from mundasense.ml.train import train_model  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the MundaSense demonstration model.")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--rows", type=int, default=720)
    parser.add_argument("--regenerate-data", action="store_true")
    args = parser.parse_args()
    config = AppConfig.from_env()
    seed = config.random_seed if args.seed is None else args.seed
    if args.regenerate_data or not config.data_path.exists():
        write_demo_data(config.data_path, rows=args.rows, seed=seed)
        print(f"Wrote clearly labelled synthetic data: {config.data_path}")
    bundle = train_model(
        config.data_path,
        config.model_path,
        ROOT / "reports" / "metrics",
        ROOT / "reports" / "figures",
        seed=seed,
    )
    metrics = bundle["metrics"]
    print(f"Model: {bundle['model_version']} ({bundle['training_config']['champion']})")
    print(
        f"Held-out synthetic metrics: MAE={metrics['mae_t_ha']:.3f} t/ha; "
        f"RMSE={metrics['rmse_t_ha']:.3f} t/ha; R2={metrics['r2']:.3f}; "
        f"coverage={metrics['interval_empirical_coverage']:.1%}"
    )
    print(f"Saved trusted bundle: {config.model_path}")


if __name__ == "__main__":
    main()
