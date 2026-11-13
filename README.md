# European Gas Trading & Storage Analytics

European gas-market research in Python: TTF summer/winter spread metrics, storage fill-rate analytics, rolling signals and backtesting with lagged positions and illustrative transaction costs.

## Run

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
python examples/run_demo.py
streamlit run app.py
```

Synthetic gas-market examples are provided; optional AGSI historical storage data require an appropriate API key. Historical TTF futures curves are not freely reproducible from storage figures. Educational, not a trading recommendation.
