import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from dateutil import parser
import statsmodels.tsa.stattools as ts
import datetime
from matplotlib.ticker import(MultipleLocator, AutoMinorLocator)

# Reading in files
DATA_PATH = '../processed_data/'

all_data = pd.read_csv(DATA_PATH + 'parsedNetDelta2020-01.csv')
price_data = pd.read_csv(DATA_PATH + 'priceData.csv')
df = pd.merge(all_data, price_data, on="timestamp")

# Parsing in files
df['date'] = df['timestamp'].apply(lambda x: parser.parse(x).date())
df['time'] = df['timestamp'].apply(lambda x: parser.parse(x).strftime("%H:%M:%S"))


#ask user for date
year = int(input("Which year: "))
month = int(input("Which month: "))
day = int(input("Which day: "))
date = datetime.datetime(year, month, day)

# Making an array to store time, NOPE, and SPY price
time = []
nope = []
spy_value = []

for row in df.itertuples() :
    if  (row.date == date.date()) :
        # print(row.date)
        time.append(row.time)
        nope.append(row.NOPE_busVolume*100)
        spy_value.append(row.active_underlying_price)
        
# Uncomment if you don't want the graph
# exit()

fig, ax1 = plt.subplots()

# NOPE line
color = 'tab:blue'
ax1.set_xlabel('time every 5 minutes')
ax1.set_ylabel('NOPE', color=color)
ax1.plot(time, nope, color=color)
ax1.tick_params(axis='y', labelcolor=color)

# SPY line
color = 'tab:red'
ax2 = ax1.twinx()
ax2.set_ylabel('SPY Price', color=color)
ax2.plot(time, spy_value, color=color)
ax2.tick_params(axis='y', labelcolor=color)

fig.tight_layout()
# fig.legend()

# The minor ticks are not really working
# plt.gca().xaxis.grid(True, which='minor')
# plt.gca().xaxis.set_minor_locator(AutoMinorLocator())

# Changing the format to hour:minute is not working
# fig.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

# The major ticks work, but no idea how to adjust besides using AutoDateLocator()
plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())

# This line does nothing idk why
fig.autofmt_xdate()

plt.show()