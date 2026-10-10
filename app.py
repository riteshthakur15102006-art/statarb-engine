import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(layout="wide", page_title="StatArb Dashboard", page_icon="📈")

# Cache data for faster loading
@st.cache_data
def load_data():
    prices = pd.read_csv('prices.csv', index_col=0, parse_dates=True)
    leaderboard = pd.read_csv('leaderboard.csv')
    return prices, leaderboard

try:
    prices, leaderboard = load_data()
except FileNotFoundError:
    st.error("Data not found. Run `engine.py` first.")
    st.stop()

st.sidebar.title("🔍 StatArb Screener")
st.sidebar.markdown("Select a pair to view the execution chart.")

st.title("📊 Market Neutral Statistical Arbitrage Dashboard")
st.markdown("### Leaderboard: Top Cointegrated Pairs")

st.dataframe(leaderboard[['Pair', 'ADF_p_value', 'Half_Life', 'Current_Z_Score', 'Beta']].style.format({
    'ADF_p_value': '{:.4f}',
    'Half_Life': '{:.2f}',
    'Current_Z_Score': '{:.2f}',
    'Beta': '{:.2f}'
}), use_container_width=True)

st.markdown("---")
st.markdown("### Execution View")

if leaderboard.empty:
    st.warning("No cointegrated pairs found.")
    st.stop()

selected_pair = st.selectbox("Select a Pair to Analyze", leaderboard['Pair'].tolist())
row = leaderboard[leaderboard['Pair'] == selected_pair].iloc[0]

stock_a = row['Stock_A']
stock_b = row['Stock_B']
beta = row['Beta']
alpha = row['Alpha']

# Recalculate spread and z-score for the selected pair
Y = prices[stock_a]
X = prices[stock_b]
spread = Y - (beta * X + alpha)

rolling_mean = spread.rolling(window=30).mean()
rolling_std = spread.rolling(window=30).std()
z_score = (spread - rolling_mean) / rolling_std

# Generate signals
signal = pd.Series(0, index=z_score.index)
signal[z_score > 2] = -1  # Short spread
signal[z_score < -2] = 1  # Long spread
signal[abs(z_score) < 0.5] = 0 # Exit

# --- 3-Panel Chart ---
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                    subplot_titles=("Normalized Price Chart", "Stationary Spread", "Z-Score Action Chart"),
                    vertical_spacing=0.08)

# Panel 1: Normalized Prices
norm_a = Y / Y.iloc[0]
norm_b = X / X.iloc[0]
fig.add_trace(go.Scatter(x=norm_a.index, y=norm_a, name=f"{stock_a} (Norm)", line=dict(color='cyan', width=2)), row=1, col=1)
fig.add_trace(go.Scatter(x=norm_b.index, y=norm_b, name=f"{stock_b} (Norm)", line=dict(color='orange', width=2)), row=1, col=1)

# Panel 2: Spread
fig.add_trace(go.Scatter(x=spread.index, y=spread, name="Spread", line=dict(color='purple', width=2)), row=2, col=1)
fig.add_trace(go.Scatter(x=rolling_mean.index, y=rolling_mean, name="Rolling Mean", line=dict(color='white', dash='dash', width=1.5)), row=2, col=1)

# Panel 3: Z-Score
fig.add_trace(go.Scatter(x=z_score.index, y=z_score, name="Z-Score", line=dict(color='lime', width=2)), row=3, col=1)
fig.add_hline(y=2, line_dash="dash", line_color="red", row=3, col=1)
fig.add_hline(y=-2, line_dash="dash", line_color="red", row=3, col=1)
fig.add_hline(y=0, line_dash="solid", line_color="gray", row=3, col=1)

# Plot signals on Z-score
long_entries = z_score[signal == 1]
short_entries = z_score[signal == -1]

fig.add_trace(go.Scatter(x=long_entries.index, y=long_entries, mode='markers', 
                         name='Long Entry', marker=dict(color='green', symbol='triangle-up', size=10)), row=3, col=1)
fig.add_trace(go.Scatter(x=short_entries.index, y=short_entries, mode='markers', 
                         name='Short Entry', marker=dict(color='red', symbol='triangle-down', size=10)), row=3, col=1)

fig.update_layout(height=900, template='plotly_dark', showlegend=True,
                  title_text=f"Execution View: {selected_pair} (Beta: {beta:.2f}, Half-Life: {row['Half_Life']:.2f} days)")
st.plotly_chart(fig, use_container_width=True)