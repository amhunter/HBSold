
# utility function for interface
# expands a belief a to include parameters from belief b
def expand_belief(belief_a, belief_b):
    belief_a_params = belief_a[0].keys()
    belief_b_params = belief_b[0].keys()
    new_params = list(set(belief_b_params).difference(belief_a_params))
    new_belief_a = []
    for state in belief_a:
        new_states = [state]
        for param in new_params:
            new_new_states = []
            for item in new_states:
                item_false = item.copy()
                item_false.update({param: False})
                new_new_states.append(item_false)
                item_true = item.copy()
                item_true.update({param: True})
                new_new_states.append(item_true)
            new_states = new_new_states
        new_belief_a.extend(new_states)
    return new_belief_a


# CONVENIENCE PRINT FUNCTIONS #


def tostr_belief_state(belief_state):
    text = ""
    for state in belief_state:
        for prop in state.keys():
            text += str(prop + ": " + str(bool(state[prop])) + " \t")
        text += "\n"
    return text


def tostr_values(values):
    text = "Parameter weights: "
    for value in values.keys():
        text += str(value + ": (" + values[value] + ") ")
    text +="\n"
    return text
