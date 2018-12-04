from role import Role
from visit import Visit
from enums import *
from voting import vote
class Mafia(Role):

    def __init__(self):
        self.name = "Mafia"
        self.alignment = Alignment.mafia
        self.night_chat = Meeting.mafnight

    def __str__(self):
        return "Mafia"

    def get_night_vote(self):
        return self.room.gen_vote_list(self.player, "not mafia")

    def process_night_vote(self, votes):
        (counts, target) = vote(votes)
        if target == VOTE_NL: # tied vote or nl - same thing
            return []
        else:
            return [Visit(self.player.player_number, target, self.nightkill, VisitPriority.Kill)]
    def nightkill(self, visitor, visited):
        self.room.players[visited].kill()


    def check_win(self, alive):
        n_maf = len([p for p in alive if p.role.alignment == Alignment.mafia])
        n_town = len(alive) - n_maf
        if (n_maf >= n_town):
            return "Mafia"
        else:
            return None
