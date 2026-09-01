from __future__ import annotations

from pathlib import Path

import pandas as pd

from mundasense.data.contracts import NUMERIC_COLUMNS, REQUIRED_COLUMNS


class DataContractError(ValueError):
    pass


def normalise_column_name(name: str) -> str:
    return "_".join(str(name).strip().lower().replace("-", " ").split())


def load_dataset(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise DataContractError(f"Dataset not found: {path}")
    try:
        frame = pd.read_csv(path, encoding="utf-8", sep=",")
    except (UnicodeDecodeError, pd.errors.ParserError) as exc:
        raise DataContractError(
            "Could not read the CSV as UTF-8 comma-delimited data. Check encoding and delimiter."
        ) from exc
    frame.columns = [normalise_column_name(column) for column in frame.columns]
    missing = sorted(set(REQUIRED_COLUMNS) - set(frame.columns))
    if missing:
        raise DataContractError(f"Missing required columns: {', '.join(missing)}")
    for column in NUMERIC_COLUMNS:
        converted = pd.to_numeric(frame[column], errors="coerce")
        newly_missing = int(converted.isna().sum() - frame[column].isna().sum())
        if newly_missing:
            raise DataContractError(
                f"Column '{column}' contains {newly_missing} non-numeric value(s)."
            )
        frame[column] = converted
    if frame.empty:
        raise DataContractError("Dataset contains no rows.")
    if frame["record_id"].duplicated().any():
        duplicates = int(frame["record_id"].duplicated().sum())
        raise DataContractError(f"Dataset contains {duplicates} duplicate record_id value(s).")
    if not frame["crop"].astype(str).str.lower().eq("maize").all():
        raise DataContractError("MVP training data must contain maize records only.")
    impossible = (
        (frame["rainfall_mm"] < 0)
        | (frame["fertilizer_kg_ha"] < 0)
        | (~frame["humidity_pct"].between(0, 100))
        | (~frame["soil_ph"].between(0, 14))
        | (frame["yield_t_ha"] < 0)
    )
    if impossible.any():
        raise DataContractError(
            f"Dataset contains {int(impossible.sum())} row(s) with impossible values."
        )
    return frame

