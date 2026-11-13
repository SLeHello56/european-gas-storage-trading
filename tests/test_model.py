import pandas as pd
import pytest
from gas_storage.model import spread_backtest, summarize


def data():
    return pd.DataFrame({"date": ["2025-01-01", "2025-01-02", "2025-01-03", "2025-01-04"],
      "storage_pct": [35., 65., 50., 50.],
      "seasonal_reference_pct": [50., 50., 50., 50.],
      "ttf_winter_eur_mwh": [42., 44., 43., 45.],
      "ttf_summer_eur_mwh": [40., 40., 40., 40.]})


def test_signals_shift_to_next_period():
    out = spread_backtest(data(), deviation_threshold_pp=5, cost_eur_mwh_per_contract=0)
    assert out.signal.tolist() == [1, -1, 0, 0]
    assert out.position.tolist() == [0, 1, -1, 0]
    assert out.pnl_eur_per_mwh.tolist() == pytest.approx([0., 2., 1., 0.])


def test_turnover_costs_on_position_changes():
    out = spread_backtest(data(), 5, 0.1)
    assert out.turnover.tolist() == [0., 1., 2., 1.]
    assert out.pnl_eur_per_mwh.tolist() == pytest.approx([0., 1.9, 0.8, -0.1])


def test_future_storage_not_in_past_position():
    original = spread_backtest(data(), 5, 0)
    altered = data()
    altered.loc[3, "storage_pct"] = 100
    updated = spread_backtest(altered, 5, 0)
    assert original.position.tolist() == updated.position.tolist()
    assert "total_pnl_eur_per_mwh" in summarize(original)


def test_invalid_storage():
    df = data()
    df.loc[0, "storage_pct"] = 101
    with pytest.raises(ValueError):
        spread_backtest(df)
