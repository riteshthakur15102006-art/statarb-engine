# 📊 Market Neutral Statistical Arbitrage Engine

🔗 **Live Interactive Dashboard:** [https://market-neutral-statistical-arbitrage.streamlit.app/](https://market-neutral-statistical-arbitrage.streamlit.app/)

A fully automated, market-neutral statistical arbitrage engine built in Python. This project scans a universe of S&P 50 stocks, identifies cointegrated pairs using the Engle-Granger two-step method, and generates mean-reversion trading signals based on rolling Z-scores. 

The interactive dashboard is built with Streamlit and Plotly, providing a dark-mode UI to visualize normalized prices, stationary spreads, and exact execution points.

## 🚀 Features

- **Vectorized Screener:** Uses fast correlation matrix filtering to reduce 1,225 possible pairs to highly correlated assets in milliseconds.
- **Cointegration Testing:** Implements the Engle-Granger two-step method (OLS regression + Augmented Dickey-Fuller test) to find stationary spreads.
- **Ornstein-Uhlenbeck Half-Life:** Calculates the half-life of mean reversion to filter out pairs that tie up capital for too long (only keeps 1-30 days).
- **Dynamic Z-Score Signals:** Generates Long/Short spread signals when the Z-score crosses +2 or -2, and exits when it reverts to 0.
- **Interactive Dashboard:** A 3-panel Plotly chart inside a Streamlit app that visualizes:
  1. Normalized Prices (Asset A vs Asset B)
  2. The Stationary Spread (with rolling mean)
  3. The Z-Score Action Chart (with exact entry/exit markers)

## 📂 Project Structure

```text
statarb-engine/
│
├── engine.py             # Main backend logic (data fetch, screening, analytics)
├── app.py                # Streamlit interactive dashboard
├── prices.csv            # Generated dataset of aligned asset prices
├── leaderboard.csv       # Generated list of top cointegrated pairs
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
