from visit import Visit
from role import Role
from enums import *
class Cop(Role):

    def __init__(self):
        self.name = "Cop"
        self.alignment = Alignment.town
        self.night_chat = Meeting.cop
        
    def get_night_vote(self):
        return self.room.gen_vote_list(self.player, "not me")

    
    def process_night_vote(self, votes):
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
        if mc or mt == VOTE_NL: # tied vote or no one
            return []
        else:
            return [Visit(self.player.player_number, mt, self.invest, VisitPriority.Most)]
    def invest(self, visitor, visited):
        t_align = "the town."
        pname = self.room.players[visited].dname
        if self.room.players[visited].role.alignment == Alignment.mafia:
            t_align = "the mafia."
        self.player.sys("Upon investigation, you realize that " + pname + " is sided with " + t_align)
