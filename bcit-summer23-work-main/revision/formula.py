
from .operator import Operator
import logging

# Formula class

# This formula class parses an input and converts it to a Formula object. If
# the input is a string, characters like ^, v, and ! will be treated as
# operators and parameters can be only one character in length.
# If the input is a list instead, with operators as instances of the Operator
# class, the parameters can be strings of any length.
# The Formula class also includes some utility functions for comparing formulas.

class Formula:

    def __init__(self, params):

        # If input is a string, convert to list
        if isinstance(params, str):
            params = Formula.convert_str_formula(params) # convert to list
            
        self.formula = Formula.parse_formula(params)
        logging.debug(f"Formula created, list: {self.formula}")
        
        # get unique parameters in formula
        self.param_list = []
        for item in self.formula:
            if isinstance(item, str):
                self.param_list.append(item)
            elif isinstance(item, Formula):
                self.param_list.extend(item.param_list)

        # maintain uniqueness in param list
        self.param_list = list(set(self.param_list))
        self.param_list.sort()

    @staticmethod
    def parse_formula(params):
        # deconstruct list into constituent formulae

        # iterate through input for character
        new_formula = []
        in_paren = False
        paren_defer = 0
        child_formula = []
        for item in params:

            # if parenthesese
            if item == Operator.PARENOPEN:
                # parse parentheses as formula and remove from input
                # search for complete parentheses
                in_paren = True
                paren_defer += 1

            elif item == Operator.PARENCLOSE:
                paren_defer -= 1
                if paren_defer == 0:
                    # out of child formula, create!
                    new_formula.append(Formula(child_formula))
                    child_formula = []
                    in_paren = False
                
            elif in_paren:
                # part of child formula!
                child_formula.append(item)
            
            else:
                # operator or otherwise, add
                new_formula.append(item)
        
        return new_formula

    @staticmethod
    def convert_str_formula(params):
        # convert string formula (from testing) to list
        params = params.replace(" ", "")
        params_new = []
        for char in params:
            if char in "()!^v>=":
                params_new.append(Operator(char))
            else:
                params_new.append(char)
        return params_new

    @staticmethod
    def is_param_subset(formula_a, formula_b):
        for item in formula_a.param_list:
            if item not in formula_b.param_list:
                return False
        return True

    @staticmethod
    def is_param_equal(formula_a, formula_b):
        return formula_a.param_list == formula_b.param_list
    
    def __str__(self):
        # return the full formula as readable string
        formula_full = []
        for item in self.formula:
            if isinstance(item, Formula):
                formula_full.extend(item.formula)
            else:
                formula_full.append(item)
        for index, item in enumerate(formula_full):
            if isinstance(item, Operator):
                formula_full[index] = item.value
        
        joiner = " "
        return f"{joiner.join(formula_full)}"
