class StrategyExecutor:
    def __init__(self, market_data, portfolio_analyzor) -> None:
        self.market_data = market_data
        self.portfolio_analyzor = portfolio_analyzor
        self.portfolio_analyzor.apply_strategy()
        self.weights = self.portfolio_analyzor.weights
    
    def normalize_weights(self):
        total_weight = sum(self.weights.values())
        for key in self.weights:
            self.weights[key] /= total_weight
        
    def adjust_weights(self):
        """
        Adjusts weights based on technical indicators, market patterns
        and Markov model predictions
        """
        for ticker, data in self.market_data.iterrows():
            total_adjustment = self.calculate_adjustments(data, ticker)
            self.weights[ticker] *= (1 + total_adjustment)
        self.normalize_weights()
    
    def calculate_adjustments(self, data, ticker):
        """Calculates adjustment factors based on secondary signals for trading."""
        adjustment_factors = {
            'rsi': self.adjust_rsi(data),
            'macd': self.adjust_macd(data),
            'bollinger': self.adjust_bollinger(data),
            'price_vs_sma': self.adjust_price_vs_sma(data),
            'price_vs_ema': self.adjust_price_vs_ema(data),
            'volatility': self.adjust_volatility(data),
            'markov': self.adjust_markov(data),
            'support_resistance': self.adjust_support_resistance(data),
            'pattern_weight': self.calculate_pattern_weights(ticker)
        }
        return sum(adjustment_factors.values())
    
    def adjust_rsi(self, data):
        """A higher relative strength index indicates that
        a stock is overbought
        Args:
            data (pd.Series): Series representing all the columns for the row
        Returns:
            float: weight adjustment based on value of RSI
        """
        if 'rsi' in data:
            return -0.05 if data['rsi'] > 70 else 0.05 if data['rsi'] < 30 else 0
        return 0
    
    def adjust_macd(self, data):
        """Moving average Convergance Divergance. When the macd line
        crosses above the signal line, the stock is bullish
        when it crosses below the signal line, the stock is bearish

        Args:
            data (pd.Series): Series representing all the columns for the row
        """
        if 'macd' in data and 'macd_signal' in data:
            return 0.05 if (data['macd'] > data['macd_signal']) else -0.05
        return 0
    
    def adjust_bollinger(self, data):
        """
        Adjusts weights based on Bollinger Bands indicators.
        Args:
            data (pd.Series): Series representing all the columns for the row
        Returns:
            float: weight adjustment based on Bollinger Bands analysis
        """
        adjustment = 0
        current_price = data['currentPrice']
        if 'upper_bollinger' in data and 'lower_bollinger' in data \
            and 'sma' in data:
            upper_band = data['upper_bollinger']
            lower_band = data['lower_bollinger']
            sma = data['sma'] 
            # Check if current price is above the upper Bollinger Band
            if current_price > upper_band:
                adjustment += 0.05
            # Check if current price is below the lower Bollinger Band
            elif current_price < lower_band:
                adjustment -= 0.05
            # Calculate bandwidth
            bandwidth = (upper_band - lower_band) / sma
            # Increase adjustment if the bandwidth is very high, indicating high volatility
            if bandwidth > 0.10:  # Threshold for high volatility
                adjustment += 0.03
            elif bandwidth < 0.05:  # Threshold for low volatility
                adjustment -= 0.03
        return adjustment

    def adjust_price_vs_sma(self, data):

        if 'sma' in data and 'currentPrice' in data:
            return 0.05 if data['currentPrice'] > data['sma'] else -0.05
        return 0

    def adjust_price_vs_ema(self, data):
 
        if 'ema' in data and 'currentPrice' in data:
            return 0.05 if data['currentPrice'] > data['ema'] else -0.05
        return 0
    
    def adjust_volatility(self, data):
        if 'volatility' in data:
            mean_volatility = self.market_data['volatility'].mean()
            return -0.05 if data['volatility'] > mean_volatility else 0.05
        return 0
    
    def adjust_markov(self, data):
        """A downtrend prediction is 0 or 1 while an uptrend prediction is 2 or 3
        """
        if 'markov_state' in data:
            return -0.10 if data['markov_state'] \
                in [0, 1] else 0.10 if data['markov_state'] in [2, 3] else 0
        return 0
    
    def adjust_support_resistance(self, data):
        """ Adjust weights based on proximity of current price to supports and resistances
        """
        if 'currentPrice' in data:
            current_price = data['currentPrice']
            support_level = data.get('supports', current_price)
            resistance_level = data.get('resistances', current_price)
            # Calculate proximity 
            support_distance_proximity = (current_price - support_level) if current_price != 0 else 0
            resistance_distance_proximity = (resistance_level - current_price) / current_price if current_price != 0 else 0
            # Adjust weights based on these factors
            support_adjustment = 0.1 * (1 - max(0, support_distance_proximity)) if current_price >= support_level else 0
            resistance_adjustment = -0.1 * (1 - max(0, resistance_distance_proximity)) if current_price <= resistance_level else 0
            return support_adjustment + resistance_adjustment
        return 0
    
    def calculate_pattern_weights(self, ticker):
        """"
        Add an adjustment for current candlestick patterns
        """
        positive_patterns = [
            'Hammer', 'Inverted Hammer', 'Morning Star',
            'Three White Soldiers', 'Piercing Line', 'Engulfing', 'Doji'
        ]
        negative_patterns = [
            'Shooting Star', 'Dark Cloud Cover', 'Evening Star',
            'Three Black Crows', 'Harami'
        ]
        pattern_weights = sum(
            [0.03 if self.market_data.at[ticker, pattern] else 0 for pattern in positive_patterns]
        ) - sum(
            [0.03 if self.market_data.at[ticker, pattern] else 0 for pattern in negative_patterns]
        )
        return pattern_weights