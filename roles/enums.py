from enum import Enum
class Meeting(Enum):
    pregame = -1
    postgame = -2
    none = 0
    day = 1
    mafnight = 2
    # mason, templar, etc go here
    
class Alignment(Enum):
    town = 0
    mafia = 1
    # 3ps can go here

class VisitPriority(Enum):
    MafRB = 1
    TownRB = 2
    Save = 3
    RoleConvert = 4
    Most = 5
    Vote = 6

# some important voting constants
VOTE_NONE = -2
VOTE_NL = -1
