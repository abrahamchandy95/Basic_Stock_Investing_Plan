import yfinance as yf


class StockDataFetcher:
    def __init__(self, portfolio):
        """
        Initializes the class with a portfolio.
        :param portfolio: A list of dictionaries, each containing the ticker symbol of a stock
        """
        self.portfolio = portfolio
    
    def get_historical_data(self, period="10y", interval="1d"):
        """
        The function gets 10 year stock data from yahoo finance for all stocks
        Args:
            period (str, optional): Time Intended for analysis Defaults to "10y".
            interval (str, optional): _description_. Defaults to "1d".
        Returns:
            dict: Dictionary of all stock data in the portfolio
        """
        historical_data = {}
        for stock in self.portfolio:
            ticker = yf.Ticker(stock['ticker_symbol'])
            data = ticker.history(period=period, interval=interval)
            historical_data[stock['ticker_symbol']] = data
        return historical_data
    
    def fetch_current_market_data(self):
        """
        The function gets the current information, including all metrics
        of every stock in the portfolio

        Returns:
            dict: Dictionary of dataframes 
        """
        market_dict = {}
        for stock in self.portfolio:
            ticker = yf.Ticker(stock['ticker_symbol'])
            market_dict[stock['ticker_symbol']] = ticker.info
        return market_dict
    
    def fetch_financials(self):
        """
        Gets financial data for the last four years

        Returns:
            dict: Dictionary of all stocks financial data
        """
        financial_data = {}
        for stock in self.portfolio:
            ticker_symbol = stock['ticker_symbol']
            ticker = yf.Ticker(ticker=ticker_symbol)
            financial_data[ticker_symbol] = {
                'annual_financials': ticker.financials,
                'quarterly_financials': ticker.quarterly_financials,
            }
        return financial_data