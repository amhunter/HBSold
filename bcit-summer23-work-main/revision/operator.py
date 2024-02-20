
from enum import Enum

# Operator constants for Formula class

class Operator(Enum):

    PARENOPEN = "("
    PARENCLOSE = ")"
    NOT = "!"
    AND = "^"
    OR = "v"
    IMPLY = ">"
    IFF = "="
