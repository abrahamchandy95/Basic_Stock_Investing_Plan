import pandas as pd


class FeatureEngineering:
    def __init__(self, market_dict, historical_data, financial_data):
        self.market_dict = market_dict
        self.historical_data = historical_data
        self.financial_data = financial_data
        self.info_fields = {
            'marketCap', 'trailingPE', 'forwardPE', 'priceToSalesTrailing12Months',
            'bookValue', 'pegRatio', 'dividendYield', 'debtToEquity', 'returnOnEquity',
            'beta', 'currentRatio', 'quickRatio', 'freeCashflow', 'operatingMargins', 
            'ebitdaMargins', 'grossMargins', 'payoutRatio', 'priceToBook', 'enterpriseToRevenue',
            'enterpriseToEbitda', 'earningsQuarterlyGrowth', 'revenueGrowth', 
            'returnOnAssets', 'operatingCashflow', 'dividendYield', 'volume', 'currentPrice'
        }
        
    def structure_historical_data(self):
        structured_data = []
        for ticker, data in self.historical_data.items():
            # Assign 'Ticker' to each DataFrame and convert it to a column
            data['Ticker'] = ticker
            # Set 'Date' and 'Ticker' as a multi-level index
            data.set_index(['Ticker'], append=True, inplace=True)
            structured_data.append(data)
        consolidated_history = pd.concat(structured_data, ignore_index=False)
        return consolidated_history
    
    def consolidate_financials(self):
        annual_financials = pd.DataFrame()
        quarterly_fianancials = pd.DataFrame()
        for ticker_symbol, data in self.financial_data.items():
            for report_type in ['annual_financials', 'quarterly_financials']:
                df = data[report_type].copy()
                if not pd.api.types.is_datetime64_any_dtype(df.columns):
                    df = df.transpose()
                df = df.reset_index().melt(
                    id_vars='index', var_name='Date', value_name='Value'
                )
                df.columns = ['Financial_Metric', 'Date', 'Value']
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                df['Ticker'] = ticker_symbol
            if report_type == 'annual_financials':
                annual_financials = pd.concat(
                    [annual_financials, df], ignore_index=True
                )
            elif report_type == 'quarterly_financials':
                quarterly_fianancials = pd.concat(
                    [quarterly_fianancials, df], ignore_index=True
                )
            if not annual_financials.empty:
                annual_financials.set_index('Date', inplace=True)
            if not quarterly_fianancials.empty:
                quarterly_fianancials.set_index('Date', inplace=True)
        return annual_financials, quarterly_fianancials
                
    def consolidate_info_fields(self):
        info_data = []
        for ticker, value in self.market_dict.items():
            info_dict = {field: value.get(field, None) for field in self.info_fields}
            info_dict['Ticker'] = ticker
            info_data.append(info_dict)
        info_dataframe = pd.DataFrame(info_data)
        info_dataframe.set_index('Ticker', inplace=True)
        return info_dataframe
            
                
        
                