from role import Role
from visit import Visit
from enums import *
class Mafia(Role):

    def __init__(self):
        self.name = "Mafia"
        self.alignment = Alignment.mafia
        self.night_chat = Meeting.mafnight

    def get_night_vote(self):
        return self.room.gen_vote_list(self.player, "not mafia")

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
        if mc or mt == VOTE_NL: # tied vote or nl - same thing
            return []
        else:
            return [Visit(self.player.player_number, mt, self.nightkill, VisitPriority.Vote)]
    def nightkill(self, visitor, visited):
        self.room.players[visited].kill()


    def check_win(self, alive):
        n_maf = len([p for p in alive if p.role.alignment == Alignment.mafia])
        n_town = len(alive) - n_maf
        if (n_maf >= n_town):
            return "Mafia"
        else:
            return None
