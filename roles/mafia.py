class Mafia(Role):

    def __init__(self):
        super().__init__()
        name = "Mafia"
        alignment = 1
        night_chat = 1

    def get_night_vote(self):
        return "VOTE " + " ".join([p.name for p in self.room.players if not(p.alignment == 1)])

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
            return None
        else:
            return Visit(self.player.player_number, mt, nightkill, 2)
    def nightkill(self, visitor, visited):
        self.room.players[visited].alive = False
