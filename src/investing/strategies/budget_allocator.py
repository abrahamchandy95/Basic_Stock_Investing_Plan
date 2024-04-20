from analysis import PortfolioAnalysisEngine


class BudgetAllocator:
    def __init__(
        self, budget, market_data, historical_data, portfolio_data, weights
    ) -> None:
        self.budget = budget
        self.market_data = market_data
        self.historical_data = historical_data
        self.portfolio_data = portfolio_data
        self.portfolio_analyzer = PortfolioAnalysisEngine(
            self.portfolio_data, self.market_data, self.historical_data
        )
        self.weights = weights
        self.minimum_allocation = 5
        
    def allocate_budget(self):
        """
        Allocates the budget based on weights
        """
        initial_allocations = {
            ticker: round(self.budget * self.weights[ticker], 2) \
                for ticker in self.weights
        }
        allocations = {
            ticker: value if value >= self.minimum_allocation else 0 \
                for ticker, value in initial_allocations.items()
        }
        # Removing allocations that are less than the minimum threshold
        for ticker, value in list(allocations.items()):
            if 0 == value:
                allocations.pop(ticker)
        
        total_allocated = sum(allocations.values())
        remaining_budget = self.budget - total_allocated
        
        if remaining_budget > 0:
            allocations = self.redistribute_remaining_budget(allocations, remaining_budget)
        # Fix rounding errors
        self.adjust_for_rounding_errors(allocations)
        return allocations
    
    def redistribute_remaining_budget(self, allocations, remaining_budget):
        """
        Redistributes any remaining budget proportionally to stocks above the minimum threshold

        Args:
            allocations (dict): Money allocated for each stock 
            remaining_budget (float): budget remaining after eliminating 
            money alloted to stocks under minimum threshold
        """
        total_weight_allocated = sum(
            self.weights[ticker] for ticker in allocations
        )
        additional_allocations = {
            ticker: (self.weights[ticker] / total_weight_allocated) * \
                remaining_budget for ticker in allocations
        }
        for ticker, additional_amount in additional_allocations.items():
            allocations[ticker] += round(additional_amount, 2)
            
        return allocations
    
    def adjust_for_rounding_errors(self, allocations):
        """
        Adjusts the final allocations to match the budget exactly, ensuring no negative allocations.

        Args:
            allocations (dict): Money allocated for each stock 
        """
        total_allocation = sum(allocations.values())
        rounding_error = self.budget - total_allocation
        if rounding_error != 0:
            # If rounding error is positive, add it to the ticker with the max allocation
            if rounding_error > 0:
                ticker_with_max_allocation = max(allocations, key=allocations.get)
                allocations[ticker_with_max_allocation] += rounding_error
            else:
                
                sorted_tickers = sorted(allocations, key=allocations.get, reverse=True)
                for ticker in sorted_tickers:
                    max_adjustable = allocations[ticker] - self.minimum_allocation
                    adjustment = max(rounding_error, - max_adjustable)
                    allocations[ticker] += adjustment
                    rounding_error -= adjustment
                    if rounding_error == 0:
                        break

            # Ensure all allocations are rounded to 2 decimal places after adjustments
            for ticker in allocations:
                allocations[ticker] = round(allocations[ticker], 2)

    
    def set_minimum_allocation(self, minimum_allocation):
        """
        Allows setting a new minimum allocation amount if needed
        Args:
            minimum_allocation (int): Lowest investment permitted per stock
        """
        self.minimum_allocation = minimum_allocation