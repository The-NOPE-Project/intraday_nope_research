import numpy as np
import pandas as pd
from scipy import stats
from dateutil import parser
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import statistics
from collections import defaultdict
import json

DATA_PATH = '../processed_data/'

all_data = pd.read_csv(DATA_PATH + 'allDataCombined.csv')
price_data = pd.read_csv(DATA_PATH + 'priceData.csv')
df = pd.merge(all_data, price_data, on="timestamp")
df['date'] = df['timestamp'].apply(lambda x: parser.parse(x).date())
df['time'] = df['timestamp'].apply(lambda x: parser.parse(x).strftime("%H:%M:%S"))
corr = []
corr_all = []
pnl = defaultdict(list)
index = 0

def backtest_short(day_group, short_entry, short_exit, stop, tolerance = 3):
    values = []
    trade_in_progress = False
    entry_price = None
    exit_price = None
    total_pnl = 0
    for index, row in day_group.iterrows():
        if row['NOPE_busVolume']*100 >= short_entry and not trade_in_progress and row['time'] > '09:45:00' and row['time'] < '15:30:00':
            entry_price = (row['NOPE_busVolume']*100, row['time'], row['active_underlying_price'])
            trade_in_progress = True
        if trade_in_progress and (row['NOPE_busVolume']*100 <= short_exit or row['NOPE_busVolume'] >= stop):
            exit_price = (row['NOPE_busVolume']*100,row['time'],row['active_underlying_price'])
            values.append((entry_price, exit_price))
            total_pnl = total_pnl + (entry_price[2] - exit_price[2])
            trade_in_progress = False
            entry_price = None
            exit_price = None
        if row['time'] == '16:00:00':
            if trade_in_progress:
                exit_price = (row['NOPE_busVolume']*100,row['time'],row['active_underlying_price'])
                values.append((entry_price, exit_price))
                total_pnl = total_pnl + (entry_price[2] - exit_price[2])
                trade_in_progress = False
                entry_price = None
                exit_price = None
            break
    return (values, total_pnl)

def backtest_long(day_group, long_entry, long_exit, stop, tolerance = 3):
    values = []
    trade_in_progress = False
    entry_price = None
    exit_price = None
    total_pnl = 0
    for index, row in day_group.iterrows():
        if row['NOPE_busVolume']*100 <= long_entry and not trade_in_progress and row['time'] > '09:45:00' and row['time'] < '15:30:00':
            entry_price = (row['NOPE_busVolume']*100, row['time'], row['active_underlying_price'])
            trade_in_progress = True
        if trade_in_progress and (row['NOPE_busVolume']*100 >= long_exit or row['NOPE_busVolume'] <= stop):
            exit_price = (row['NOPE_busVolume']*100,row['time'],row['active_underlying_price'])
            values.append((entry_price, exit_price))
            total_pnl = total_pnl + (exit_price[2] - entry_price[2])
            trade_in_progress = False
            entry_price = None
            exit_price = None
        if row['time'] == '16:00:00':
            if trade_in_progress:
                exit_price = (row['NOPE_busVolume']*100,row['time'],row['active_underlying_price'])
                values.append((entry_price, exit_price))
                total_pnl = total_pnl + (exit_price[2] - entry_price[2])
                trade_in_progress = False
                entry_price = None
                exit_price = None
            break
    return (values, total_pnl)

total_pnl = defaultdict(tuple)
real_total_pnl = 0
for name, group in df.groupby('date'):
    total_pnl[str(name)] = backtest_long(group, -70, -40, -100)
    real_total_pnl = real_total_pnl + total_pnl[str(name)][1]

print(json.dumps(total_pnl, indent=1))
print(real_total_pnl)
