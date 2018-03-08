# base role - Blue Villager

class Role:
    name = ""
    alignment = 0
    night_chat = -1
    roleblocked = False
    allowed_commands = {"VOTE":[0,1], "MSG":[0,1]}
    target = -1 # target from night action
    ready = False
    player = None
    
    def __init__(self, room, player):
        self.room = room
        self.player = play
    
    def get_night_action(self): # get night action html
        return ''

    def get_day_action(self): # item stuff most likely goes here
        return ''

    def get_night_vote(self): # empty, no vote for villagers at night
        return "VOTE"
    def get_day_vote(self): # all players
        return "VOTE " + " ".join([str(p.player_number) for p in self.room.players])

    def action(self, params): # blue villager has no actions
        pass # propagate through to items?
