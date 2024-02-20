
from abc import ABC, abstractmethod

# Distance finder abstract and concrete classes

# The following classes implement distance finding algorithms required for
# the trust revision process. Only basic Hamming Distance and Weighted
# Hamming distance are included, and the extra Parametrized Distance is
# not distinct from them.

class AbstractDistanceFinder(ABC):

    @abstractmethod
    def get_distance(self, state_a, state_b, args=None):
        pass


class HammingDistanceFinder(AbstractDistanceFinder):

    def get_distance(self, state_a, state_b, args=None):
        dist = 0
        for item in set(list(state_a.keys())+list(state_b.keys())):
            if item in state_a and item in state_b and state_a[item] != state_b[item]:
                dist += 1
            # elif item in state_a and int(state_a[item]) == 1:
            #     dist += 1
            # elif item in state_b and int(state_b[item]) == 1:
            #     dist += 1                
        return dist


class WeightedHammingFinder(AbstractDistanceFinder):

    def get_distance(self, state_a, state_b, args):
        dist = 0
        for item in state_a:
            if int(state_a[item]) != int(state_b[item]):
                dist += int(args[item])
        return dist


class ParamDistanceFinder(AbstractDistanceFinder):

    def get_distance(self, state_a, state_b, args):
        dist = 0
        for item in state_a:
            if int(state_a[item]) != int(state_b[item]):
                dist += int(args[item])
        return dist
