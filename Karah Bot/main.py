import csv
import os
from datetime import datetime, timedelta
from statistics import mean

# Define paths
data_paths = {
    'AUDUSD': os.path.join('Data', 'AUDUSD_2024-07-04-00_00.csv'),
    'EURUSD': os.path.join('Data', 'EURUSD_2024-07-04-00_00.csv'),
    'GBPUSD': os.path.join('Data', 'GBPUSD_2024-07-04-00_00.csv'),
    'USDCAD': os.path.join('Data', 'USDCAD_2024-07-04-00_00.csv'),
    'USDJPY': os.path.join('Data', 'USDJPY_2024-07-04-00_00.csv')
}

def read_csv(path):
    with open(path, mode='r') as file:
        reader = csv.DictReader(file)
        return list(reader)

# Read data
data = {pair: read_csv(path) for pair, path in data_paths.items()}

def to_datetime(data):
    for row in data:
        row['Timestamp'] = datetime.strptime(row['Timestamp'], '%Y-%m-%d %H:%M:%S')
        row['Close'] = float(row['Close'])

for df in data.values():
    to_datetime(df)

def compute_sma(data, window):
    sma = []
    for i in range(len(data)):
        if i < window:
            sma.append(None)
        else:
            close_prices = [data[j]['Close'] for j in range(i - window, i)]
            sma.append(mean(close_prices))
    return sma

def compute_rsi(data, window):
    rsi = []
    for i in range(len(data)):
        if i < window:
            rsi.append(None)
        else:
            gains, losses = 0, 0
            for j in range(i - window, i):
                change = data[j]['Close'] - data[j - 1]['Close']
                if change > 0:
                    gains += change
                else:
                    losses -= change
            avg_gain = gains / window
            avg_loss = losses / window
            rs = avg_gain / avg_loss if avg_loss != 0 else 0
            rsi.append(100 - (100 / (1 + rs)))
    return rsi

def add_indicators(data):
    sma_50 = compute_sma(data, 50)
    sma_200 = compute_sma(data, 200)
    rsi = compute_rsi(data, 14)
    for i in range(len(data)):
        data[i]['SMA_50'] = sma_50[i]
        data[i]['SMA_200'] = sma_200[i]
        data[i]['RSI'] = rsi[i]

for pair, df in data.items():
    add_indicators(df)

def trading_signal(data):
    lot_size = 0.01
    tp_percentage = 0.005  # 0.50%
    sl_fixed = 0.30  # 30 cents

    for row in data:
        row['Signal'] = 0
        row['Entry_Price'] = None
        row['TP'] = None
        row['SL'] = None

        if row['SMA_50'] and row['SMA_200'] and row['RSI']:
            if row['Close'] > row['SMA_50'] and row['Close'] > row['SMA_200'] and row['RSI'] < 30:
                row['Signal'] = 1
                row['Entry_Price'] = row['Close']
                row['TP'] = row['Close'] * (1 + tp_percentage)
                row['SL'] = row['Close'] - sl_fixed
            elif row['Close'] < row['SMA_50'] and row['Close'] < row['SMA_200'] and row['RSI'] > 70:
                row['Signal'] = -1
                row['Entry_Price'] = row['Close']
                row['TP'] = row['Close'] * (1 - tp_percentage)
                row['SL'] = row['Close'] + sl_fixed

for pair, df in data.items():
    trading_signal(df)

def write_csv(data, path):
    fieldnames = data[0].keys()
    with open(path, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

# Save the processed data with trading signals for further use
output_dir = os.path.join('ProcessedData')
os.makedirs(output_dir, exist_ok=True)
for pair, df in data.items():
    output_path = os.path.join(output_dir, f'{pair}_processed.csv')
    write_csv(df, output_path)

# Simulating continuous trading (market hours: 24 hours from Sunday 5 PM EST to Friday 5 PM EST)
market_open = datetime(2024, 7, 7, 17)  # Sunday 5 PM EST
market_close = datetime(2024, 7, 12, 17)  # Friday 5 PM EST
current_time = market_open

while current_time <= market_close:
    for pair, df in data.items():
        for row in df:
            if row['Timestamp'] == current_time:
                if row['Signal'] == 1:
                    print(f"Buy Signal for {pair} at {row['Entry_Price']:.5f}. TP: {row['TP']:.5f}, SL: {row['SL']:.5f}")
                elif row['Signal'] == -1:
                    print(f"Sell Signal for {pair} at {row['Entry_Price']:.5f}. TP: {row['TP']:.5f}, SL: {row['SL']:.5f}")
    current_time += timedelta(minutes=5)
