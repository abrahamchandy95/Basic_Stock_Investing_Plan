import pandas as pd
import numpy as np


class MarkovModel:
    """
    A statistical model for randomly changing systems that assumes
    that future states depend on the current state and not the sequence
    of events preceeding it
    """
    def __init__(self, data, years=3) -> None:
        self.original_data = data
        self.historical_data = self.limit_data_to_recent_years(data, years)
        self.thresholds = {}
        self.states = {}
        self.transition_matrices = {}
    
    def limit_data_to_recent_years(self, data, years):
        """ Limit data to the most recent years specified. """
        current_date = pd.to_datetime('today').tz_localize('America/New_York')
        cutoff_date = current_date - pd.DateOffset(years=years)
        return data[data.index >= cutoff_date]
        
    def calculate_thresholds(self):
        data = self.historical_data
        price_changes = data['Close'].pct_change().dropna()
        mean_change = price_changes.mean()
        std_dev = price_changes.std()
        
        # Define thresholds for significant and minor changes
        self.thresholds = {
            'significant': mean_change + std_dev,
            'minor': mean_change
        }
        
    def define_states(self):
        """
        Let S be a finite set of states in the Markov model, denoted as 
        S = {s1, s2, s3, s4, .. , sn}
        the probability of moving from one probability to another is P = [pij]
        pij = P(Xt+1 = sj | Xt = si)
        """
        self.calculate_thresholds()
        price_changes = self.historical_data['Close'].pct_change().dropna()
        significant = self.thresholds['significant']
        minor = self.thresholds['minor']

        self.states = price_changes.apply(
            lambda change:
                0 if change <= -significant else
                1 if -significant < change <= -minor else
                2 if -minor < change <= minor else
                3)
    
    def markov_chain_transition_matrix(self):
        """
        Shows the probability of each state going to the other side
        """
        self.define_states()
        states = self.states
        transition_matrix = pd.crosstab(states, states.shift(-1), normalize='index')
        self.transition_matrices = transition_matrix
        return self.transition_matrices

    def predict_next_state(self):
        """
        Uses the transition matrix to predict the next state 
        based on the current state’s probabilities.
        """
        transition_matrix = self.markov_chain_transition_matrix()
        current_state = self.states.iloc[-1]
        next_state_probabilities = transition_matrix.loc[current_state]
        next_state = np.random.choice(
            next_state_probabilities.index, p=next_state_probabilities.values
        )
        return next_state

