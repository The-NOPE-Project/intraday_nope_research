import numpy as np
from numpy import *
import pandas as pd
from scipy import stats
from dateutil import parser
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import matplotlib.dates as mdates
import statistics

DATA_PATH = '../processed_data/'

df = pd.read_csv(DATA_PATH + 'allNOPEDataCombined.csv')
df['timestamp'] = df['timestamp'].apply(lambda x: pd.to_datetime(x))

dPriceLag = []
monthDateTime = pd.to_datetime('2020-01-02 9:35')
monthDateTime = monthDateTime.replace(day=1)
filterDatetime = pd.to_datetime('2020-01-02 9:35')
endFilterDatetime = pd.to_datetime('2020-02-02 16:35')
breakFilterDateTime = pd.to_datetime('2020-02-02 16:35')

# we need to setup our shifted data columns
df['NOPE_allVolume'] = df['NOPE_allVolume'].apply(lambda x: x*100.0)
df['NOPE_allVolumePrev'] = df['NOPE_allVolume'].shift()

df['deltaNope'] = df.apply(lambda x: x['NOPE_allVolume'] - x['NOPE_allVolumePrev'], axis=1)
df['deltaNope'].fillna(0.0 ,inplace = True)
df['deltaNopePrev'] = df['deltaNope'].shift()

df['deltaNope2'] = df.apply(lambda x: x['deltaNope'] - x['deltaNopePrev'], axis=1)
df['deltaNope2'].fillna(0.0 ,inplace = True)
df['deltaNope2Prev'] = df['deltaNope2'].shift()

df['active_underlying_price_prev'] = df['active_underlying_price'].shift()

df['deltaPrice'] = df.apply(lambda x: x['active_underlying_price'] - x['active_underlying_price_prev'], axis=1)
df['deltaPrice'].fillna(0.0 ,inplace = True)

df['deltaPrice+5'] = df['deltaPrice'].shift(-1)
df['deltaPrice+5'].fillna(0.0 ,inplace = True)

df['deltaPrice+10'] = df['deltaPrice'].shift(-2)
df['deltaPrice+10'].fillna(0.0 ,inplace = True)

df['dN-dN2'] = df.apply(lambda x: x['deltaNope'] - (0.5*x['deltaNope2Prev'] - 0.5*x['deltaNope2']), axis=1)
df['dN-dN2'].fillna(0.0 ,inplace = True)
print(df)

for index, row in df.iterrows():
    #print(index, row)
    if (index == 0):
        filterDatetime = row['timestamp']
        endFilterDatetime = row['timestamp'].replace(hour=16)
        continue
    else:
        # ignore the first entry in each day, as we just want to compare the data within a single day, and not the end
        # of the previous day to the open of the current
        if('9:35' in str(row['timestamp'])):
            # build the day range filter begin and end
            filterDatetime = row['timestamp']
            endFilterDatetime = row['timestamp'].replace(hour=16)
            monthDateTime = row['timestamp'].replace(day=1)
            print('Processing entry range: ', filterDatetime, ' ', endFilterDatetime)
            continue


        # use a split interpolate on the second order to function as the modeled second order
        # this is a reduction of cubic spline interpolation used in forward forecasting signal processing
        #df.at[index, 'dN-dN2'] = deltaNope - (0.5*lastDNope2 - 0.5*deltaNope2)

        # process data up to the latest data entry
        dNope = df[(df['timestamp'] <= filterDatetime) & (df['timestamp'] >= monthDateTime)]['deltaNope'].to_numpy()
        # where_are_NaNs = isnan(dNope)
        # dNope[where_are_NaNs] = 0.0

        dNope2 = df[(df['timestamp'] <= filterDatetime) & (df['timestamp'] >= monthDateTime)]['deltaNope2'].to_numpy()
        # where_are_NaNs = isnan(dNope2)
        # dNope2[where_are_NaNs] = 0.0

        dN_sub_dN2 = df[(df['timestamp'] <= filterDatetime) & (df['timestamp'] >= monthDateTime)]['dN-dN2'].to_numpy()
        # where_are_NaNs = isnan(dN_sub_dN2)
        # dN_sub_dN2[where_are_NaNs] = 0.0

        dPrice = df[(df['timestamp'] <= filterDatetime) & (df['timestamp'] >= monthDateTime)]['deltaPrice'].to_numpy()
        # where_are_NaNs = isnan(dPrice)
        # dPrice[where_are_NaNs] = 0.0

        dNopeRaw = df[(df['timestamp'] <= filterDatetime) & (df['timestamp'] >= monthDateTime)]['NOPE_allVolume'].to_numpy()
        # where_are_NaNs = isnan(dNopeRaw)
        # dNopeRaw[where_are_NaNs] = 0.0

        dPrice_p5 = df[(df['timestamp'] <= filterDatetime) & (df['timestamp'] >= monthDateTime)]['deltaPrice+5'].to_numpy()

        dPrice_p10 = df[(df['timestamp'] <= filterDatetime) & (df['timestamp'] >= monthDateTime)]['deltaPrice+10'].to_numpy()
        # dNope = df['deltaNope'].to_numpy()
        # dNope2 = df['deltaNope2'].to_numpy()
        # dN_sub_dN2 = df['dN-dN2'].to_numpy()
        # dPrice = df['deltaPrice'].to_numpy()
        # dNopeRaw = df['NOPE_allVolume'].to_numpy()

        df.at[index, 'corrLag'] = stats.spearmanr(dNope, dPrice_p5)[0]
        df.at[index, 'corrD2Lag'] = stats.spearmanr(dNope2, dPrice_p5)[0]
        dN_dN2_dP_t_plus_5 = stats.spearmanr(dN_sub_dN2, dPrice_p5)
        df.at[index, 'corrdN_sub_dN2_lag'] = dN_dN2_dP_t_plus_5[0]

        df.at[index, 'corrLag_2'] = stats.spearmanr(dNope, dPrice_p10)[0]
        df.at[index, 'corrD2Lag_2'] = stats.spearmanr(dNope2, dPrice_p10)[0]
        df.at[index, 'corrdN_sub_dN2_lag_2'] = stats.spearmanr(dN_sub_dN2, dPrice_p10)[0]

        #print(dNope, dPrice, dPriceLag, dPriceLag2)

        # compute our various correlations
        dN_dP = stats.spearmanr(dNope, dPrice)
        df.at[index, 'corr'] = dN_dP[0]
        df.at[index, 'corrRaw'] = stats.spearmanr(dNope, dNopeRaw)[0]

        dN2_dP = stats.spearmanr(dNope2, dPrice)
        df.at[index, 'corrD2'] = dN2_dP[0]

        dN_dN2_dP = stats.spearmanr(dN_sub_dN2, dPrice)
        df.at[index, 'corrdN_sub_dN2'] = dN_dN2_dP[0]

        # if(row['timestamp'] > breakFilterDateTime):
        #     break

fig, axs = plt.subplots(3, 1)
fig.suptitle('Spearman R Rank Correlation \n SPY Intra-day deltaNope vs. deltaPrice August 2020')

#axs[3].scatter(df['timestamp'], df['deltaNope'], 2, 'red', label='dNope/dt')
#axs[3].scatter(df['timestamp'], df['deltaNope2'], 2, 'yellow', label='dNope2/d2t')
#axs[3].scatter(df['timestamp'], df['dN-dN2'], 2, 'pink', label='dNope/dt - est_dNope2/d2t')
#axs[3].scatter(df['timestamp'], df['deltaPrice'], 2, 'blue', label='dPrice/dt')
#axs[3].scatter(df['timestamp'], dPriceLag2, 2, 'pink', label='dPrice/dt')

axs[0].plot(df['timestamp'], df['corr'], 'green', label='Cor(dNope(T),dPrice(T))')
axs[0].plot(df['timestamp'], df['corrLag'], 'orange', label='Cor(dNope(T), dPrice(T+5))')
axs[0].plot(df['timestamp'], df['corrLag_2'], 'red', label='Cor(dNope(T), dPrice(T+10))')
axs[0].plot(df['timestamp'], df['corrRaw'], 'cyan', label='Cor(NOPE(T), dPrice(T))')
axs[0].xaxis.set_ticks([i*82 for i in range(0,250)])
axs[0].set_xlim([pd.to_datetime('2020-01-01 9:35'), pd.to_datetime('2020-12-31 4:35')])
axs[0].yaxis.set_ticks([i/4.0 for i in range(-6,6,1)])
axs[0].get_xaxis().set_ticklabels([])
axs[0].title.set_text('First Order Differential Analysis')
axs[0].grid()

axs[0].legend(loc="lower right")
#axs[0].xlabel("Time")
#axs[0].ylabel("Raw")
#axs[0].xticks(np.arange(0, 1605, 75))
#axs[0].yticks(np.arange(-2.5, 2.5, 0.25))


axs[1].plot(df['timestamp'], df['corrD2'], 'black', label='Cor(dNope2(T),dPrice(T))')
axs[1].plot(df['timestamp'], df['corrD2Lag'], 'blue', label='Cor(dNope2(T),dPrice(T+5))')
axs[1].plot(df['timestamp'], df['corrD2Lag_2'], 'green', label='Cor(dNope2(T),dPrice(T+10))')
axs[1].xaxis.set_ticks([i*82 for i in range(0,250)])
axs[1].set_xlim([pd.to_datetime('2020-01-01 9:35'), pd.to_datetime('2020-12-31 4:35')])
axs[1].yaxis.set_ticks([i/4.0 for i in range(-6,6,1)])
axs[1].get_xaxis().set_ticklabels([])
axs[1].title.set_text('Second Order Differential Analysis')
axs[1].grid()
axs[1].legend(loc="lower right")

axs[2].plot(df['timestamp'], df['corrdN_sub_dN2'], 'green', label='Cor((dNope - est_dNope2)(T) , dPrice(T))')
axs[2].plot(df['timestamp'], df['corrdN_sub_dN2_lag'], 'red', label='Cor((dNope - est_dNope2)(T) , dPrice(T+5))')
axs[2].plot(df['timestamp'], df['corrdN_sub_dN2_lag_2'], 'blue', label='Cor((dNope - est_dNope2)(T) , dPrice(T+10))')
axs[2].xaxis.set_ticks([i*82 for i in range(0,250)])
axs[2].set_xlim([pd.to_datetime('2020-01-01 9:35'), pd.to_datetime('2020-12-31 4:35')])
axs[2].yaxis.set_ticks([i/4.0 for i in range(-6,6,1)])
#axs[2].get_xaxis().set_ticklabels([])
axs[2].title.set_text('Forward Projection First/Second Order Differential Analysis')
axs[2].grid()
axs[2].legend(loc="lower right")

plt.show()
