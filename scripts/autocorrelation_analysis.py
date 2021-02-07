import pandas as pd
import csv
from dateutil import parser
from matplotlib import pyplot as plt
import numpy as np  

DATA_PATH = "../processed_data/"
LAGS = 100

def autocorrelateplot():
    # Must have generated the minmax csv's
    min_df = pd.read_csv(DATA_PATH + 'NOPE_min.csv')
    max_df = pd.read_csv(DATA_PATH + 'NOPE_max.csv')
    
    min_plot = plt.figure(0)
    min_data = min_df['Value']
    plt.title("Autocorrelation Plot Daily Min NOPE")  
    plt.xlabel("Lags")  
    plt.acorr(min_data, maxlags = LAGS)
    plt.grid(True)

    max_plot = plt.figure(1)
    max_data = max_df['Value']
    plt.title("Autocorrelation Plot Daily Max NOPE")  
    plt.xlabel("Lags")
    plt.acorr(max_data, maxlags = LAGS)  
    plt.grid(True)

    plt.show()

def gen_daily_minmax_nope():
    # Init Files
    all_data = pd.read_csv(DATA_PATH + 'allDataCombined.csv')
    price_data = pd.read_csv(DATA_PATH + 'priceData.csv')

    # Load into dataframe
    df = pd.merge(all_data, price_data, on="timestamp")
    df['date'] = df['timestamp'].apply(lambda x: parser.parse(x).date())
    df['time'] = df['timestamp'].apply(lambda x: parser.parse(x).strftime("%H:%M:%S"))

    days = df['date'].unique()

    with open("../processed_data/NOPE_daily_min.csv", 'w') as NOPE_MIN_CSV, open("../processed_data/NOPE_daily_max.csv", 'w') as NOPE_MAX_CSV:
        min_writer = csv.writer(NOPE_MIN_CSV)
        max_writer = csv.writer(NOPE_MAX_CSV)

        min_writer.writerow(['Date', 'Value'])
        max_writer.writerow(['Date', 'Value'])

        for d in days:
            rows = df.loc[df['date'] == d]

            min_nope = rows['NOPE_allVolume'].min()
            min_writer.writerow([d, min_nope])

            max_nope = rows['NOPE_allVolume'].max()
            max_writer.writerow([d, max_nope])

if __name__ == '__main__':
    autocorrelateplot()