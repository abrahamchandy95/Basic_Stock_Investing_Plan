import numpy as np
import pandas as pd

from utils import find_nearest_date


class PortfolioAnalysisEngine:
    def __init__(
        self, portfolio_data, market_data, historical_data
    ):
        self.historical_data = historical_data
        self.portfolio_data = pd.DataFrame(portfolio_data)
        self.portfolio_data.set_index('ticker_symbol', inplace=True)
        self.market_data = market_data
        self.metrics = {
            'marketCap': 'high', 'trailingPE': 'low', 'forwardPE': 'low',
            'priceToSalesTrailing12Months': 'low', 'bookValue': 'high',
            'pegRatio': 'low', 'dividendYield': 'high', 'debtToEquity': 'low',
            'returnOnEquity': 'high', 'momentum': 'high', 'portfolioDiversity': 'high',
            'beta': 'low', 'currentRatio':'high', 'quickRatio': 'high', 
            'freeCashflow':'high', 'operatingMargins': 'high', 'ebitdaMargins': 'high',
            'grossMargins': 'high', 'payoutRatio': 'low', 'priceToBook': 'low', 
            'enterpriseToRevenue': 'low', 'enterpriseToEbitda': 'low', 
            'earningsQuarterlyGrowth': 'high', 'revenueGrowth': 'high', 
            'returnOnAssets': 'high', 'operatingCashflow': 'high',
            'averageVolume': 'high', 'volumeChange': 'high', 'sharpe_ratio': 'high'
        }
        self.initialize_weights()

    def initialize_weights(self):
        self.weights = {
            ticker: 1.0 / len(self.market_data) for ticker in self.market_data.index
        }
    
    def normalize_metric(self, series, direction):
        min_val = series.min()
        max_val = series.max()
        if direction == 'high':
            return (series - min_val) / (max_val - min_val)
        return 1 - (series - min_val) / (max_val - min_val)
    
    def normalize_scores(self, dataframe, columns):
        for col in columns:
            min_val = dataframe[col].min()
            max_val = dataframe[col].max()
            dataframe[col] = (dataframe[col] - min_val) / (max_val - min_val)
    
    def calculate_portfolio_diversity(self):
        # Merge 'portfolio_data' with 'market_data' directly on their indices
        self.portfolio_data = self.portfolio_data.merge(
            self.market_data[['currentPrice']],
            left_index=True,
            right_index=True,
            how='left'
        )
        # Calculate total cost and current market value per stock
        self.portfolio_data['total_cost'] = self.portfolio_data['stocks_owned'] * \
            self.portfolio_data['average_cost']
        total_portfolio_value = self.portfolio_data['total_cost'].sum()
        self.portfolio_data['dollar_value'] = self.portfolio_data['stocks_owned'] * \
            self.portfolio_data['currentPrice']
        # Calculate a discount score where larger scores are incentivised
        self.portfolio_data['discount_score'] = (
            self.portfolio_data['average_cost'] - self.portfolio_data['currentPrice']
        ) / self.portfolio_data['average_cost']
        # Balance score where larger scores are deincentivized
        self.portfolio_data['balance_score'] = 1 / (
            self.portfolio_data['dollar_value'] / total_portfolio_value
        )
        # Normalize scores to range between 0 and 1
        self.normalize_scores(
            self.portfolio_data, ['discount_score', 'balance_score']
        )
        # Calculate 'portfolioDiversity' as a weighted sum of 'discount_score' and 'balance_score'
        self.portfolio_data['portfolioDiversity'] = (
            (0.7 * self.portfolio_data['discount_score']) + \
                (0.3 * self.portfolio_data['balance_score'])
        )
        # Merge the portfolio diversity back into the market data
        self.market_data = self.market_data.merge(
            self.portfolio_data[['portfolioDiversity']],
            left_index=True,
            right_index=True,
            how='left'
        )

    def calculate_momentum(self):
        latest_date = pd.Timestamp('today').floor('D') - pd.DateOffset(days=1)
        end_date = latest_date - pd.DateOffset(days=21)
        start_date = end_date - pd.DateOffset(days=230)
        percent_changes = {}
        for ticker, data in self.historical_data.items():
            data = data.sort_index()
            # Find the nearest valid start and end dates
            valid_start_date = find_nearest_date(start_date, data.index)
            valid_end_date = find_nearest_date(end_date, data.index)
            # Calculate percent change if both dates are found
            if pd.notna(valid_start_date) and pd.notna(valid_end_date) \
                and valid_end_date > valid_start_date:
                start_close = data.loc[valid_start_date, 'Close']
                end_close = data.loc[valid_end_date, 'Close']
                percent_change = (end_close - start_close) / start_close
            else:
                percent_change = np.nan
            percent_changes[ticker] = percent_change         
            # Map the percent change (momentum) to the market_data DataFrame
            if ticker in self.market_data.index:
                self.market_data.loc[ticker, 'momentum'] = percent_change
        # Normalize the momentum scores directly within market_data
        self.normalize_scores(self.market_data, ['momentum'])
        
    def calculate_volume_metrics(self):
        for ticker, data in self.historical_data.items():
            if 'Volume' in data.columns:
                data['averageVolume'] = data['Volume'].rolling(window=50).mean()
                data['relativeVolume'] = data['Volume'] / data['averageVolume']
                data['volumeChange'] = data['Volume'].pct_change()
            # Update market data
            for metric in ['averageVolume', 'relativeVolume', 'volumeChange']:
                    self.market_data.at[ticker, metric] = data[metric].dropna().iloc[-1] \
                    if not data[metric].dropna().empty else np.nan
        self.normalize_scores(self.market_data, ['averageVolume', 'relativeVolume', 'volumeChange'])
    
    def calculate_sharpe_ratio(self, risk_free_rate=0.01):
        # formula for daily risk free rate is below
        daily_risk_free_rate = (1 + risk_free_rate) ** (1/252) - 1
        for ticker, data in self.historical_data.items():
            if 'Close' in data.columns:
                # Calculate returns as a pct change
                daily_returns = data['Close'].pct_change()
                excess_daily_returns = daily_returns - daily_risk_free_rate
                # Calculate the mean and standard deviation of excess daily returns
                mean_excess_returns = excess_daily_returns.mean()
                std_excess_returns = excess_daily_returns.std()
                # Calculate Sharpe Ratio and annualize for benchmarch comparison
                if std_excess_returns > 0:
                    sharpe_ratio = mean_excess_returns / std_excess_returns
                    annual_sharpe_ratio = sharpe_ratio * (252 ** 0.5)
                    self.market_data.at[ticker, 'sharpe_ratio'] = annual_sharpe_ratio
                else:
                    self.market_data.at[ticker, 'sharpe_ratio'] = np.nan
            else:
                self.market_data.at[ticker, 'sharpe_ratio'] = np.nan
        # normalize scores
        self.normalize_scores(self.market_data, ['sharpe_ratio'])
                
    def calculate_all_metrics(self):
        self.calculate_volume_metrics()
        for metric, direction in self.metrics.items():
            if metric in self.market_data.columns:
                self.market_data[metric] = self.normalize_metric(
                    self.market_data[metric], direction
                )
        # Calculate fundamental score as the mean of all metrics
        self.market_data['fundamental_score'] = self.market_data[
            list(self.metrics.keys())
        ].mean(axis=1)
        
    def apply_strategy(self):
        
        self.calculate_portfolio_diversity()
        self.calculate_momentum()
        self.calculate_sharpe_ratio()
        self.calculate_all_metrics()

        # Normalize the fundamental scores for proportional adjustment
        max_score = self.market_data['fundamental_score'].max()
        min_score = self.market_data['fundamental_score'].min()
        normalized_scores = (
            self.market_data['fundamental_score'] - min_score
        ) / (max_score - min_score)
        
        # Adjust initial weights based on normalized fundamental scores
        self.weights = {
            ticker: (self.weights[ticker] * normalized_scores.loc[ticker])
            for ticker in self.market_data.index
        }
        # Normalize weights to ensure they sum to 1
        total_weight = sum(self.weights.values())
        self.weights = {
            ticker: weight / total_weight for ticker, weight in self.weights.items()
        }                     