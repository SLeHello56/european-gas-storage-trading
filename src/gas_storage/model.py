"""Illustrative TTF winter/summer spread research with strictly lagged signals."""
import numpy as np
import pandas as pd

REQUIRED = {"date", "storage_pct", "seasonal_reference_pct", "ttf_winter_eur_mwh", "ttf_summer_eur_mwh"}


def spread_backtest(frame: pd.DataFrame, deviation_threshold_pp: float = 5.0,
                    cost_eur_mwh_per_contract: float = 0.04) -> pd.DataFrame:
    """Storage-deviation signal to a 1-MWh-equivalent winter/summer spread.

    Signal[t] = +1 if storage[t] is below seasonal reference by > threshold
              = -1 if above by > threshold; otherwise 0.
    Position[t] = signal[t-1], so P&L[t] = position[t] * Δspread[t]
                 − cost * abs(position[t] − position[t-1]).
    Daily closing marks and next-day fills are approximated by daily values.
    Contract IDs/rolls, spreads' bid-ask cost per leg and transaction timestamps
    are not represented; this is NOT a production-level executable strategy.
    """
    if deviation_threshold_pp < 0 or cost_eur_mwh_per_contract < 0:
        raise ValueError("Threshold and cost must be nonnegative")
    if not REQUIRED.issubset(frame):
        raise ValueError(f"Missing columns: {sorted(REQUIRED - set(frame))}")
    out = frame.copy()
    out["date"] = pd.to_datetime(out["date"], errors="raise")
    out = out.sort_values("date").reset_index(drop=True)
    if out["date"].duplicated().any():
        raise ValueError("Observation dates must be unique")
    numeric = list(REQUIRED - {"date"})
    if out[numeric].isna().any().any():
        raise ValueError("No missing market data allowed")
    if ((out[["storage_pct", "seasonal_reference_pct"]] < 0) |
        (out[["storage_pct", "seasonal_reference_pct"]] > 100)).any().any():
        raise ValueError("Storage percentages must fall in [0,100]")
    if (out[["ttf_winter_eur_mwh", "ttf_summer_eur_mwh"]] <= 0).any().any():
        raise ValueError("Forward prices must be positive")
    out["storage_deviation_pp"] = out["storage_pct"] - out["seasonal_reference_pct"]
    out["winter_summer_spread"] = out["ttf_winter_eur_mwh"] - out["ttf_summer_eur_mwh"]
    out["signal"] = np.select([out["storage_deviation_pp"] < -deviation_threshold_pp,
                                out["storage_deviation_pp"] > deviation_threshold_pp],
                               [1, -1], default=0).astype(int)
    out["position"] = out["signal"].shift(1).fillna(0).astype(int)
    out["spread_change"] = out["winter_summer_spread"].diff().fillna(0.0)
    out["turnover"] = out["position"].diff().fillna(out["position"]).abs()
    out["pnl_eur_per_mwh"] = out["position"] * out["spread_change"] - cost_eur_mwh_per_contract * out["turnover"]
    out["cumulative_pnl_eur_per_mwh"] = out["pnl_eur_per_mwh"].cumsum()
    return out


def summarize(df: pd.DataFrame) -> dict:
    pnl = df["pnl_eur_per_mwh"]
    return {"total_pnl_eur_per_mwh": float(pnl.sum()),
            "active_days": int(df["position"].ne(0).sum()),
            "position_changes": int((df["turnover"] > 0).sum()),
            "mean_daily_pnl_eur_per_mwh": float(pnl.mean()),
            "pnl_positive_days_fraction": float((pnl > 0).mean())}
