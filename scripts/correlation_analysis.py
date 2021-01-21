import numpy as np
import pandas as pd
from scipy import stats
from dateutil import parser
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import statistics

from scripts.simple_backtest_reversions import backtest_long

DATA_PATH = '../processed_data/'

all_data = pd.read_csv(DATA_PATH + 'allDataCombined.csv')
price_data = pd.read_csv(DATA_PATH + 'priceData.csv')
df = pd.merge(all_data, price_data, on="timestamp")
df['date'] = df['timestamp'].apply(lambda x: parser.parse(x).date())
corr = []
corr_all = []
dates = []
index = 0

for name, group in df.groupby('date'):
    backtest_long(group, -60, -30, -100)
    exit()
    index = index + 1
    if len(group[group['NOPE_allVolume'].isna()]):
        continue
    group['spy_change'] = group['active_underlying_price'].shift(1)
    group['spy_change'] = 100*(group['active_underlying_price']-group['spy_change'])/group['spy_change']
    group['prior_spy_change'] = group['spy_change'].shift(1)
    group = group[:-1]
    corr.append(stats.pearsonr(group['spy_change'], group['NOPE_busVolume'])[0])
    corr_all.append(stats.spearmanr(group['shifted_spy_change'], group['NOPE_busVolume'])[0])
    dates.append(index)

print(statistics.median(corr_all))
plt.plot(dates, corr_all)
plt.show()
