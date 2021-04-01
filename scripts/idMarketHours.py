from datetime import time
import pandas as pd
import pandas_market_calendars as mcal
import numpy as np

'''
all_data = pd.read_csv(DATA_PATH + 'allDataCombined.csv').loc[:,['timestamp', 'C', 'P', 'netDelta', 'stockVolumeAll', 'stockVolumeBus',
                                                                  'numStockTransactions', 'NOPE_busVolume', 'NOPE_allVolume', 'spyPrice']]
df = all_data.copy()
df['timestamp'] = pd.Index(pd.to_datetime(df['timestamp'])).tz_localize('US/Eastern')
df = df.set_index('timestamp')
df.index = pd.to_datetime(df.index)
df['time'] = df.index.strftime("%H:%M:%S")
df['date'] = df.index.strftime("%Y-%m-%d")
'''

def idMarketHours(
    df, dateCol = 'date', timeCol = 'time', dropNonRMH = False
):
  """
  Creates column 'RMH' to mark rows inside regular market hours


  Parameters
  ----------
  df : pandasDataframe to label
  dateCol : str, default 'date'
      Column with days in strftime("%Y-%m-%d") format
  timeCol : str, default 'time'
      Column with days in strftime("%H:%M:%S") format
  dropNonRMH : bool, default False
      Whether to drop non regular market hours rows

  Returns
  -------
  DataFrame
    Added column 'RMH'
  """

  nyse = mcal.get_calendar('NYSE')
  marketSchedule = nyse.schedule(start_date=df['date'].min(), end_date=df['date'].max())
  marketSchedule['openTime'] = pd.DatetimeIndex(marketSchedule['market_open']).tz_convert('US/Eastern').strftime("%H:%M:%S")
  marketSchedule['closeTime'] = pd.DatetimeIndex(marketSchedule['market_close']).tz_convert('US/Eastern').strftime("%H:%M:%S")
  marketSchedule['date'] = marketSchedule.index.strftime("%Y-%m-%d")
  df['RMH'] = 0
  mSchedCols = ['index']
  mSchedCols.extend(list(marketSchedule.columns))

  for day in marketSchedule.itertuples():
    df['RMH'] = np.where((df['date'] == day[mSchedCols.index('date')]) & 
                                (df['time'] >= day[mSchedCols.index('openTime')]) & 
                                (df['time'] <= day[mSchedCols.index('closeTime')])
                                , 1, df['RMH'])
    
  if dropNonRMH:
    df = df.loc[df['RMH'] == 1].copy()

  return df