import csv
import os
from datetime import datetime, timedelta
import MetaTrader5 as mt5

# Define paths for CSV files
data_paths = {
    'AUDUSD': os.path.join('Data', 'AUDUSD_2024-07-04-00_00.csv'),
    'EURUSD': os.path.join('Data', 'EURUSD_2024-07-04-00_00.csv'),
    'GBPUSD': os.path.join('Data', 'GBPUSD_2024-07-04-00_00.csv'),
    'USDCAD': os.path.join('Data', 'USDCAD_2024-07-04-00_00.csv'),
    'USDJPY': os.path.join('Data', 'USDJPY_2024-07-04-00_00.csv')
}

# Read CSV file
def read_csv(path):
    with open(path, mode='r') as file:
        reader = csv.DictReader(file)
        return list(reader)

# Convert timestamps to datetime objects and parse float values for 'Close'
def to_datetime(data):
    for row in data:
        row['Timestamp'] = datetime.strptime(row['Timestamp'], '%Y-%m-%d %H:%M:%S')
        row['Close'] = float(row['Close'])

# Read and preprocess data
data = {pair: read_csv(path) for pair, path in data_paths.items()}
for df in data.values():
    to_datetime(df)

# Simplified trend analysis based on past prices
def analyze_trends(current_price, past_prices):
    avg_past_price = sum(past_prices) / len(past_prices)
    return "buy" if current_price < avg_past_price else "sell"

# Initialize MetaTrader5 connection
def connect_to_mt5():
    if not mt5.initialize():
        print("initialize() failed")
        mt5.shutdown()

# Get current account balance from MetaTrader5
def get_account_balance():
    account_info = mt5.account_info()
    if account_info is None:
        raise Exception("Failed to get account balance.")
    return account_info.balance

# Place order on MetaTrader5
def place_order_mt5(pair, order_type, price, tp, sl):
    symbol = pair
    lot = 0.01
    deviation = 20

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY if order_type == "buy" else mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": deviation,
        "magic": 234000,
        "comment": "Karah Bot order",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Order failed: {result.comment}")
    else:
        print(f"Order placed successfully: {result}")
    return result

# Calculate take profit and stop loss based on balance
def calculate_tp_sl(balance, current_price):
    tp = current_price * (1 + 0.05 * balance / current_price)  # 5% of balance
    sl = current_price * (1 - 0.01 * balance / current_price)  # 1% of balance
    return tp, sl

# Simulate continuous trading during market hours (Sunday 5 PM EST to Friday 5 PM EST)
def run_trading_bot(data):
    market_open = datetime(2024, 7, 7, 17)  # Sunday 5 PM EST
    market_close = datetime(2024, 7, 12, 17)  # Friday 5 PM EST
    current_time = market_open
    initial_balance = get_account_balance()
    target_balance = initial_balance * 1.30  # 30% daily return target

    connect_to_mt5()

    while current_time <= market_close:
        current_balance = get_account_balance()
        if current_balance >= target_balance:
            print("Daily return target achieved. Stopping trading.")
            break

        for pair, df in data.items():
            past_prices = [row['Close'] for row in df if row['Timestamp'] < current_time]
            if past_prices:
                current_price = past_prices[-1]
                decision = analyze_trends(current_price, past_prices[-50:])  # Use last 50 prices for trend analysis
                tp, sl = calculate_tp_sl(current_balance, current_price)

                if decision == "buy":
                    place_order_mt5(pair, "buy", current_price, tp, sl)
                elif decision == "sell":
                    place_order_mt5(pair, "sell", current_price, tp, sl)

        current_time += timedelta(minutes=5)

    mt5.shutdown()

# Run the trading bot
run_trading_bot(data)
