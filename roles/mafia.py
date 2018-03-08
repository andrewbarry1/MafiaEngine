class Mafia(Role):

    def __init__(self, room):
        super().__init__(room)
        name = "Mafia"
        alignment = 1
        night_chat = 0
        allowed_commands["KILL"] = [1]

    def get_night_action(self):
        return "<p>Kill Someone?</p>" # idk if we'll make night kills work this way...

    
    def get_night_vote(self):
        return "VOTE" + #TODO GENERATE LIST OF PEOPLE WHO AREN'T MAFIA
