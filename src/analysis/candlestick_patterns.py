import numpy as np
import pandas as pd


class CandlestickPatterns:
    def __init__(self, historical_data) -> None:
        self.data = historical_data
        
    def identify_doji(self, ticker):
        df = self.data[ticker]
        body = np.abs(df['Close'] - df['Open'])
        price_range = df['High'] - df['Low']
        return body <= (price_range * 0.1)

    def identify_hammer(self, ticker):
        df = self.data[ticker]
        body = np.abs(df['Close'] - df['Open'])
        total_range = df['High'] - df['Low']
        lower_shadow = np.minimum(df['Open'], df['Close']) - df['Low']
        upper_shadow = df['High'] - np.maximum(df['Open'], df['Close'])
        return (body <= total_range * 0.3) & \
            (lower_shadow >= 2 * body) & (upper_shadow <= body * 0.3)

    def identify_inverted_hammer(self, ticker):
        df = self.data[ticker]
        body = np.abs(df['Close'] - df['Open'])
        total_range = df['High'] - df['Low']
        lower_shadow = np.minimum(df['Open'], df['Close']) - df['Low']
        upper_shadow = df['High'] - np.maximum(df['Open'], df['Close'])
        return (body <= total_range * 0.3) & \
            (upper_shadow >= 2 * body) & (lower_shadow <= body * 0.3)

    def identify_shooting_star(self, ticker):
        df = self.data[ticker]
        body = np.abs(df['Close'] - df['Open'])
        total_range = df['High'] - df['Low']
        lower_shadow = np.minimum(df['Open'], df['Close']) - df['Low']
        upper_shadow = df['High'] - np.maximum(df['Open'], df['Close'])
        return (body <= total_range * 0.3) & \
            (upper_shadow >= 2 * body) & (lower_shadow <= body * 0.1)

    def identify_spinning_tops(self, ticker):
        df = self.data[ticker]
        body = np.abs(df['Close'] - df['Open'])
        total_range = df['High'] - df['Low']
        upper_shadow = df['High'] - np.maximum(df['Open'], df['Close'])
        lower_shadow = np.minimum(df['Open'], df['Close']) - df['Low']
        return (body <= total_range * 0.1) & (upper_shadow >= body) & (lower_shadow >= body)

    def identify_engulfing(self, ticker):
        df = self.data[ticker]
        current_body = df['Close'] - df['Open']
        previous_body = df['Close'].shift(1) - df['Open'].shift(1)
        return (np.abs(current_body) > np.abs(previous_body)) & \
            (np.sign(current_body) != np.sign(previous_body))

    def identify_harami(self, ticker):
        df = self.data[ticker]
        current_body = df['Close'] - df['Open']
        previous_body = df['Close'].shift(1) - df['Open'].shift(1)
        return (np.abs(current_body) < np.abs(previous_body)) & \
            (np.sign(current_body) != np.sign(previous_body))

    def identify_piercing_line(self, ticker):
        df = self.data[ticker]
        previous_close = df['Close'].shift(1)
        previous_open = df['Open'].shift(1)
        return (df['Open'] < previous_close) & \
            (
                df['Close'] > previous_open + (previous_close - previous_open) / 2
        )

    def identify_dark_cloud_cover(self, ticker):
        df = self.data[ticker]
        previous_close = df['Close'].shift(1)
        previous_open = df['Open'].shift(1)
        return (df['Open'] > previous_close) & \
            (
                df['Close'] < previous_open + (previous_close - previous_open) / 2
        )

    def identify_morning_star(self, ticker):
        df = self.data[ticker]
        first = df['Close'].shift(2) > df['Open'].shift(2)
        second = np.abs(
            df['Close'].shift(1) - df['Open'].shift(1)
        ) <= (
            df['High'].shift(1) - df['Low'].shift(1)
        ) * 0.1
        third = (df['Open'] < df['Close'].shift(1)) & \
            (df['Close'] > df['Open'].shift(2))
        return first & second & third

    def identify_evening_star(self, ticker):
        df = self.data[ticker]
        first = df['Close'].shift(2) < df['Open'].shift(2)
        second = np.abs(
            df['Close'].shift(1) - df['Open'].shift(1)
            ) <= (
                df['High'].shift(1) - df['Low'].shift(1)
        ) * 0.1
        third = (
            df['Open'] > df['Close'].shift(1)
            ) & (
                df['Close'] < df['Open'].shift(2)
        )
        return first & second & third

    def identify_three_white_soldiers(self, ticker):
        df = self.data[ticker]
        first = df['Close'].shift(2) > df['Open'].shift(2)
        second = df['Close'].shift(1) > df['Open'].shift(1)
        third = df['Close'] > df['Open']
        increasing = first & second & third
        higher_closes = (
            df['Close'].shift(2) < df['Close'].shift(1)
            ) & (
                df['Close'].shift(1) < df['Close']
        )
        return increasing & higher_closes

    def identify_three_black_crows(self, ticker):
        df = self.data[ticker]
        first = df['Close'].shift(2) < df['Open'].shift(2)
        second = df['Close'].shift(1) < df['Open'].shift(1)
        third = df['Close'] < df['Open']
        decreasing = first & second & third
        lower_closes = (
            df['Close'].shift(2) > df['Close'].shift(1)
        ) & (
            df['Close'].shift(1) > df['Close']
        )
        return decreasing & lower_closes
    
    def identify_patterns_for_ticker(self, ticker):
        """
        Identifies all patterns for the historical data of a stock
        """
        df = self.data[ticker]
        patterns = pd.DataFrame(index=df.index)
        patterns['Doji'] = self.identify_doji(ticker)
        patterns['Hammer'] = self.identify_hammer(ticker)
        patterns['Inverted Hammer'] = self.identify_inverted_hammer(ticker)
        patterns['Shooting Star'] = self.identify_shooting_star(ticker)
        patterns['Spinning Tops'] = self.identify_spinning_tops(ticker)
        patterns['Engulfing'] = self.identify_engulfing(ticker)
        patterns['Harami'] = self.identify_harami(ticker)
        patterns['Piercing Line'] = self.identify_piercing_line(ticker)
        patterns['Dark Cloud Cover'] = self.identify_dark_cloud_cover(ticker)
        patterns['Morning Star'] = self.identify_morning_star(ticker)
        patterns['Evening Star'] = self.identify_evening_star(ticker)
        patterns['Three White Soldiers'] = self.identify_three_white_soldiers(ticker)
        patterns['Three Black Crows'] = self.identify_three_black_crows(ticker)
        return patterns
        
    def find_patterns(self):
        
        """Applies pattern identification across all tickers and aggregates results."""
        all_patterns = {}
        for ticker in self.data:
            all_patterns[ticker] = self.identify_patterns_for_ticker(ticker)
        return all_patterns