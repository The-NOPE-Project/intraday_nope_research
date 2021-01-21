import numpy as np
import pandas as pd
from scipy import stats
from dateutil import parser
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import statistics
import statsmodels.tsa.stattools as ts
from collections import defaultdict

from data_prep import gen_df
df = gen_df()

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
