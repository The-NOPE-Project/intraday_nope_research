import numpy as np
import pandas as pd
from scipy import stats
from dateutil import parser
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import matplotlib.dates as mdates
import statistics

DATA_PATH = '../processed_data/'

price_data = pd.read_csv(DATA_PATH + 'priceData.csv')
nope_data = pd.read_csv(DATA_PATH + 'parsedNetDelta2020-08.csv')
df = pd.merge(nope_data, price_data, on="timestamp")

deltaNope = 0.0
deltaNope2 = 0.0
deltaPrice = 0.0
lastNope = 0.0
lastDNope = 0.0
lastDNope2 = 0.0
lastPrice = 0.0
dPriceLag = []

for index, row in df.iterrows():

    if (index == 0):
        df['deltaNope'] = 0.0
        df['deltaPrice'] = 0.0
        df['deltaNope2'] = 0.0
        df['dN-dN2'] = 0.0
        lastNope = row['NOPE_allVolume']
        lastPrice = row['active_underlying_price']
        lastDNope = 0.0
        lastDNope2 = 0.0
        continue
    else:
        # ignore the first entry in each day, as we just want to compare the data within a single day, and not the end
        # of the previous day to the open of the current
        if('9:35' in row['timestamp']):
            #print('Skipping entry:' , row['timestamp'])
            lastNope = row['NOPE_allVolume']
            lastPrice = row['active_underlying_price']
            lastDNope = 0.0
            lastDNope2 = 0.0
            continue

        deltaNope = lastNope - row['NOPE_allVolume']
        deltaPrice = lastPrice - row['active_underlying_price']
        deltaNope2 = lastDNope - deltaNope

        #print(deltaNope, deltaPrice)
        df.at[index, 'deltaNope'] = deltaNope
        df.at[index, 'deltaPrice'] = deltaPrice
        df.at[index, 'deltaNope2'] = deltaNope2

        # use a split interpolate on the second order to function as the modeled second order
        # this is a reduction of cubic spline interpolation used in forward forecasting signal processing
        df.at[index, 'dN-dN2'] = deltaNope - (0.5*lastDNope2 - 0.5*deltaNope2)

        dNope = df['deltaNope'].to_numpy()
        dNope2 = df['deltaNope2'].to_numpy()
        dN_sub_dN2 = df['dN-dN2'].to_numpy()
        dPrice = df['deltaPrice'].to_numpy()
        dNopeRaw = df['NOPE_allVolume'].to_numpy()

        # shift the data back by 1
        dPriceLag = np.delete(dPrice, 0, 0)
        dPriceLag = np.insert(dPriceLag, dPriceLag.size - 1, 0)

        # shift the data back by 2
        dPriceLag2 = np.delete(dPrice, 0, 0)
        dPriceLag2 = np.delete(dPriceLag2, 0, 0)
        dPriceLag2 = np.insert(dPriceLag2, dPriceLag2.size - 1, 0)
        dPriceLag2 = np.insert(dPriceLag2, dPriceLag2.size - 1, 0)

        # compute our various correlations
        dN_dP = stats.spearmanr(dNope, dPrice)
        df.at[index, 'corr'] = dN_dP[0]
        print("dNope p Value: ", str(dN_dP[1]))
        df.at[index, 'corrLag'] = stats.spearmanr(dNope, dPriceLag)[0]
        df.at[index, 'corrLag_2'] = stats.spearmanr(dNope, dPriceLag2)[0]
        df.at[index, 'corrRaw'] = stats.spearmanr(dNope, dNopeRaw)[0]

        dN2_dP = stats.spearmanr(dNope2, dPrice)
        df.at[index, 'corrD2'] = dN2_dP[0]
        print("dNope2 p Value: ", str(dN2_dP[1]))
        df.at[index, 'corrD2Lag'] = stats.spearmanr(dNope2, dPriceLag)[0]
        df.at[index, 'corrD2Lag_2'] = stats.spearmanr(dNope2, dPriceLag2)[0]

        dN_dN2_dP = stats.spearmanr(dN_sub_dN2, dPrice)
        df.at[index, 'corrdN_sub_dN2'] = dN_dN2_dP[0]
        print("dNope - dNope2 p Value: ", str(dN_dN2_dP[1]))


        dN_dN2_dP_t_plus_5 = stats.spearmanr(dN_sub_dN2, dPriceLag)
        df.at[index, 'corrdN_sub_dN2_lag'] = dN_dN2_dP_t_plus_5[0]
        print("dNope - dNope2 T+5 p Value: ", str(dN_dN2_dP_t_plus_5[1]))
        df.at[index, 'corrdN_sub_dN2_lag_2'] = stats.spearmanr(dN_sub_dN2, dPriceLag2)[0]


    lastNope = row['NOPE_allVolume']
    lastPrice = row['active_underlying_price']
    lastDNope = deltaNope
    lastDNope2 = deltaNope2

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
axs[0].xaxis.set_ticks([i*100 for i in range(0,20)])
axs[0].yaxis.set_ticks([i/4.0 for i in range(-4,4,1)])
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
axs[1].xaxis.set_ticks([i*100 for i in range(0,20)])
axs[1].yaxis.set_ticks([i/4.0 for i in range(-4,4,1)])
axs[1].get_xaxis().set_ticklabels([])
axs[1].title.set_text('Second Order Differential Analysis')
axs[1].grid()
axs[1].legend(loc="lower right")

axs[2].plot(df['timestamp'], df['corrdN_sub_dN2'], 'green', label='Cor((dNope - est_dNope2)(T) , dPrice(T))')
axs[2].plot(df['timestamp'], df['corrdN_sub_dN2_lag'], 'red', label='Cor((dNope - est_dNope2)(T) , dPrice(T+5))')
axs[2].plot(df['timestamp'], df['corrdN_sub_dN2_lag_2'], 'blue', label='Cor((dNope - est_dNope2)(T) , dPrice(T+10))')
axs[2].xaxis.set_ticks([i*100 for i in range(0,20)])
axs[2].yaxis.set_ticks([i/4.0 for i in range(-4,4,1)])
axs[2].get_xaxis().set_ticklabels([])
axs[2].title.set_text('Forward Projection First/Second Order Differential Analysis')
axs[2].grid()
axs[2].legend(loc="lower right")

plt.show()
