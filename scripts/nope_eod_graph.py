import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from dateutil import parser
import statsmodels.tsa.stattools as ts
from collections import defaultdict

# Reading in files
DATA_PATH = '../processed_data/'

all_data = pd.read_csv(DATA_PATH + 'parsedNetDelta2020-01.csv')
price_data = pd.read_csv(DATA_PATH + 'priceData.csv')
df = pd.merge(all_data, price_data, on="timestamp")

# Parsing in files
df['date'] = df['timestamp'].apply(lambda x: parser.parse(x).date())
df['time'] = df['timestamp'].apply(lambda x: parser.parse(x).strftime("%H:%M:%S"))

# Making an array to store dates and NOPE End of day
# Note: We include two different ways to do so
date = []
nope_EOD = []

# for index, row in df.iterrows() :
    # if (row['time'] == '16:00:00') :
        # date.append(row['date'].strftime("%d/%b/%Y"))
        # nope_EOD.append(row['NOPE_busVolume']*100)
        
for row in df.itertuples() :
    if  (row.time == '16:00:00') :
        # print(row.date)
        # print(row.date.strftime("%d/%b/%Y"))
        # print(row.date.strftime("%Y-%b-%d"))
        date.append(row.date)
        nope_EOD.append(row.NOPE_busVolume*100)

# Uncomment if you don't want the graph
# exit()

# Plotting them on a graph
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%d/%b/%Y"))
# Uncomment this line if you want to show all the dates
# plt.gca().xaxis.set_major_locator(mdates.DayLocator())
plt.plot(date,nope_EOD)
plt.gcf().autofmt_xdate()
plt.show()