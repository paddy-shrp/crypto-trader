import datetime as dt
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from data_center import DataCenter
from objects.broker import Broker
from objects.trader import Trader
import time

# survival of the fittest

class Simulator:
    def __init__(self, start_date, stop_date, step_time:dt.timedelta, data_center, stocks, trader_count, starting_cash):
        self.start_date = start_date
        self.stop_date = stop_date
        self.step_time = step_time
        self.current_date = start_date
        self.data_center = data_center
        self.broker = Broker(start_date, self.data_center, stocks, 0.025, 0.01)
        traders = []
        trader_probbar = tf.keras.utils.Progbar(trader_count)
        for i in range(trader_count):
            trader = Trader(self.broker, starting_cash, stocks)
            traders.append(trader)
            trader_probbar.update(i)
        trader_probbar.update(trader_count)
        self.traders = traders
        self.starting_cash = starting_cash
        print("Simulation initalized!")
        
    def simualte(self):
        week_progress = self.current_date.weekday() / 6.0
        day_progress = (60 * self.current_date.hour + self.current_date.minute) / (24 * 60)

        additional_trader_data = [week_progress, day_progress]

        historical_data = data_center.get_history_by_frequency(self.current_date, dt.timedelta(days=15), "15min", stocks[0]).values[:, 0]
        historical_data = np.flip(historical_data)[:900] / self.starting_cash

        self.broker.update_timestamp(self.current_date)
        for trader in self.traders: trader.calculate_decisions(additional_trader_data.copy(), historical_data.copy())
        self.add_time(step_time)
    
    def add_time(self, timedelta):
        if (self.current_date + timedelta) < self.stop_date:
            self.current_date += timedelta
        else:
            self.current_date = self.stop_date
    
    def get_best_trader(self):
        profits = []
        for i in range(len(self.traders)):
            profits.append(self.traders[i].get_net_worth() - starting_cash)
        return self.traders[np.argmax(profits)]

    def get_simulation_progress(self):
        return (self.current_date - self.start_date) / (self.stop_date - self.start_date)
    
    def get_steps_needed(self):
        return np.floor((self.stop_date - self.start_date) / self.step_time)


stocks = ["ETH/USD"]

data_center = DataCenter(stocks, file_path="./data/data_center.csv")
trader_count = 100
starting_cash = 1000

start_date = dt.datetime(2023, 12, 1)
end_date = dt.datetime(2023, 12, 2)
step_time = dt.timedelta(minutes=15)

sim = Simulator(start_date, end_date, step_time, data_center, stocks, trader_count, starting_cash)

progbar = tf.keras.utils.Progbar(sim.get_steps_needed())

times = []
times.append(time.time())

while sim.current_date < sim.stop_date:
    progbar.update(int(np.floor(sim.get_simulation_progress() * sim.get_steps_needed())))
    sim.simualte()
    times.append(time.time())
progbar.update(int(sim.get_steps_needed()))

time_intervals = []
for i in range(2, len(times)):
    time_intervals.append((times[i] - times[i-1]) / trader_count)

trader_profits = []
trader_trade_counts = []
for trader in sim.traders:
    trader_profits.append(trader.get_net_worth() - starting_cash)
    trader_trade_counts.append(len(trader.trades))
x = np.arange(trader_count)
plt.scatter(x, trader_profits)
plt.scatter(x, trader_trade_counts)


# best_trader = sim.get_best_trader()
# x = np.arange(len(time_intervals))
# mean = round(np.mean(time_intervals), 4)
# title = str(round(best_trader.get_net_worth() - starting_cash, 2)) + " - " + str(mean)
# plt.title(title)
# plt.scatter(x, time_intervals, s=2)
# plt.axhline(mean)


plt.show()