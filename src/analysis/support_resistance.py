import numpy as np
from scipy.signal import argrelextrema


class SupportResistance:
    def __init__(self, historical_data, order=10):
        """
        Initializes the class with historical data.
        :param historical_data: A Dictionary of DataFrames containing 'Close' prices for each ticker.
        :param order: How many points on each side to use for the local extrema calculation.
        """
        self.data = historical_data
        self.order = order
    
    def calculate_supports(self, ticker):
        """
        Identifies support levels using local minima.
        """
        prices = self.data[ticker]['Close']
        local_minima = argrelextrema(prices.values, np.less_equal, order=self.order)[0]
        supports = prices.iloc[local_minima]
        return supports.dropna()

    def calculate_resistances(self, ticker):
        """
        Identifies resistance levels using local maxima.
        """
        prices = self.data[ticker]['Close']
        local_maxima = argrelextrema(prices.values, np.greater_equal, order=self.order)[0]
        resistances = prices.iloc[local_maxima]
        return resistances.dropna()

    def find_levels(self):
        """
        Calculate and return support and resistance levels for each ticker in the historical data.
        """
        supports = {}
        resistances = {}
        for ticker in self.data:
            supports[ticker] = self.calculate_supports(ticker)
            resistances[ticker] = self.calculate_resistances(ticker)
        return supports, resistances