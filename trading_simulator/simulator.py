import datetime as dt
import numpy as np
import tensorflow as tf
from trading_simulator.broker import Broker
from trading_simulator.trader import Trader

class Simulator:
    def __init__(self, start_date, stop_date, step_time:dt.timedelta, data_center, stocks, trader_count, starting_cash):
        self.start_date = start_date
        self.stop_date = stop_date
        self.step_time = step_time
        self.current_date = start_date
        self.data_center = data_center
        self.stocks = stocks
        self.broker = Broker(start_date, self.data_center, stocks, 0.025, 0.01)
        traders = []
        trader_progbar = tf.keras.utils.Progbar(trader_count)
        for i in range(trader_count):
            trader = Trader(self.broker, starting_cash, stocks)
            traders.append(trader)
            trader_progbar.update(i)
        trader_progbar.update(trader_count)
        self.traders = traders
        self.starting_cash = starting_cash
        print("Simulation initalized!")
        
    def simualte(self):
        week_progress = self.current_date.weekday() / 6.0
        day_progress = (60 * self.current_date.hour + self.current_date.minute) / (24 * 60)

        additional_trader_data = [week_progress, day_progress]

        historical_data = self.data_center.get_history_by_frequency(self.current_date, dt.timedelta(days=15), "15min", self.stocks[0]).values[:, 0]
        historical_data = np.flip(historical_data)[:900] / self.starting_cash

        self.broker.update_timestamp(self.current_date)
        for trader in self.traders: trader.calculate_decisions(additional_trader_data.copy(), historical_data.copy())
        self.add_time(self.step_time)
    
    def add_time(self, timedelta):
        if (self.current_date + timedelta) < self.stop_date:
            self.current_date += timedelta
        else:
            self.current_date = self.stop_date
    
    def get_best_trader(self):
        profits = []
        for i in range(len(self.traders)):
            profits.append(self.traders[i].get_net_worth() - self.starting_cash)
        return self.traders[np.argmax(profits)]

    def get_simulation_progress(self):
        return (self.current_date - self.start_date) / (self.stop_date - self.start_date)
    
    def get_steps_needed(self):
        return np.floor((self.stop_date - self.start_date) / self.step_time)