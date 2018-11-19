from visit import Visit
from role import Role
from enums import *
from voting import vote
class Cop(Role):

    def __init__(self):
        self.name = "Cop"
        self.alignment = Alignment.town
        self.night_chat = Meeting.cop
        
    def get_night_vote(self):
        return self.room.gen_vote_list(self.player, "not me")

    
    def process_night_vote(self, votes):
        (counts, target) = vote(votes)
        if target == VOTE_NL: # tied vote or nl - same thing
            return []
        else:
            return [Visit(self.player.player_number, target, self.invest, VisitPriority.Most)]

        
    def invest(self, visitor, visited):
        t_align = "the town."
        pname = self.room.players[visited].dname
        if self.room.players[visited].role.alignment == Alignment.mafia:
            t_align = "the mafia."
        self.player.sys("Upon investigation, you realize that " + pname + " is sided with " + t_align)
