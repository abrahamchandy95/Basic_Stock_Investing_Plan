import pandas as pd


class ETFDataFiller:
    def __init__(self, market_data, data_fetcher):
        """
        Initializes the ETFDataFiller with market data and a data fetching class that provides ETF data.
        
        :param market_data: DataFrame containing the market data with tickers as indices.
        :param data_fetcher: An instance of a class that can provide ETF data
        """
        self.market_data = market_data
        self.data_fetcher = data_fetcher
        self.mapping = {
            'currentPrice': 'navPrice',
            'beta': 'beta3Year',
            'dividendYield': 'trailingAnnualDividendYield',
            'marketCap': 'totalAssets',
            'returnOnEquity': 'threeYearAverageReturn',
        }
        self.etf_relevant_keys = [
            'trailingAnnualDividendRate', 'trailingAnnualDividendYield', 
            'lastDividendValue', 'lastDividendDate', 'yield', 
            'navPrice', 'category', 'ytdReturn', 'beta3Year', 
            'threeYearAverageReturn', 'totalAssets', 
        ]

    def is_etf(self, ticker):
        """ 
        Determine if the ticker is an ETF by checking if all mapped fields in market_data are NaN. 
        """
        return all(pd.isna(self.market_data.at[ticker, col]) for col in self.mapping)

    def get_etf_data(self, ticker):
        """ 
        Retrieve and filter data for a specific ETF based on relevant keys. 
        """
        etf_data = {}
        full_etf_data = self.data_fetcher.fetch_current_market_data()[ticker] 
        for key in full_etf_data:
            if key in self.etf_relevant_keys:
                etf_data[key] = full_etf_data[key]
        return etf_data

    def fill_data(self, ticker):
        """ 
        Fill NaN values in the market data for a specific 
        ticker using the ETF data provided.
        """
        if self.is_etf(ticker):
            etf_data = self.get_etf_data(ticker)
            for market_col, etf_col in self.mapping.items():
                if pd.isna(self.market_data.at[ticker, market_col]) \
                    and etf_col in etf_data:
                    self.market_data.at[ticker, market_col] = etf_data[etf_col]

    def fill_all_etfs(self):
        """ 
        Identify and fill data for all ETFs in the market_data DataFrame. 
        """
        for ticker in self.market_data.index:
            if self.is_etf(ticker):
                self.fill_data(ticker)

    def display_data(self):
        """ Utility method to display the DataFrame. """
        print(self.market_data)