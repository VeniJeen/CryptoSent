import pandas as pd
from datetime import datetime

def date_parser_utc_local(x): return datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S')


#data from: https://www.cryptodatadownload.com/data/bitstamp/
def get_btc_actual_hourly():
    path=r"C:\Users\Ben\Desktop\Diplomatiki\CryptoSent\Datasets\CryptoCoin Actuals\Bitstamp_BTCUSD_1h.csv"
    df=pd.read_csv(path)
    df['datetime']=pd.to_datetime(df.unix.progress_apply(date_parser_utc_local))
    df=df.set_index('datetime')
    df['avg_hl']=(df.high+df.low)/2
    df['avg_oc']=(df.open+df.close)/2
    return df

