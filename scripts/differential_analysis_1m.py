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

df = pd.read_csv(DATA_PATH + 'intraNope_1m_2020-03-25.csv')
df['Timestamp'] = df['Timestamp'].apply(lambda x: pd.to_datetime(x))

# we need to setup our shifted data columns
df['spyNOPE_Bus'] = df['spyNOPE_Bus'].apply(lambda x: x*100.0)
df['spyNOPE_BusPrev'] = df['spyNOPE_Bus'].shift()

df['deltaNope'] = df.apply(lambda x: x['spyNOPE_Bus'] - x['spyNOPE_BusPrev'], axis=1)
df['deltaNope'].fillna(0.0 ,inplace = True)
df['deltaNopePrev'] = df['deltaNope'].shift()

df['deltaNope2'] = df.apply(lambda x: x['deltaNope'] - x['deltaNopePrev'], axis=1)
df['deltaNope2'].fillna(0.0 ,inplace = True)
df['deltaNope2Prev'] = df['deltaNope2'].shift()

df['Close_prev'] = df['Close'].shift()

df['deltaPrice'] = df.apply(lambda x: x['Close'] - x['Close_prev'], axis=1)
df['deltaPrice'].fillna(0.0 ,inplace = True)

df['deltaPrice+5'] = df['deltaPrice'].shift(-1)
df['deltaPrice+5'].fillna(0.0 ,inplace = True)

df['deltaPrice+10'] = df['deltaPrice'].shift(-2)
df['deltaPrice+10'].fillna(0.0 ,inplace = True)

# use a split interpolate on the second order to function as the modeled second order
# this is a reduction of cubic spline interpolation used in forward forecasting signal processing
df['dN-dN2'] = df.apply(lambda x: x['deltaNope'] - (0.5*x['deltaNope2Prev'] - 0.5*x['deltaNope2']), axis=1)
df['dN-dN2'].fillna(0.0 ,inplace = True)
print(df)

for index, row in df.iterrows():
    #print(index, row)
    if (index == 0):
        filterDatetime = row['Timestamp']
        endFilterDatetime = row['Timestamp'].replace(hour=16)
        continue
    else:

        print("Processing data: ", row['Timestamp'])

        # process data up to the latest data entry
        dNope = df[(df['Timestamp'] <= row['Timestamp'])]['deltaNope'].to_numpy()
        dNope2 = df[(df['Timestamp'] <= row['Timestamp'])]['deltaNope2'].to_numpy()
        dN_sub_dN2 = df[(df['Timestamp'] <= row['Timestamp'])]['dN-dN2'].to_numpy()
        dPrice = df[(df['Timestamp'] <= row['Timestamp'])]['deltaPrice'].to_numpy()
        dNopeRaw = df[(df['Timestamp'] <= row['Timestamp'])]['spyNOPE_Bus'].to_numpy()
        dPrice_p5 = df[(df['Timestamp'] <= row['Timestamp'])]['deltaPrice+5'].to_numpy()
        dPrice_p10 = df[(df['Timestamp'] <= row['Timestamp'])]['deltaPrice+10'].to_numpy()

        df.at[index, 'corrLag'] = stats.spearmanr(dNope, dPrice_p5)[0]
        df.at[index, 'corrD2Lag'] = stats.spearmanr(dNope2, dPrice_p5)[0]
        dN_dN2_dP_t_plus_5 = stats.spearmanr(dN_sub_dN2, dPrice_p5)
        df.at[index, 'corrdN_sub_dN2_lag'] = dN_dN2_dP_t_plus_5[0]

        df.at[index, 'corrLag_2'] = stats.spearmanr(dNope, dPrice_p10)[0]
        df.at[index, 'corrD2Lag_2'] = stats.spearmanr(dNope2, dPrice_p10)[0]
        df.at[index, 'corrdN_sub_dN2_lag_2'] = stats.spearmanr(dN_sub_dN2, dPrice_p10)[0]

        # compute our various correlations
        dN_dP = stats.spearmanr(dNope, dPrice)
        df.at[index, 'corr'] = dN_dP[0]
        df.at[index, 'corrRaw'] = stats.spearmanr(dNope, dNopeRaw)[0]

        dN2_dP = stats.spearmanr(dNope2, dPrice)
        df.at[index, 'corrD2'] = dN2_dP[0]

        dN_dN2_dP = stats.spearmanr(dN_sub_dN2, dPrice)
        df.at[index, 'corrdN_sub_dN2'] = dN_dN2_dP[0]

        # debug break to reduce processing time
        # if(row['Timestamp'] > breakFilterDateTime):
        #     break

fig, axs = plt.subplots(3, 1, constrained_layout=True)

fig.suptitle('Spearman R Rank Correlation \n SPY Intra-day 1m deltaNope vs. deltaPrice 03-25-2020')

#axs[3].scatter(df['Timestamp'], df['deltaNope'], 2, 'red', label='dNope/dt')
#axs[3].scatter(df['Timestamp'], df['deltaNope2'], 2, 'yellow', label='dNope2/d2t')
#axs[3].scatter(df['Timestamp'], df['dN-dN2'], 2, 'pink', label='dNope/dt - est_dNope2/d2t')
#axs[3].scatter(df['Timestamp'], df['deltaPrice'], 2, 'blue', label='dPrice/dt')
#axs[3].scatter(df['Timestamp'], dPriceLag2, 2, 'pink', label='dPrice/dt')

# build up a date range to define the x ticks
datelist = pd.date_range(start = df.at[1, 'Timestamp'], end = df.at[len(df.index)-1, 'Timestamp'], periods=26).tolist()
timelist = [x.strftime('%H:%M') for x in datelist]

axs[0].plot(df['Timestamp'], df['corr'], 'green', label='Cor(dNope(T),dPrice(T))')
axs[0].plot(df['Timestamp'], df['corrLag'], 'orange', label='Cor(dNope(T), dPrice(T+1))')
axs[0].plot(df['Timestamp'], df['corrLag_2'], 'red', label='Cor(dNope(T), dPrice(T+2))')
axs[0].plot(df['Timestamp'], df['corrRaw'], 'cyan', label='Cor(NOPE(T), dPrice(T))')
axs[0].xaxis.set_ticks(datelist)
axs[0].set_xlim([datelist[0].replace(hour=9, minute=30), datelist[len(datelist)-1].replace(hour=16, minute=35)])
axs[0].yaxis.set_ticks([i/4.0 for i in range(-4,4,1)])
axs[0].get_xaxis().set_ticklabels(timelist)
axs[0].title.set_text('First Order Differential Analysis')
axs[0].grid()

axs[0].legend(loc="lower right")
#axs[0].xlabel("Time")
#axs[0].ylabel("Raw")
#axs[0].xticks(np.arange(0, 1605, 75))
#axs[0].yticks(np.arange(-2.5, 2.5, 0.25))


axs[1].plot(df['Timestamp'], df['corrD2'], 'black', label='Cor(dNope2(T),dPrice(T))')
axs[1].plot(df['Timestamp'], df['corrD2Lag'], 'blue', label='Cor(dNope2(T),dPrice(T+1))')
axs[1].plot(df['Timestamp'], df['corrD2Lag_2'], 'green', label='Cor(dNope2(T),dPrice(T+2))')
axs[1].xaxis.set_ticks(datelist)
axs[1].set_xlim([datelist[0].replace(hour=9, minute=30), datelist[len(datelist)-1].replace(hour=16, minute=35)])
axs[1].yaxis.set_ticks([i/4.0 for i in range(-4,4,1)])
axs[1].get_xaxis().set_ticklabels(timelist)
axs[1].title.set_text('Second Order Differential Analysis')
axs[1].grid()
axs[1].legend(loc="lower right")

axs[2].plot(df['Timestamp'], df['corrdN_sub_dN2'], 'green', label='Cor((dNope - est_dNope2)(T) , dPrice(T))')
axs[2].plot(df['Timestamp'], df['corrdN_sub_dN2_lag'], 'red', label='Cor((dNope - est_dNope2)(T) , dPrice(T+1))')
axs[2].plot(df['Timestamp'], df['corrdN_sub_dN2_lag_2'], 'blue', label='Cor((dNope - est_dNope2)(T) , dPrice(T+2))')
axs[2].xaxis.set_ticks(datelist)
axs[2].set_xlim([datelist[0].replace(hour=9, minute=30), datelist[len(datelist)-1].replace(hour=16, minute=35)])
axs[2].yaxis.set_ticks([i/4.0 for i in range(-4,4,1)])
axs[2].get_xaxis().set_ticklabels(timelist)
axs[2].title.set_text('Forward Projection First/Second Order Differential Analysis')
axs[2].grid()
axs[2].legend(loc="lower right")

plt.show()
