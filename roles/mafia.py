from role import Role
from enums import *
class Mafia(Role):

    def __init__(self):
        super().__init__()
        name = "Mafia"
        alignment = Alignment.mafia
        night_chat = Meeting.mafnight

    def get_night_vote(self):
        return self.room.gen_vote_list("not mafia")

    def process_night_vote(self, votes):
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
            return []
        else:
            return [Visit(self.player.player_number, mt, nightkill, VisitPriority.Vote)]
    def nightkill(self, visitor, visited):
        self.room.players[visited].alive = False


    def check_win(self, alive):
        n_maf = len([p for p in alive if p.alignment == Alignment.mafia])
        n_town = len(alive) - n_maf
        if (n_maf >= n_town):
            return "Mafia"
        else:
            return None
