import random
class MafiaRoom:
    players = []
    setup = None
    time = 0
    
    def __init__(self, setup):
        self.players = [] # MafiaPlayer objects
        self.setup = setup

    # add player to room
    def add_player(self, new_player):
        if len(self.players) < len(self.setup):
            self.players.append(new_player)
            for player in self.players:
                player.sendMessage("JOIN " + new_player.name + " " + str(new_player.player_number))
            return False
        else:
            return True





    def command(self, sender, command, params):
        if (command == "MSG"):
            self.msg(params, sender.chat_number, self.alive)
        elif (command == "VOTE"):
            self.vote(self, sender.player_number, sender.chat_number, int(params))
            sender.vote(int(params))
            check_advance_time()
        elif (command == "ACTION"):
            sender.role.action(params)
            check_advance_time()


    def check_advance_time(self):
        advance_day = True
        for player in self.players:
            if not(player.ready()):
                advance_day = False
        if (advance_day):
            advance_time()


    def advance_time(self): # entire game cycle basically
        time += 1
        if (time == 0): # setup the entire game
            random.shuffle(self.players)
            for i in range(len(self.players)): # randomly assign roles
                self.players[i].role = self.setup[i]
            pass # TODO
        if (time % 2 == 0): # night time
            # TODO process day actions, votes
            for p in self.players:
                p.chat_number = p.role.night_chat
                p.vote = -2
                p.role.get_night_action()
        elif (time % 2 == 1): # day time
            pass # TODO process all night actions, set to day

    # send message to other people in this chat (day, maf night, town night, etc)
    def msg(self, message, chat_number, alive):
        if chat_number == -1:
            return
        else:
            for player in [p for p in self.players if p.chat_number == chat_number or not p.alive]:
                player.sendMessage("MSG " + message)
                
    def vote(self, voter_n, chat_n, target_n):
        if chat_n == -1:
            return
        else:
            for player in [p for p in self.players if p.chat_number == chat_number or not p.alive]:
                player.sendMessage("VOTE " + str(voter_n) + " " + str(target_n))
