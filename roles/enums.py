from enum import Enum
class Meeting(Enum):
    pregame = -1
    postgame = -2
    none = 0
    day = 1
    mafnight = 2
    dead = 3
    cop = 4
    doc = 5

    
class Alignment(Enum):
    town = 0
    mafia = 1

    
class VisitPriority(Enum):
    Vote = 0
    MafRB = 1
    TownRB = 2
    Save = 3
    RoleConvert = 4
    Most = 5
    Kill = 6

    
# some important voting constants
VOTE_NONE = -2
VOTE_NL = -1
