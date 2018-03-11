class Doctor(Role):

    def __init__(self):
        super().__init__()
        self.name = "Doctor"
        self.alignment = 0
        self.night_chat = 2

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
        mt = -2
        mc = False
        for k in counts:
            if counts[k] > max:
                max = counts[k]
                mt = k
                mc = False
            elif counts[k] == max:
                mc = True
        if mc or mt == -1: # tied vote or no one
            return []
        else:
            return [Visit(self.player.player_number, mt, save, 2)]
    def save(self, visitor, visited):
        self.room.players[visited].evars.append("save")
