import matplotlib.pyplot as plt
import pandas as pd

from src.analysis import CandlestickPatterns
from src.analysis import SupportResistance


class StockDataVisualizer:
    def __init__(self, historical_data, years=3) -> None:
        self.historical_data = historical_data
        self. limit_data_to_recent_years(years)
        self.candlestick_patterns = CandlestickPatterns(self.historical_data)
        self.support_resistance = SupportResistance(self.historical_data)
    
    def limit_data_to_recent_years(self, years):
            """
            Limits the data to the most recent years
            """
            current_date = pd.Timestamp.now(tz='America/New_York')
            cutoff_date = current_date - pd.DateOffset(years=years)
            self.historical_data = {
                ticker: data[data.index >= cutoff_date] \
                    for ticker, data in self.historical_data.items()
            }
    
    def plot_stock_data(self):
        for ticker, data in self.historical_data.items():
            fig, ax = plt.subplots(figsize=(14, 7))
            # Plot stock closing price
            ax.plot(data.index, data['Close'], label='Close Price', color='blue')

            # Highlight candlestick patterns
            patterns = self.candlestick_patterns.find_patterns().get(ticker, pd.DataFrame())
            for pattern_name, presence_data in patterns.items():
                valid_dates = presence_data.index[presence_data]  # Get dates where the pattern is True
                if not valid_dates.empty:
                    pattern_prices = data.loc[valid_dates, 'Close']
                    ax.scatter(valid_dates, pattern_prices, label=pattern_name, s=100, marker='o')

            # Fetching support and resistance data for the specific ticker
            supports = self.support_resistance.find_levels()[ticker] \
                if ticker in self.support_resistance.find_levels() else pd.Series()
            resistances = self.support_resistance.find_levels()[ticker] \
                if ticker in self.support_resistance.find_levels() else pd.Series()

            # Plot support levels if they exist
            if not supports.empty:
                ax.scatter(
                    supports.index, supports, color='green', s=100, marker='^', label='Support'
                )
            # Plot resistance levels if they exist
            if not resistances.empty:
                ax.scatter(
                    resistances.index, resistances, color='red', s=100, marker='v', label='Resistance'
                )
            # Formatting the plot
            ax.set_title(
                f'Stock Price ({ticker}) with Candlestick Patterns and Support/Resistance'
            )
            ax.set_xlabel('Date')
            ax.set_ylabel('Price')
            ax.legend()
            ax.grid(True)

            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
