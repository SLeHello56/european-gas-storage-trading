from gas_storage.data import synthetic_gas_market
from gas_storage.model import spread_backtest, summarize

if __name__ == "__main__":
    result = spread_backtest(synthetic_gas_market())
    print(summarize(result))
    print(result[["date", "storage_deviation_pp", "signal", "position", "pnl_eur_per_mwh"]].head(12).to_string(index=False))
