import numpy as np
import pandas as pd


class TechnicalAnalysis:
    def __init__(self, historical_data, max_years=3):
        self.historical_data = historical_data
        self.limit_data_to_recent_years(max_years)
        self.windows = self.calculate_volatility_based_window()
        
    def limit_data_to_recent_years(self, years):
        """
        Limits the data to the most recent years
        """
        current_date = pd.to_datetime('today').tz_localize('America/New_York')
        cutoff_date = current_date - pd.DateOffset(years=years)
        limited_data = {}  # Dictionary to store limited data for each ticker
        for ticker, data in self.historical_data.items():
            limited_data[ticker] = data[data.index >= cutoff_date]
        self.historical_data = limited_data 
        
    def calculate_volatility_based_window(self):
        """
        Calculates a dynamic window size based on volatility for each stock in the portfolio
        """
        window_sizes = {}
        for ticker, data in self.historical_data.items():
            recent_volatility = data['Close'].rolling(window=30).std().dropna().iloc[-1]
            overall_volatility = data['Close'].std()
            window_sizes[ticker] = max(10, int(50/2)) if recent_volatility > overall_volatility else 50
        return window_sizes
        
    def calculate_sma(self, ticker, window=None):
        """Calculates the Simple Moving Average percentage change 
        (Primary Trading Signal)
        """
        if window is None:
            window = self.windows[ticker]
        sma_values = self.historical_data[ticker]['Close'].rolling(window=window).mean()
        sma_pct_change = sma_values.pct_change()
        return sma_pct_change
    
    def calculate_ema(self, ticker, window=None):
        """
        Calculates exponetial moving average (Primary Trading Signal)
        """
        if window is None:
            window = self.windows[ticker]
        ema_values = self.historical_data[ticker]['Close'].ewm(span=window, adjust=False).mean()
        return ema_values
    
    def calculate_moving_volatility(self, ticker, window=None):
        """Calculate the moving standard deviation over a window
        """
        if window is None:
            window = self.windows[ticker]
        return self.historical_data[ticker]['Close'].rolling(window=window).std()
    
    def calculate_rsi(self, ticker, window=14):
        """Calculates Relative Strenght Index, calculated over 14 days.
        Gains and Losses are averaged out over 14 days.
        RS = Average Gain/ Average Loss
        RSI = 100 - (100/(1+RS))
        """
        delta = self.historical_data[ticker]['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def calculate_macd(self, ticker, fast=12, slow=26, signal=9):
        """
        Calculate Moving Average Convergence Divergence (MACD). 
        Based on the difference between short term (fast) and 
        long term (slow) exponential moving averages
        macd_signal is the smoothening factor: \the difference can signal trends
        """
        ema_fast = self.calculate_ema(ticker, window=fast)
        ema_slow = self.calculate_ema(ticker, window=slow)
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal, adjust=False).mean()
        # signal line smoothens the MACD line itself
        return macd, macd_signal
    
    def calculate_bollinger_bands(self, ticker, window=20):
        """Calculate Bollinger Bands
        """
        sma = self.calculate_sma(ticker, window=window)
        std = self.historical_data[ticker]['Close'].rolling(window=window).std()
        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)
        return upper_band, lower_band
    
    def calculate_percent_b(self, ticker, window=20):
        """
        a normalized representation of where the last closing price falls relative to the Bollinger Bands.
        """
        upper_band, lower_band = self.calculate_bollinger_bands(ticker, window)
        current_price = self.historical_data[ticker]['Close'].iloc[-1]
        percent_b = (current_price - lower_band) / (upper_band - lower_band)
        return percent_b

    def calculate_obv(self, ticker):
        """
        Calculate On-Balance Volume (OBV)
        """
        close = self.historical_data[ticker]['Close']
        volume = self.historical_data[ticker]['Volume']
        obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
        obv_prev = obv.shift(1)
        return obv, obv_prev
    
    def calculate_recent_trend(self, ticker):
        # Based on short and long term moving averages
        short_term_window = 20
        long_term_window = 90
        # Calculate short and long term moving averages
        short_term_ma = self.historical_data[ticker]['Close'].rolling(
            window=short_term_window
        ).mean()
        # Exponential moving average for long term
        long_term_ma = self.historical_data[ticker]['Close'].ewm(
            span=long_term_window, adjust=False
        ).mean()
        # trend signal shows the relationship between short and long term mas
        trend_signal = (short_term_ma > long_term_ma).astype(int) - \
            (short_term_ma < long_term_ma).astype(int)
        trend_description = trend_signal.map(
            {1: 'up', -1: 'down', 0: 'flat'}
        ).fillna('flat')
        return trend_description