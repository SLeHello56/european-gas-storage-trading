"""Reproducible completely synthetic AGSI+-style storage/TTF examples."""
import numpy as np
import pandas as pd


def synthetic_gas_market(days: int = 365, seed: int = 18) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    t = np.arange(days)
    seasonal = 62 - 23 * np.cos(2 * np.pi * t / 365)
    storage = np.clip(seasonal + 6 * np.sin(2 * np.pi * t / 75) + rng.normal(0, 1.2, days), 5, 98)
    summer = 35 + 4 * np.sin(2 * np.pi * t / 150) + rng.normal(0, 1, days).cumsum() / 8
    # Spread path responds partly to weather/storage shocks; deliberately artificial.
    spread = 4 - 0.14 * (storage - seasonal) + 1.3 * np.sin(2 * np.pi * t / 28)
    spread += rng.normal(0, 0.8, days).cumsum() / 8
    return pd.DataFrame({
        "date": pd.date_range("2025-01-01", periods=days).strftime("%Y-%m-%d"),
        "storage_pct": np.round(storage, 2),
        "seasonal_reference_pct": np.round(seasonal, 2),
        "ttf_winter_eur_mwh": np.round(summer + spread, 2),
        "ttf_summer_eur_mwh": np.round(summer, 2),
    })
