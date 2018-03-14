# base role - Blue Villager
from visit import Visit
from enums import *
class Role:
    name = "Villager"
    alignment = Alignment.town
    night_chat = Meeting.none
    ready = True
    player = None
    room = None
    day_vote_priority = 1
    
    def __init__(self):
        self.room = None
        self.player = None
    
    def get_night_action(self): # get night action html
        return ''

    def get_day_action(self): # item stuff most likely goes here
        return ''

    def get_night_vote(self): # empty, no vote for villagers at night
        self.ready = True # ready up for the night
        self.player.ready = True
        return "VLIST"
    def get_day_vote(self): # all players
        return self.room.gen_vote_list(self.player, "all")

    def process_night_vote(self, votes):
        return [] # no night vote to process
    def process_day_vote(self, votes): # process day vote (lynch, shared by all roles)
        counts = {}
        for v in votes:
            if v in counts:
                counts[v] += 1
            else:
                counts[v] = 1
        max = 0
        mt = VOTE_NONE
        mc = False
        for k in counts:
            if counts[k] > max:
                max = counts[k]
                mt = k
                mc = False
            elif counts[k] == max:
                mc = True
        if mc or mt == VOTE_NL: # tied vote or nl - same thing
            return []
        else:
            return [Visit(self.player.player_number, mt, self.lynch, VisitPriority.Vote)]
    def lynch(self, visitor, visited):
        self.room.players[visited].kill()

    def get_night_visit(self):
        return []
        

    def action(self, params): # blue villager has no actions
        pass # propagate through to items?


    # Town win condition - no mafia left alive
    def check_win(self, alive):
        n_maf = len([p for p in alive if p.role.alignment == Alignment.mafia])
        if (n_maf == 0):
            return "Village"
        else:
            return None
