
from .formula import Formula
from .valuation import Valuation
from .distance_finder import HammingDistanceFinder
from .distance_finder import WeightedHammingFinder
from .distance_finder import ParamDistanceFinder
import logging
from itertools import combinations
from math import floor

# Trust revision implementation
# Explanation of the trust revision process is included in the README

# Trust variables
TRUST_OBS_DECREASE = 1.0
TRUST_OBS_INCREASE = 1.0
TRUST_DECREASE = 1.0
TRUST_INCREASE = 1.0
NOTRUST_THRESHOLD = 0
DIFF_THRESHOLD = 100

class TrustThreshold:

    def __init__(self,
                 obs_decrease=TRUST_OBS_DECREASE,
                 obs_increase=TRUST_OBS_INCREASE,
                 decrease=TRUST_DECREASE,
                 increase=TRUST_INCREASE,
                 notrust_threshold=NOTRUST_THRESHOLD,
                 diff_threshold=DIFF_THRESHOLD):
        self.obs_decrease = obs_decrease
        self.obs_increase = obs_increase
        self.decrease = decrease
        self.increase = increase
        self.notrust_threshold = notrust_threshold
        self.diff_threshold = diff_threshold

# Belief revision functions

# belief reviser
# input: a list of states (dicts of t/f values) and a new list of states
# output: a consistent state closest to the list input
def revise_belief(current_belief, new_belief, values, distance_finder):

    belief_distances = []

    minimum_dist = 9999
    #for new_state in evaluate_formula(new_formula):
    for new_state in new_belief:
        distance = 9999
        for old_state in current_belief:
            new_distance = distance_finder.get_distance(old_state,
                                                        new_state,
                                                        values)
            if new_distance < distance:
                distance = new_distance
            if new_distance < minimum_dist:
                minimum_dist = new_distance
        # add new state with distance as a mini list to list
        belief_distances.append((new_state, distance))

    new_belief_state = []
    for state, dist in belief_distances:
        if dist == minimum_dist:
            new_belief_state.append(state)

    # return new state and a boolean of if the states overlapped or not
    return new_belief_state, minimum_dist > 0


def trust_revise_beliefs(current_belief, values, *new_beliefs, trusted_agents=None,
                         distance_finder=None, trust_thresholds=None):

    if distance_finder is None:
        distance_finder = HammingDistanceFinder()

    if trust_thresholds is None:
        trust_thresholds = TrustThreshold()

    logging.debug(f"Values for trust thresholds: {trust_thresholds.obs_increase, trust_thresholds.obs_decrease, trust_thresholds.increase, trust_thresholds.decrease, trust_thresholds.notrust_threshold, trust_thresholds.diff_threshold}")

    # if at least one observation, then result must match observation
    # and information outside it should be ignored
    confidence = False
    # count observations as separate
    observations = [belief for belief in new_beliefs if belief.agent is None]
    # info from non-observation agents
    agent_beliefs = [belief for belief in new_beliefs if belief.agent is not None]

    # step 1: if observations, limit result to observations
    # and check agent beliefs for agreeing/disagreeing with result
    if len(observations) > 0:
        confidence = True
        total_observation = observations[0].belief_state
        
        for observation in observations:
            new_belief, belief_jump = revise_belief(current_belief.belief_state,
                                                    observation.belief_state,
                                                    values, distance_finder)
            # belief_jump unused since observations cannot be ignored
            current_belief = Valuation(new_belief, None)
            # set minimum observation
            total_observation, extra = revise_belief(total_observation,
                                                     observation.belief_state,
                                                     values, distance_finder)

        # check for items that agree/disagree with observation
        # change trust, and skip beliefs that disagree with observation entirely
        for agent_belief in agent_beliefs[:]:
            
            new_belief, belief_jump = revise_belief(total_observation,
                                                    agent_belief.belief_state,
                                                    values, distance_finder)
            if belief_jump:
                agent_beliefs.remove(agent_belief)
                trusted_agents[agent_belief.agent] *= trust_thresholds.obs_decrease
            else:
                trusted_agents[agent_belief.agent] *= trust_thresholds.obs_increase

    # step 2: compare beliefs against each other
    # to check for large trust differences
    # and discard less trusted suggestions
    for agent_a, agent_b in combinations(agent_beliefs[:], 2):
        
        new_belief, belief_jump = revise_belief(agent_a.belief_state,
                                                agent_b.belief_state,
                                                values, distance_finder)
        trust_diff = trusted_agents[agent_a.agent] - trusted_agents[agent_b.agent]
        # get less trusted agent
        worse_agent = agent_b if trust_diff > 0 else agent_a
        # check if difference passes threshold
        if abs(trust_diff) >= trust_thresholds.diff_threshold:
            # check if overlap
            # if not, don't trust worse agent, remove from list
            if belief_jump:
                trusted_agents[worse_agent.agent] *= trust_thresholds.decrease
                try:
                    agent_beliefs.remove(worse_agent)
                except ValueError:
                    pass # already removed from main list
            # otherwise trust worse agent slightly more
            else:
                trusted_agents[worse_agent.agent] *= trust_thresholds.increase

    # step 3: revise by remaining beliefs
    for agent_belief in agent_beliefs:

        if trusted_agents[agent_belief.agent] <= trust_thresholds.notrust_threshold:
            continue

        new_belief, belief_jump = revise_belief(current_belief.belief_state,
                                                agent_belief.belief_state,
                                                values, distance_finder)
        
        # check if outside current observation belief
        if confidence and belief_jump:
            truncated_state = [state for state in agent_belief.belief_state
                               if state in total_observation]
            if len(truncated_state) > 0:
                new_belief, belief_jump = revise_belief(current_belief.belief_state,
                                                        truncated_state,
                                                        values, distance_finder)
                current_belief = Valuation(new_belief, None)
            
        else:
            current_belief = Valuation(new_belief, None)

        # cap belief values
        trusted_agents[agent_belief.agent] = floor(trusted_agents[agent_belief.agent])
        if trusted_agents[agent_belief.agent] < 0:
            trusted_agents[agent_belief.agent] = 0
        if trusted_agents[agent_belief.agent] > 100:
            trusted_agents[agent_belief.agent] = 100

    return current_belief

