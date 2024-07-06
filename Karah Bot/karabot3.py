import csv
import os
from datetime import datetime, timedelta

# Define paths for CSV files
data_paths = {
    'AUDUSD': os.path.join('Data', 'AUDUSD_2024-07-04-00_00.csv'),
    'EURUSD': os.path.join('Data', 'EURUSD_2024-07-04-00_00.csv'),
    'GBPUSD': os.path.join('Data', 'GBPUSD_2024-07-04-00_00.csv'),
    'USDCAD': os.path.join('Data', 'USDCAD_2024-07-04-00_00.csv'),
    'USDJPY': os.path.join('Data', 'USDJPY_2024-07-04-00_00.csv')
}

# Read CSV file and handle missing 'Timestamp' or 'Close' key
def read_csv(path):
    data = []
    with open(path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if 'Timestamp' in row and 'Close' in row:
                try:
                    row['Timestamp'] = datetime.strptime(row['Timestamp'], '%Y-%m-%d %H:%M:%S')
                    row['Close'] = float(row['Close'])
                    data.append(row)
                except ValueError as e:
                    print(f"Error parsing row: {row}, error: {e}")
            else:
                print(f"'Timestamp' or 'Close' not found in {path}")
    return data

# Convert timestamps to datetime objects and parse float values for 'Close'
def to_datetime(data):
    for row in data:
        try:
            row['Timestamp'] = datetime.strptime(row['Timestamp'], '%Y-%m-%d %H:%M:%S')
            row['Close'] = float(row['Close'])
        except ValueError as e:
            print(f"Error converting data: {row}, error: {e}")

# Simplified trend analysis based on past prices
def analyze_trends(current_price, past_prices):
    avg_past_price = sum(past_prices) / len(past_prices)
    return "buy" if current_price < avg_past_price else "sell"

# Placeholder function to simulate placing an order
def place_order(pair, order_type, price, tp, sl):
    print(f"{order_type.capitalize()} order placed for {pair} at {price:.5f}. TP: {tp:.5f}, SL: {sl:.5f}")

# Simulated account balance
account_balance = 10000.0  # Initial balance

# Calculate take profit and stop loss based on balance
def calculate_tp_sl(balance, current_price):
    tp = current_price * 1.05  # 5% increase
    sl = current_price * 0.99  # 1% decrease
    return tp, sl

# Update account balance based on trade outcome
def update_balance(order_type, price, tp, sl):
    global account_balance
    if order_type == "buy":
        account_balance += (tp - price) * 0.01  # Simulate profit from trade
    elif order_type == "sell":
        account_balance += (price - tp) * 0.01  # Simulate profit from trade
    print(f"Updated account balance: {account_balance:.2f}")

# Simulate continuous trading during market hours (Sunday 5 PM EST to Friday 5 PM EST)
def run_trading_bot(data):
    market_open = datetime(2024, 7, 7, 17)  # Sunday 5 PM EST
    market_close = datetime(2024, 7, 12, 17)  # Friday 5 PM EST
    current_time = market_open
    initial_balance = account_balance
    target_balance = initial_balance * 1.30  # 30% daily return target

    while current_time <= market_close:
        if account_balance >= target_balance:
            print("Daily return target achieved. Stopping trading.")
            break

        for pair, df in data.items():
            past_prices = [row['Close'] for row in df if row.get('Timestamp') < current_time]
            if past_prices:
                current_price = past_prices[-1]
                decision = analyze_trends(current_price, past_prices[-50:])  # Use last 50 prices for trend analysis
                tp, sl = calculate_tp_sl(account_balance, current_price)

                if decision == "buy":
                    place_order(pair, "buy", current_price, tp, sl)
                    update_balance("buy", current_price, tp, sl)
                elif decision == "sell":
                    place_order(pair, "sell", current_price, tp, sl)
                    update_balance("sell", current_price, tp, sl)

        current_time += timedelta(minutes=5)

# Read and preprocess data
data = {pair: read_csv(path) for pair, path in data_paths.items()}
for df in data.values():
    to_datetime(df)

# Print the first few rows of each dataset to verify
for pair, df in data.items():
    print(f"{pair} data:")
    for row in df[:5]:  # Print first 5 rows
        print(row)
    print()

# Run the trading bot
run_trading_bot(data)
