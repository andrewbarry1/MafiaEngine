from role import Role
from visit import Visit
from enums import *
class Doctor(Role):

    def __init__(self):
        self.name = "Doctor"
        self.alignment = Alignment.town
        self.night_chat = Meeting.doc

    def get_night_vote(self):
        return self.room.gen_vote_list("all")

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
            return [Visit(self.player.player_number, mt, self.save, VisitPriority.Save)]
    def save(self, visitor, visited):
        self.room.players[visited].evars.append("save")
