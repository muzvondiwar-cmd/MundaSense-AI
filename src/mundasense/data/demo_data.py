from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

DISTRICTS = (
    "Bindura",
    "Chinhoyi",
    "Gokwe South",
    "Goromonzi",
    "Masvingo",
    "Mutare",
    "Plumtree",
    "Zvishavane",
)

SEASONS = ("2021/22", "2022/23", "2023/24", "2024/25")

DEMO_SCENARIOS = {
    "balanced": {
        "rainfall_mm": 690.0,
        "fertilizer_kg_ha": 125.0,
        "temperature_c": 24.0,
        "humidity_pct": 63.0,
        "soil_ph": 6.2,
        "crop": "maize",
        "season": "2025/26",
        "district": "Goromonzi",
        "farm_reference": "Demo - balanced",
    },
    "water_stress": {
        "rainfall_mm": 255.0,
        "fertilizer_kg_ha": 70.0,
        "temperature_c": 31.5,
        "humidity_pct": 37.0,
        "soil_ph": 5.8,
        "crop": "maize",
        "season": "2025/26",
        "district": "Masvingo",
        "farm_reference": "Demo - water stress",
    },
    "unusual": {
        "rainfall_mm": 1_420.0,
        "fertilizer_kg_ha": 520.0,
        "temperature_c": 38.0,
        "humidity_pct": 92.0,
        "soil_ph": 8.8,
        "crop": "maize",
        "season": "2025/26",
        "district": "Outside demo range",
        "farm_reference": "Demo - unusual data",
    },
}


def generate_synthetic_maize_data(rows: int = 720, seed: int = 42) -> pd.DataFrame:
    """Generate honest demonstration data with plausible structure, not field evidence."""
    rng = np.random.default_rng(seed)
    district = rng.choice(DISTRICTS, rows)
    season = rng.choice(SEASONS, rows)
    rainfall = np.clip(rng.normal(620, 185, rows), 150, 1_150)
    fertilizer = np.clip(rng.gamma(3.1, 36, rows), 0, 360)
    temperature = np.clip(rng.normal(25.1, 3.1, rows), 16, 35)
    humidity = np.clip(70 - 0.07 * (temperature - 20) * 10 + rng.normal(0, 9, rows), 28, 92)
    soil_ph = np.clip(rng.normal(6.1, 0.72, rows), 4.2, 8.2)

    rainfall_score = 2.05 * np.exp(-((rainfall - 680) / 330) ** 2)
    fertilizer_score = 1.25 * (1 - np.exp(-fertilizer / 105))
    temperature_penalty = 0.055 * (temperature - 24.0) ** 2
    humidity_penalty = 0.0007 * (humidity - 62.0) ** 2
    ph_penalty = 0.38 * (soil_ph - 6.2) ** 2
    district_effect_map = {
        name: effect for name, effect in zip(DISTRICTS, (0.18, 0.12, -0.08, 0.24, -0.18, 0.08, -0.22, -0.12), strict=True)
    }
    season_effect_map = dict(zip(SEASONS, (-0.16, 0.06, -0.12, 0.18), strict=True))
    context = np.array([district_effect_map[value] for value in district]) + np.array(
        [season_effect_map[value] for value in season]
    )
    noise = rng.normal(0, 0.48, rows)
    yield_t_ha = np.clip(
        0.55
        + rainfall_score
        + fertilizer_score
        - temperature_penalty
        - humidity_penalty
        - ph_penalty
        + context
        + noise,
        0.15,
        7.5,
    )

    return pd.DataFrame(
        {
            "record_id": [f"SYN-{index + 1:04d}" for index in range(rows)],
            "crop": "maize",
            "district": district,
            "season": season,
            "rainfall_mm": rainfall.round(1),
            "fertilizer_kg_ha": fertilizer.round(1),
            "temperature_c": temperature.round(1),
            "humidity_pct": humidity.round(1),
            "soil_ph": soil_ph.round(2),
            "yield_t_ha": yield_t_ha.round(3),
            "data_source": "MundaSense deterministic synthetic demo generator v1",
            "is_synthetic": True,
        }
    )


def write_demo_data(path: Path, rows: int = 720, seed: int = 42) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    generate_synthetic_maize_data(rows=rows, seed=seed).to_csv(path, index=False, encoding="utf-8")
    return path

