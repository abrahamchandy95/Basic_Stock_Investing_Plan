# Import necessary modules from the project structure
from config import load_portfolio_data, PORTFOLIO_PATH
from src.data import StockDataFetcher, FeatureEngineering, ETFDataFiller
from src.investing.orchestratrion import InvestmentDecisionMaker, PortfolioUpdator

def main():
    # Load the portfolio data from a predefined path
    my_portfolio = load_portfolio_data(PORTFOLIO_PATH)

    # Create a data fetcher instance with the portfolio
    data_fetcher = StockDataFetcher(portfolio=my_portfolio)

    # Fetch historical, financial, and current market data
    historical_data = data_fetcher.get_historical_data()
    financial_data = data_fetcher.fetch_financials()
    market_dict = data_fetcher.fetch_current_market_data()

    # Process the fetched data through feature engineering
    feature_engineering = FeatureEngineering(market_dict, historical_data, financial_data)
    market_data = feature_engineering.consolidate_info_fields()

    # Fill the ETF data using the processed market data
    etf_filler = ETFDataFiller(market_data, data_fetcher)
    etf_filler.fill_all_etfs()

    # Make investment decisions based on the processed data
    decision = InvestmentDecisionMaker(historical_data, market_data, my_portfolio, 100)
    money_allocated_per_company = decision.execute_strategy()

    # Update the portfolio file 
    updator = PortfolioUpdator(PORTFOLIO_PATH)
    updator.save_portfolio()

    # Print the results of the investment decision
    print(money_allocated_per_company)

if __name__ == "__main__":
    main()
