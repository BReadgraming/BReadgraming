import pandas as pd
import os

audusd_path = os.path.join('..', 'Data', 'AUDUSD_2024-07-04-00_00.csv')
eurusd_path = os.path.join('..', 'Data', 'EURUSD_2024-07-04-00_00.csv')
gbpusd_path = os.path.join('..', 'Data', 'GBPUSD_2024-07-04-00_00.csv')
usdcad_path = os.path.join('..', 'Data', 'USDCAD_2024-07-04-00_00.csv')
usdjpy_path = os.path.join('..', 'Data', 'USDJPY_2024-07-04-00_00.csv')

audusd_data = pd.read.csv(audusd_path)
eurusd_data = pd.read_csv(eurusd_path)
gbpusd_data = pd.read_csv(gbpusd_path)
usdcad_data = pd.read_csv(usdcad_path)
usdjpy_data = pd.read_csv(usdjpy_path)
