# 📊 Market Neutral Statistical Arbitrage Engine

🔗 Live Interactive Dashboard: https://market-neutral-statistical-arbitrage.streamlit.app/

A fully automated, market-neutral statistical arbitrage engine built in Python. This project scans a universe of S&P 50 stocks, identifies cointegrated pairs using the Engle-Granger two-step method, and generates mean-reversion trading signals based on rolling Z-scores.

The interactive dashboard is built with Streamlit and Plotly, providing a dark-mode UI to visualize normalized prices, stationary spreads, and exact execution points.

## 🚀 Features

- Vectorized Screener: Uses fast correlation matrix filtering to reduce 1,225 possible pairs to highly correlated assets in milliseconds.
- Cointegration Testing: Implements the Engle-Granger two-step method (OLS regression + Augmented Dickey-Fuller test) to find stationary spreads.
- Ornstein-Uhlenbeck Half-Life: Calculates the half-life of mean reversion to filter out pairs that tie up capital for too long (only keeps 1-30 days).
- Dynamic Z-Score Signals: Generates Long/Short spread signals when the Z-score crosses +2 or -2, and exits when it reverts to 0.
- Interactive Dashboard: A 3-panel Plotly chart inside a Streamlit app that visualizes:
  1. Normalized Prices (Asset A vs Asset B)
  2. The Stationary Spread (with rolling mean)
  3. The Z-Score Action Chart (with exact entry/exit markers)

## 📂 Project Structure

statarb-engine/
├── engine.py             # Main backend logic (data fetch, screening, analytics)
├── app.py                # Streamlit interactive dashboard
├── prices.csv            # Generated dataset of aligned asset prices
├── leaderboard.csv       # Generated list of top cointegrated pairs
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation

## 🛠️ Installation & Usage

1. Clone the repository:
   git clone https://github.com/riteshthakur15102006-art/statarb-engine.git
   cd statarb-engine

2. Install dependencies:
   pip install -r requirements.txt

3. Run the Engine (Generates Data):
   python engine.py
   (This will download 2 years of data, run the cointegration tests, and save prices.csv and leaderboard.csv.)

4. Launch the Dashboard:
   streamlit run app.py

## 📈 How the Strategy Works (Market Neutral)

The core philosophy is Market Neutrality. We do not care if the S&P 500 goes up or down. We only care that the mathematical spread between two assets reverts to its historical mean.

The Spread:
We find the hedge ratio (Beta) using OLS regression:
Spread = Price(Y) - [Beta * Price(X) + Alpha]

The Signals:
We calculate a rolling Z-score of the spread over a 30-day window:
- Z-Score > +2.0: Short the Spread (Short Asset Y, Long Asset X)
- Z-Score < -2.0: Long the Spread (Long Asset Y, Short Asset X)
- Z-Score ≈ 0: Exit both positions.

## 📚 Research Papers Behind the Code

This project is deeply rooted in academic research:
1. Engle, R. F., & Granger, C. W. J. (1987). Co-integration and error correction: Representation, estimation, and testing. Econometrica.
2. Gatev, E., Goetzmann, W. N., & Rouwenhorst, K. G. (2006). Pairs trading: Performance of a relative-value arbitrage rule. The Review of Financial Studies.
3. Avellaneda, M., & Lee, J.-H. (2010). Statistical arbitrage in the US equities market. Quantitative Finance.

## ⚠️ Disclaimer

This project is for educational purposes only. It is not financial advice. Past performance does not guarantee future results. Always do your own research before deploying any capital.
