# Imports #1
import math
from scipy.stats import norm

# Global assignments #1
S = 100
K = 110

def price_call_option():
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    call_price = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    return call_price

# Global assignments #2
T = 1
r = 0.05
sigma = 0.20

def price_put_option():
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    put_price = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    return put_price

# Import #2
try:
    import numpy as np
    import pandas as pd
except ImportError:
    pass

# Global assignments #2
call_price = price_call_option()
put_price = price_put_option()

# Simple statements
print(f'The price of the call option is: {call_price:.2f}')
print(f'The price of the put option is: {put_price:.2f}')