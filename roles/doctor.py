from role import Role
from visit import Visit
from enums import *
from voting import vote
class Doctor(Role):

    def __init__(self):
        self.name = "Doctor"
        self.alignment = Alignment.town
        self.night_chat = Meeting.doc

    def get_night_vote(self):
        return self.room.gen_vote_list(self.player, "not me")

    def process_night_vote(self, votes):
        (counts, target) = vote(votes)
        if target == VOTE_NL: # tied vote or nl - same thing
            return []
        else:
            return [Visit(self.player.player_number, target, self.save, VisitPriority.Save)]
    def save(self, visitor, visited):
        self.room.players[visited].evars.append("save")
