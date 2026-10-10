import yfinance as yf
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
import warnings

warnings.filterwarnings('ignore')

# 1. FETCH & CLEAN DATA
def fetch_data(tickers, start_date, end_date):
    print("Downloading data from Yahoo Finance...")
    data = yf.download(tickers, start=start_date, end=end_date, progress=False)
    
    # Handle new yfinance API (Adj Close removed in newer versions)
    if 'Adj Close' in data.columns.levels[0]:
        data = data['Adj Close']
    else:
        data = data['Close']
    
    # Drop failed tickers, forward-fill missing days, drop remaining NaNs
    data = data.dropna(axis=1, how='all').ffill().dropna()
    
    # Remove timezones for easier plotting
    if data.index.tz is not None:
        data.index = data.index.tz_localize(None)
        
    print(f"Data fetched. Shape: {data.shape}")
    return data

# 2. VECTORIZED SCREENER (Fast Correlation Filter)
def find_correlated_pairs(prices, threshold=0.80):
    print("Calculating correlation matrix...")
    returns = prices.pct_change().dropna()
    corr_matrix = returns.corr()
    
    pairs = []
    # Check upper triangle only to avoid duplicate pairs
    for i in range(len(corr_matrix.columns)):
        for j in range(i + 1, len(corr_matrix.columns)):
            if abs(corr_matrix.iloc[i, j]) > threshold:
                pairs.append((corr_matrix.columns[i], corr_matrix.columns[j]))
                
    print(f"Found {len(pairs)} highly correlated pairs.")
    return pairs

# 3. ANALYTICS ENGINE (Cointegration & Half-Life)
def analyze_pairs(prices, pairs):
    print("Running Cointegration and Half-Life tests...")
    results = []
    
    for stock_a, stock_b in pairs:
        Y = prices[stock_a]
        X = prices[stock_b]
        
        # 1. Find hedge ratio (Beta) using OLS regression
        X_const = sm.add_constant(X)
        model = sm.OLS(Y, X_const).fit()
        beta = model.params[stock_b]
        alpha = model.params['const']
        
        # 2. Calculate spread and run ADF test for stationarity
        spread = Y - (beta * X + alpha)
        adf_result = adfuller(spread, autolag='AIC')
        p_value = adf_result[1]
        
        # Keep only stationary spreads (p < 0.05)
        if p_value < 0.05:
            # 3. Calculate Half-Life (Ornstein-Uhlenbeck process)
            spread_lag = spread.shift(1).dropna()
            spread_diff = spread.diff().dropna()
            spread_lag, spread_diff = spread_lag.align(spread_diff, join='inner')
            
            ou_model = sm.OLS(spread_diff, sm.add_constant(spread_lag)).fit()
            theta = ou_model.params.iloc[1]
            
            if theta < 0: # Mean reverting
                half_life = -np.log(2) / theta
                
                # Keep only pairs with reasonable half-life (1 to 30 days)
                if 1 < half_life < 30:
                    # 4. Calculate Rolling Z-Score
                    window = 30
                    rolling_mean = spread.rolling(window=window).mean()
                    rolling_std = spread.rolling(window=window).std()
                    z_score = (spread - rolling_mean) / rolling_std
                    
                    results.append({
                        'Stock_A': stock_a,
                        'Stock_B': stock_b,
                        'Beta': beta,
                        'Alpha': alpha,
                        'ADF_p_value': p_value,
                        'Half_Life': half_life,
                        'Current_Z_Score': z_score.iloc[-1]
                    })
                    
    leaderboard = pd.DataFrame(results)
    if not leaderboard.empty:
        leaderboard['Pair'] = leaderboard['Stock_A'] + ' - ' + leaderboard['Stock_B']
        leaderboard = leaderboard.sort_values('ADF_p_value').reset_index(drop=True)
        print(f"Found {len(leaderboard)} valid pairs.")
    else:
        print("No valid pairs found. Try lowering correlation threshold.")
        
    return leaderboard

# MAIN EXECUTION
if __name__ == "__main__":
    tickers = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM', 'V', 'JNJ',
        'WMT', 'PG', 'MA', 'DIS', 'HD', 'BAC', 'XOM', 'PFE', 'CSCO', 'VZ',
        'ADBE', 'NFLX', 'INTC', 'T', 'MRK', 'PEP', 'ABT', 'KO', 'TMO', 'AVGO',
        'CMCSA', 'WFC', 'COST', 'CVS', 'ACN', 'LLY', 'TXN', 'NKE', 'DHR', 'QCOM',
        'UNP', 'BMY', 'PM', 'LOW', 'HON', 'UNH', 'ORCL', 'IBM', 'GE', 'CAT'
    ]
    
    start_date = "2022-01-01"
    end_date = "2024-01-01"
    
    prices_df = fetch_data(tickers, start_date, end_date)
    prices_df.to_csv('prices.csv')
    
    correlated_pairs = find_correlated_pairs(prices_df, threshold=0.80)
    
    if correlated_pairs:
        leaderboard_df = analyze_pairs(prices_df, correlated_pairs)
        
        if not leaderboard_df.empty:
            leaderboard_df.to_csv('leaderboard.csv', index=False)
            print("Leaderboard saved as 'leaderboard.csv'")
            
            # --- Print Trade Signals for the Best Pair ---
            best_pair = leaderboard_df.iloc[0]
            stock_a = best_pair['Stock_A']
            stock_b = best_pair['Stock_B']
            beta = best_pair['Beta']
            alpha = best_pair['Alpha']
            
            print(f"\n--- Signals for {stock_a} - {stock_b} ---")
            Y = prices_df[stock_a]
            X = prices_df[stock_b]
            spread = Y - (beta * X + alpha)
            
            rolling_mean = spread.rolling(window=30).mean()
            rolling_std = spread.rolling(window=30).std()
            z_score = (spread - rolling_mean) / rolling_std
            
            # FIX: Initialize as empty string, not integer 0
            signals_df = pd.DataFrame({'Z_Score': z_score, 'Signal': ''})
            
            signals_df.loc[signals_df['Z_Score'] > 2, 'Signal'] = 'SHORT SPREAD (Sell Y, Buy X)'
            signals_df.loc[signals_df['Z_Score'] < -2, 'Signal'] = 'LONG SPREAD (Buy Y, Sell X)'
            signals_df.loc[abs(signals_df['Z_Score']) < 0.5, 'Signal'] = 'EXIT (Close Both)'
            
            active_signals = signals_df[signals_df['Signal'] != '']
            print(active_signals.tail(10))