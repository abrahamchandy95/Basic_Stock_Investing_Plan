import numpy as np

from analysis import TechnicalAnalysis, CandlestickPatterns, SupportResistance, MarkovModel


class AnalysisImplementor:
    def __init__(self, historical_data, market_data) -> None:
        self.historical_data = historical_data
        self.market_data = market_data
        self.technical_analysis = TechnicalAnalysis(self.historical_data)
        self.candlestick_patterns = CandlestickPatterns(self.historical_data)
        self.support_resistance = SupportResistance(self.historical_data)
        self.markov_models = {
            ticker: MarkovModel(data) for ticker, data in self.historical_data.items()
        }
    
    def implement_all_analysis(self):
        self.implement_technical_analysis()
        self.implement_pattern_analysis()
        self.integrate_markov_predictions()
        
    def implement_technical_analysis(self):
        """ 
        Applies most recent technical analysis to market data
        """
        for ticker in self.technical_analysis.historical_data.keys():
            self.market_data.loc[ticker, 'sma'] = \
                self.technical_analysis.calculate_sma(ticker).iloc[-1]
            self.market_data.loc[ticker, 'ema'] = \
                self.technical_analysis.calculate_ema(ticker).iloc[-1]
            self.market_data.loc[ticker, 'volatility'] = \
                self.technical_analysis.calculate_moving_volatility(ticker).iloc[-1]
            self.market_data.loc[ticker, 'rsi'] = \
                self.technical_analysis.calculate_rsi(ticker).iloc[-1]
            macd, macd_signal = self.technical_analysis.calculate_macd(ticker)
            self.market_data.loc[ticker, 'macd'] = macd.iloc[-1]
            self.market_data.loc[ticker, 'macd_signal'] = macd_signal.iloc[-1]
            upper_band, lower_band = \
                self.technical_analysis.calculate_bollinger_bands(ticker)
            self.market_data.loc[ticker, 'upper_bollinger'] = upper_band.iloc[-1]
            self.market_data.loc[ticker, 'lower_bollinger'] = lower_band.iloc[-1]
            obv, obv_prev = self.technical_analysis.calculate_obv(ticker)
            self.market_data.loc[ticker, 'obv'] = obv.iloc[-1]
            self.market_data.loc[ticker, 'obv_previous'] = obv_prev.iloc[-1]
            self.market_data.loc[ticker, 'trend'] = \
                self.technical_analysis.calculate_recent_trend(ticker).iloc[-1]
    
    def implement_pattern_analysis(self):
        """Adds candlestick patterns and support/resistance levels to the market data
        """
        self.market_data['supports'] = None
        self.market_data['resistances'] = None
        
        supports, resistances = self.support_resistance.find_levels()
        for ticker in supports:
            self.market_data.loc[ticker, 'supports'] = \
                supports[ticker].iloc[-1] if not supports[ticker].empty else None
            self.market_data.loc[ticker, 'resistances'] = \
                resistances[ticker].iloc[-1] if not resistances[ticker].empty else None

        all_patterns = self.candlestick_patterns.find_patterns()
        for ticker, patterns in all_patterns.items():
            # Get the last date's data for each ticker's patterns
            last_patterns = patterns.iloc[-1]
            # Ensure the ticker is already an index in market_data or has an equivalent key
            if ticker in self.market_data.index:
                for pattern_name in patterns.columns:
                    # Safely add pattern columns to market_data if not already present
                    if pattern_name not in self.market_data.columns:
                        self.market_data[pattern_name] = np.nan  # Initialize if not existing
                    
                    # Update the specific pattern entry for the ticker in market_data
                    self.market_data.loc[ticker, pattern_name] = float(last_patterns[pattern_name]
)                
    def integrate_markov_predictions(self):
        """
        Integrate Markov model predictions into market data
        """
        self.market_data['markov_state'] = None
        for ticker, model in self.markov_models.items():
            if ticker in self.market_data.index:
                self.market_data.at[ticker, 'markov_state'] = model.predict_next_state()