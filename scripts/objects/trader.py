import numpy as np
from trader_nn import TraderModel

class Trader:

    def __init__(self, broker, cash, stocks):
        self.broker = broker
        self.data_center = broker.data_center
        self.cash = cash
        self.portfolio = {}
        for stock in stocks:
            self.portfolio[stock] = [0, 0]
        self.profit = 0
        self.trades = []
        self.model = TraderModel()
        self.confidence_margin = np.random.rand() * (0.05-0.02) + 0.02

    def buyUSD(self, stock, amountUSD):
        if self.cash < (amountUSD): return False
        trade = self.broker.buyUSD(self, stock, amountUSD)
        if trade:
            self.cash -= amountUSD
            
            portfolio_stock = self.portfolio[stock]
            buyIn = self.calculate_new_buyIn(portfolio_stock[0], portfolio_stock[1], trade[3], trade[2])
            self.portfolio[stock] = [portfolio_stock[0] + trade[3], buyIn]

            self.trades.append((trade[1], trade[2], trade[3]))
            return True

    def sellStock(self, stock, amountStock):
        if self.portfolio[stock][0] < amountStock: return False
        trade = self.broker.sellStock(self, stock, amountStock)
        if trade:
            portfolio_stock = self.portfolio.get(stock, [0, 0])
            self.portfolio[stock] = [portfolio_stock[0] - amountStock, portfolio_stock[1]]

            self.cash += trade[3]
            self.trades.append((trade[1], trade[2], -trade[3]))
            return True

    def calculate_decision(self, stock, additional_trader_data, historical_data):
        trader_data = []
        buy_in_stakes = self.cash * self.confidence_margin
        net_worth = self.get_net_worth()
        if net_worth != 0:
            trader_data.append(self.cash / net_worth)
            trader_data.append(buy_in_stakes / net_worth)
            trader_data.append(self.get_stock_worth(stock) / net_worth)
            trader_data.append(self.get_stock_profit_percentage(stock, True))
            trader_data.append(self.get_stock_profit(stock, True) / net_worth)
        else:
            for _ in range(5): trader_data.append(0)
        trader_data.extend(additional_trader_data)

        results = self.model.calculate(trader_data, historical_data)[0]
        results = results / np.sum(results)
        action = np.random.choice(range(len(results)), p=results)
        
        match action:
            case 0: pass
            case 1: self.buyUSD(stock, buy_in_stakes)
            case 2: self.sellStock(stock, self.portfolio[stock][0])

    def calculate_decisions(self, additional_trader_data, historical_data):
        for stock in self.portfolio:
            self.calculate_decision(stock, additional_trader_data, historical_data)

    def calculate_new_buyIn(self, oldAmount, oldBuyIn, addedAmount, addedBuyIn):
        if (oldAmount + addedAmount) == 0: return 0
        sum = oldAmount * oldBuyIn + addedAmount * addedBuyIn
        return sum / (oldAmount + addedAmount)

    def get_cash(self):
        return self.cash

    def get_net_worth(self, withFees=False):
        net_worth = self.cash
        for stock in self.portfolio.keys():
             stock_worth = self.get_stock_worth(stock, withFees)
             net_worth += stock_worth
        return net_worth

    def get_stock_worth(self, stock, withFees=False):
        if withFees:
            return self.broker.apply_sell_fees(self.portfolio[stock][0], self.broker.get_price(stock))
        else:
            return self.portfolio[stock][0] * self.broker.get_price(stock)

    def get_stock_profit_percentage(self, stock, withFees=False):
        if self.portfolio[stock][0] == 0: return 0
        if withFees:
            return self.broker.apply_sell_fees(self.portfolio[stock][0], self.broker.get_price(stock)) / (self.portfolio[stock][0] * self.portfolio[stock][1])
        else:
            return self.broker.get_price(stock) / self.portfolio[stock][1]
    
    def get_stock_profit(self, stock, withFees=False):
        if self.portfolio[stock][0] == 0: return 0
        if withFees:
            return self.broker.apply_sell_fees(self.portfolio[stock][0], self.broker.get_price(stock)) - self.portfolio[stock][0] * self.portfolio[stock][1]
        else:
            return (self.broker.get_price(stock) - self.portfolio[stock][1]) * self.portfolio[stock][0]
