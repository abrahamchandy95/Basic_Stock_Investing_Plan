import datetime
import json

from config import load_config_file, PORTFOLIO_PATH
from utils import get_current_price

class PortfolioUpdator:
    def __init__(self, filename):
        self.filename = filename
        self.portfolio = load_config_file(PORTFOLIO_PATH)

    def update_portfolio(self, allocations):
        current_date = datetime.today().strftime('%Y-%m-%d')
        for stock in self.portfilio:
            ticker = stock['ticker_symbol']
            if ticker in allocations:
                allocated_amount = allocations[ticker]
                if allocated_amount > 0:
                    current_price = get_current_price(ticker)
                    stock['stocks_owned'] += allocated_amount / current_price
                    stock['average_cost'] = (
                        stock['average_cost'] * stock['stocks_owned'] + allocated_amount
                    ) / (
                        stock['stocks_owned'] + allocated_amount / current_price
                    )
                    stock['as_of_date'] = current_date
    
    def save_portfolio(self):
        """ Save the updated portfolio back to the JSON file. """
        with open(self.filename, 'w') as file:
            json.dump(self.portfolio, file, indent=4)
        