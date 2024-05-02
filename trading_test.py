from trading_simulator.data_center import DataCenter
from trading_simulator.broker import Broker
from trading_simulator.trader import Trader
import datetime as dt

stocks = ["ETH/USD"]

data_center = DataCenter(stocks, file_name="eth_usd_2022")
trader_count = 100
starting_cash = 10000

start_date = dt.datetime(2023, 12, 1)

broker = Broker(start_date, data_center, stocks, 0, 0.05, 1)
trader = Trader(broker, 10000, stocks)

trader.buyUSD(stocks[0], 500)
print(trader.portfolio)

broker.update_timestamp(start_date + dt.timedelta(days=1))
print(broker.get_price(stocks[0]))