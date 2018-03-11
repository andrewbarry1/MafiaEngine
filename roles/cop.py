class Cop(Role):

    def __init__(self):
        super().__init__()
        self.name = "Cop"
        self.alignment = Alignment.town
        self.night_chat = Meeting.none

    def gen_night_vote(self):
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
            return [Visit(self.player.player_number, mt, invest, VisitPriority.Most)]
    def save(self, visitor, visited):
        t_align = "the town."
        pname = self.room.players[visited].name
        if self.room.players[visited].alignment == 1:
            t_align = "the mafia."
        self.player.sys("Upon investigation, you realize that " + pname + " is sided with " + t_align)
