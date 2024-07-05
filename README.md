import pandas as pd
import numpy as np
import os

# Define paths
data_paths = {
    'AUDUSD': os.path.join('..', 'Data', 'AUDUSD_2024-07-04-00_00.csv'),
    'EURUSD': os.path.join('..', 'Data', 'EURUSD_2024-07-04-00_00.csv'),
    'GBPUSD': os.path.join('..', 'Data', 'GBPUSD_2024-07-04-00_00.csv'),
    'USDCAD': os.path.join('..', 'Data', 'USDCAD_2024-07-04-00_00.csv'),
    'USDJPY': os.path.join('..', 'Data', 'USDJPY_2024-07-04-00_00.csv')
}

# Read data
data = {pair: pd.read_csv(path) for pair, path in data_paths.items()}

# Convert timestamps to datetime and set as index
for df in data.values():
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df.set_index('Timestamp', inplace=True)

def compute_rsi(series, window):
    delta = series.diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def add_indicators(df):
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    df['RSI'] = compute_rsi(df['Close'], window=14)
    return df

def fibonacci_retracement_levels(high, low):
    diff = high - low
    return {
        'level_0.0': high,
        'level_0.236': high - 0.236 * diff,
        'level_0.382': high - 0.382 * diff,
        'level_0.5': high - 0.5 * diff,
        'level_0.618': high - 0.618 * diff,
        'level_0.764': high - 0.764 * diff,
        'level_1.0': low,
    }

def trading_signal(df):
    df['Signal'] = 0
    df['Entry_Price'] = np.nan
    df['TP'] = np.nan
    df['SL'] = np.nan

    lot_size = 0.01
    tp_percentage = 0.005  # 0.50%
    sl_fixed = 0.30  # 30 cents

    buy_conditions = (df['Close'] > df['SMA_50']) & (df['Close'] > df['SMA_200']) & (df['RSI'] < 30)
    sell_conditions = (df['Close'] < df['SMA_50']) & (df['Close'] < df['SMA_200']) & (df['RSI'] > 70)

    for i in range(len(df)):
        if buy_conditions[i]:
            df.at[df.index[i], 'Signal'] = 1
            df.at[df.index[i], 'Entry_Price'] = df['Close'][i]
            df.at[df.index[i], 'TP'] = df['Close'][i] * (1 + tp_percentage)
            df.at[df.index[i], 'SL'] = df['Close'][i] - sl_fixed
        elif sell_conditions[i]:
            df.at[df.index[i], 'Signal'] = -1
            df.at[df.index[i], 'Entry_Price'] = df['Close'][i]
            df.at[df.index[i], 'TP'] = df['Close'][i] * (1 - tp_percentage)
            df.at[df.index[i], 'SL'] = df['Close'][i] + sl_fixed

    return df

# Process data
for pair, df in data.items():
    data[pair] = add_indicators(df)
    data[pair] = trading_signal(df)

# Output processed data for verification
for pair, df in data.items():
    print(f"{pair} Data:")
    print(df[['Signal', 'Entry_Price', 'TP', 'SL']].dropna().head())

# Save the processed data with trading signals for further use
output_dir = os.path.join('..', 'ProcessedData')
os.makedirs(output_dir, exist_ok=True)
for pair, df in data.items():
    output_path = os.path.join(output_dir, f'{pair}_processed.csv')
    df.to_csv(output_path)
