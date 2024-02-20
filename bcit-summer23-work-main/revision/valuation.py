
# Valuation class

# Belief states are expected to be a list of dicts, with the dicts representing
# the truth/falsity of propositions.
# E.g. [ {"a":True, "b":False}, {"a":False, "b":False} ]
# Agent is the associated agent, None meaning an observation.
# Formula is an optional argument which can make the valuation have an
# associated formula.

class Valuation:

    def __init__(self, belief_state, agent, formula=None):
        self.belief_state = belief_state
        self.agent = agent
        self.formula = formula
