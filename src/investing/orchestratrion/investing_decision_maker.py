from strategies import (
    AnalysisImplementor, StrategyExecutor, BudgetAllocator 
)
from analysis import PortfolioAnalysisEngine


class InvestmentDecisionMaker:
    
    def __init__(
        self, historical_data, market_data, portfolio_data, budget
    ):
        self.historical_data = historical_data
        self.market_data = market_data
        self.portfolio_data = portfolio_data
        self.portfolio_analyzer = PortfolioAnalysisEngine(portfolio_data, market_data, historical_data)
        self.analysis_implementor = AnalysisImplementor(historical_data, market_data)
        self.strategy_exeutor = StrategyExecutor(market_data, self.portfolio_analyzer)
        self.budget_allocator = None  
        self.budget = budget

    def execute_strategy(self):
        # Perform all market and financial analyses
        self.analysis_implementor.implement_all_analysis()
        self.strategy_exeutor.adjust_weights()
        self.budget_allocator = BudgetAllocator(
            self.budget, self.market_data, self.historical_data, 
            self.portfolio_data, self.strategy_exeutor.weights
        )
        # Allocate budget based on the adjusted weights
        allocations = self.budget_allocator.allocate_budget()

        return allocations