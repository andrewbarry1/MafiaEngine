# base role - Blue Villager
from enums import *
class Role:
    name = ""
    alignment = Alignment.town
    night_chat = Meeting.none
    ready = False
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
        return "VOTE"
    def get_day_vote(self): # all players
        return self.room.gen_vote_list("all")

    def process_night_vote(self, votes):
        return None # no night vote to process
    def process_day_vote(self, votes): # process day vote (lynch, shared by all roles)
        counts = {}
        for v in votes:
            if v in counts:
                counts[v] += 1
            else:
                counts[v] = 1
        max = 0
        mt = -2
        mc = False
        for k in counts:
            if counts[k] > max:
                max = counts[k]
                mt = k
                mc = False
            elif counts[k] == max:
                mc = True
        if mc or mt == -1: # tied vote or nl - same thing
            return None
        else:
            return [Visit(self.player.player_number, mt, lynch, VisitPriority.Vote)]
    def lynch(self, visitor, visited):
        self.room.players[visited].alive = False

    def get_night_visit():
        return []
        

    def action(self, params): # blue villager has no actions
        pass # propagate through to items?
