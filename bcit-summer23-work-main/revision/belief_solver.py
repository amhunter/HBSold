
from .operator import Operator
from .formula import Formula
import itertools

# The following functions use the Formula and Operator class to implement
# a satisfiability checker, converting a formula to a list of states where
# the formula is true for its parameters.
# Only the last function, evaluate_formula(formula), is used outside of this
# file.

# Formula solver functions

def sat_operator_mapper(left, operator, right):
    
    # map operators and values
    if operator == Operator.AND:
        valuemap = {"00":"0", "10":"0", "01":"0", "11":"1"}
    elif operator == Operator.OR:
        valuemap = {"00":"0", "10":"1", "01":"1", "11":"1"}
    elif operator == Operator.IMPLY:
        valuemap = {"00":"1", "10":"0", "01":"1", "11":"1"}
    elif operator == Operator.IFF:
        valuemap = {"00":"1", "10":"0", "01":"0", "11":"1"}
    
    return valuemap[str(int(left)) + str(int(right))] == "1"

    
def check_satisfied(formula, valuation):
    # formula and valuation map (e.g. {p:1, q:0, r:1})
    # recurses and returns true/false for given formula
    #logging.debug(f"Checking satisfaction for {formula} with valuation {valuation}")

    # if only a prop, return value
    if len(formula.formula) == 1:
        value = formula.formula[0]
        if isinstance(value, bool):
            return value
        elif isinstance(value, str):
            return valuation[formula.formula[0]]
        else:
            pass # formula, no return yet

    # iterate through formula list to get values from recursion
    local_formula = formula.formula.copy()
    for index, item in enumerate(formula.formula):
        if isinstance(item, Formula):
            local_formula[index] = check_satisfied(item, valuation)

    # do the math for the results
    buffer = []
    for element in local_formula:

        # add valuation or operator
        if isinstance(element, Operator) or isinstance(element, bool):
            buffer.append(element)
        else:
            buffer.append(valuation[element])

        # deal with negation
        if len(buffer) >= 2 and buffer[-2] == Operator.NOT:
            buffer[-1] = not buffer[-1] # invert last formula
            del buffer[-2]

        # send to resolver thing
        if len(buffer) == 3 and Operator.NOT not in buffer:
            buffer = [sat_operator_mapper(*buffer)]

    # should have one item in list as T/F value left
    return buffer[0]


def evaluate_formula(formula):
    # 1. get list of unique propositions
    props = formula.param_list
    # 2. iterate through brute force combinations of T/F values
    permutations = itertools.product((False, True), repeat=len(props))
    valuations = []
    for permutation in permutations:
        valuations.append(dict(zip(props, permutation)))
    # 3. for each, run recursive sat checker to see if valuation satisfies
    true_valuations = []
    for valuation in valuations:
        if check_satisfied(formula, valuation):
            true_valuations.append(valuation)
    
    return true_valuations
