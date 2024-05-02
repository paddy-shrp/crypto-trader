from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
import datetime as dt
import pandas as pd

class DataCenter:
    
    def __init__(self, stocks, start=None, end=None, file_path=None):
        
        self.dfs = {}

        if file_path:
            try:
                crypto_df = pd.read_csv(file_path, index_col=["symbol", "timestamp"])
                crypto_df.index = crypto_df.index.set_levels(pd.to_datetime(crypto_df.index.levels[1]), level='timestamp')
                for stock in stocks:
                    stock_df = crypto_df.loc[stock]
                   
                    self.dfs[stock] = stock_df
                print("Datacenter initalized!")
                return
            except:
                client = CryptoHistoricalDataClient()
                request_params = CryptoBarsRequest(symbol_or_symbols=stocks,
                                   timeframe=TimeFrame.Minute, 
                                   start = start,
                                   end = end)
                bars = client.get_crypto_bars(request_params)
                crypto_df = pd.DataFrame(bars.df)
                crypto_df.index = crypto_df.index.set_levels(pd.to_datetime(crypto_df.index.levels[1]), level='timestamp')
                crypto_df.pop("vwap")
                crypto_df.to_csv(file_path)
                print(file_path, "File does not exist.")
        
        for stock in stocks:
            self.dfs[stock] = crypto_df.loc[stock]
        print("Datacenter initalized!")

    def get_price(self, stock, query_time):
        formatted_time = pd.to_datetime(query_time).tz_localize("UTC")
        closest = self.dfs[stock].index.get_indexer([formatted_time], method="nearest")
        return self.dfs[stock].iloc[closest].values[0][0]
    
    def get_history_by_frequency(self, current_date, history_time, freq, stock):
        history_end_time = pd.to_datetime(current_date - history_time).tz_localize("UTC")
        current_date = pd.to_datetime(current_date).tz_localize("UTC") 
        return self.dfs[stock][history_end_time:current_date].asfreq(freq).ffill()