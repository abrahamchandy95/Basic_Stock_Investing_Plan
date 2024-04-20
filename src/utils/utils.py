import numpy as np
import pandas as pd
import yfinance as yf

def find_nearest_date(target_date, index, tolerance_days=5):
    # Ensure the target_date is localized to New York timezone
    if target_date.tzinfo is None \
        or target_date.tzinfo.utcoffset(target_date) is None:
        target_date = pd.Timestamp(target_date).tz_localize('America/New_York')
    else:
        target_date = target_date.tz_convert('America/New_York')
    
    # Generate a date range for the target date with a specified tolerance
    date_range = pd.date_range(
        start=target_date - pd.DateOffset(days=tolerance_days), 
        end=target_date + pd.DateOffset(days=tolerance_days),
        tz='America/New_York'  # Ensure the date range is in the New York timezone
    )

    # Convert the index to New York timezone if it isn't already
    if index.tz is None:
        index = index.tz_localize('America/New_York')
    elif index.tz.zone != 'America/New_York':
        index = index.tz_convert('America/New_York')

    # Find intersection of the provided index with the generated date range
    valid_dates = index.intersection(date_range)
    if not valid_dates.empty:
        # Find the nearest date by calculating minimum absolute difference
        nearest_date = valid_dates[np.abs(valid_dates - target_date).argmin()]
        return nearest_date
    
    return np.nan
    
def get_current_price(stock_symbol):
    stock_data = yf.Ticker(stock_symbol)
    current_price = stock_data.history(period='1d')['Close'][0]
    return current_price