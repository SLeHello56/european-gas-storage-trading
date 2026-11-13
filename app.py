import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from gas_storage.data import synthetic_gas_market
from gas_storage.model import spread_backtest, summarize

st.set_page_config(page_title="Gas Storage & TTF Trading", page_icon="🔥", layout="wide")
st.title("European Gas Trading & Storage Analytics")
st.caption("Research-only seasonal TTF spread backtest · synthetic examples, not GIE/ICE observations")
with st.sidebar:
    deviation = st.slider("Storage deviation trigger (percentage points)", 0.0, 20.0, 5.0, 0.5)
    cost = st.number_input("Turnover cost (€/MWh per 1 spread unit)", 0.0, 2.0, 0.04, step=0.01)
source = st.file_uploader("Optional CSV: date,storage_pct,seasonal_reference_pct,ttf_winter_eur_mwh,ttf_summer_eur_mwh", type="csv")
df = pd.read_csv(source) if source is not None else synthetic_gas_market()
try:
    out = spread_backtest(df, deviation, cost)
    m = summarize(out)
    a, b, c = st.columns(3)
    a.metric("Backtest total (€/MWh spread)", f'{m["total_pnl_eur_per_mwh"]:.2f}')
    b.metric("Days with position", m["active_days"])
    c.metric("Position changes", m["position_changes"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=out.date, y=out.storage_pct, name="Storage %"))
    fig.add_trace(go.Scatter(x=out.date, y=out.seasonal_reference_pct, name="Seasonal reference %", line=dict(dash="dash")))
    fig.update_layout(title="Storage fill vs seasonal norm", yaxis_title="Capacity filled (%)")
    st.plotly_chart(fig, use_container_width=True)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=out.date, y=out.winter_summer_spread, name="TTF winter/summer spread", yaxis="y1"))
    fig2.add_trace(go.Scatter(x=out.date, y=out.cumulative_pnl_eur_per_mwh, name="Cumulative model P&L", yaxis="y2"))
    fig2.update_layout(title="Mark-to-market spread and cumulative model P&L",
                       yaxis=dict(title="TTF spread (€/MWh)"), yaxis2=dict(title="Model P&L (€/MWh)", overlaying="y", side="right"))
    st.plotly_chart(fig2, use_container_width=True)
    st.dataframe(out, use_container_width=True, hide_index=True)
    st.download_button("Download signal & backtest", out.to_csv(index=False), "gas_spread_backtest.csv", "text/csv")
except (ValueError, TypeError, KeyError) as exc:
    st.error(f"Input validation error: {exc}")
st.warning("Educational strategy only: synthetic marks, no executable forward-contract selection, bid/ask, funding or actual GIE API feed.")
