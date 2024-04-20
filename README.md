Basic Stock Investing Plan

Project Overview

This project is designed to perform an in-depth analysis of each stock within your portfolio, 
providing insights and recommendations on fund allocation to optimize your investment strategy. 
The goal is to help investors allocate their budget to different stocks, 
based on calculated suggestions from the model. The objective of the project is to maximize return over time.


Features
Stock Analysis: Conducts a detailed analysis of each stock in the user's portfolio.
Investment Suggestions: Based on the analysis, suggests how to allocate funds among various stocks to potentially increase returns.
Customizable Budget: Users can specify their investment budget, with a default setting of $100.

Installation
Clone the repository to your local machine:

git clone https://github.com/abrahamchandy95/Basic_Stock_Investing_Plan.git

Prepare Your Portfolio Data:
Create a JSON file that describes your stock portfolio. Refer to the .ipynb files in the test/ directory for examples of how the portfolio JSON should be structured.
The JSON file should include fields such as stock name, ticker symbol, quantity owned, average cost per stock, etc.
Set Your Budget:
In main.py, adjust the budget to reflect the amount you're willing to allocate. The default budget is set to $100.
Run the Analysis:
Execute main.py to see the fund allocation suggestions based on your current portfolio and budget.

Example
Here is an example of what your portfolio JSON might look like:

[
    {
        "stock_name": "Tesla",
        "ticker_symbol": "TSLA",
        "stocks_owned": 10,
        "average_cost": 210
    },
    {
        "stock_name": "Apple",
        "ticker_symbol": "AAPL",
        "stocks_owned": 20,
        "average_cost": 170
    }
]

License
This project is licensed under the MIT License - see the LICENSE.md file for details.
