import math
from scipy.stats import norm

# Import #2
try:
    import numpy as np
    import pandas as pd
except ImportError:
    pass

class Foo:

    def __init__(self):
        # Imports #1

        # Global assignments #1
        self.S = 100
        self.K = 110

        # Global assignments #2
        self.T = 1
        self.r = 0.05
        self.sigma = 0.20

        # Global assignments #2
        self.call_price = self.price_call_option()
        self.put_price = self.price_put_option()

        # Simple statements
        print(f'The price of the call option is: {self.call_price:.2f}')
        print(f'The price of the put option is: {self.put_price:.2f}')


    def price_call_option(self):
        d1 = (math.log(self.S / self.K) + (self.r + 0.5 * self.sigma ** 2) * self.T) / (self.sigma * math.sqrt(self.T))
        d2 = d1 - self.sigma * math.sqrt(self.T)
        call_price = self.S * norm.cdf(d1) - self.K * math.exp(-self.r * self.T) * norm.cdf(d2)
        return call_price

    def price_put_option(self):
        d1 = (math.log(self.S / self.K) + (self.r + 0.5 * self.sigma ** 2) * self.T) / (self.sigma * math.sqrt(self.T))
        d2 = d1 - self.sigma * math.sqrt(self.T)
        put_price = self.K * math.exp(-self.r * self.T) * norm.cdf(-d2) - self.S * norm.cdf(-d1)
        return put_price
