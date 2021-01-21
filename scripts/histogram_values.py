import numpy as np
import pandas as pd
from scipy import stats
from dateutil import parser
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import statistics
import statsmodels.tsa.stattools as ts
from collections import defaultdict

DATA_PATH = '../processed_data/'

df = pd.read_csv(DATA_PATH + 'allDataCombined.csv')
#price_data = pd.read_csv(DATA_PATH + 'priceData.csv')
#df = pd.merge(all_data, price_data, on="timestamp")
df['date'] = df['timestamp'].apply(lambda x: parser.parse(x).date())
df['time'] = df['timestamp'].apply(lambda x: parser.parse(x).strftime("%H:%M:%S"))
eod_nope = df[df['time'] == '16:00:00']['NOPE_busVolume']*100
intraday_nope = df[df['time'] < '15:30:00']['NOPE_busVolume']*100
dic = defaultdict(float)
for name, group in df.groupby('date'):
    if len(group[group['NOPE_busVolume'].isna()]):
        continue
    dic[name] = ts.adfuller(group['NOPE_busVolume'])[1]

print(statistics.mean(eod_nope))
exit()
plt.hist(eod_nope, density=True, bins=20, alpha=0.5, label='EOD')
plt.hist(intraday_nope, density=True, bins=20, alpha=0.5, label='Intraday')
plt.legend(loc='upper right')
#intra = np.histogram(intraday_nope, bins=np.arange(-300, 300, 10))
plt.show()
