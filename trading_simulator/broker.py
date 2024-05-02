
class Broker:
    
    def __init__(self, timestamp, data_center, stocks, buyFee=0.0, sellFee=0.0, flatFee=0.0):
        self.timestamp = timestamp
        self.data_center = data_center
        self.stocks = stocks
        self.prices = {}
        self.buyFee = buyFee
        self.sellFee = sellFee
        self.flatFee = flatFee
        self.trades = []

        self.update_prices()
    
    def update_timestamp(self, timestamp):
        self.timestamp = timestamp
        self.update_prices()

    def update_prices(self):
        for stock in self.stocks:
            self.prices[stock] = self.data_center.get_price(stock, self.timestamp)

    def get_price(self, stock):
        return self.prices[stock]

    def buyUSD(self, trader, stock, amountUSD):
        stock_price = self.get_price(stock)
        return self.trade(trader, stock, stock_price, self.apply_buy_fees(amountUSD, stock_price))

    def sellStock(self, trader, stock, amountCoin):
        stock_price = self.get_price(stock)
        return self.trade(trader, stock, stock_price, self.apply_sell_fees(amountCoin, stock_price))

    def apply_buy_fees(self, inputUSD, stock_price):
        if inputUSD == 0: return 0
        return (1 - self.buyFee) * (inputUSD - self.flatFee) / stock_price

    def apply_sell_fees(self, inputAmount, stock_price):
        if inputAmount == 0: return 0
        return (1- self.sellFee) * inputAmount * stock_price - self.flatFee

    def trade(self, trader, stock, stock_price, amount):
        trade = (trader, stock, stock_price, amount)
        self.trades.append(trade)
        # return None if trade was not successful, here 100%
        return trade