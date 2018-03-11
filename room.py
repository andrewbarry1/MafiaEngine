import random
class MafiaRoom:
    players = []
    setup = None
    time = -1
    visits = []
    
    def __init__(self, setup):
        self.players = [] # MafiaPlayer objects
        self.setup = setup
        self.callbacks = {"day_end":[], "vote":[], "msg":[], "night_end":[]}

    # add player to room
    def add_player(self, new_player):
        if len(self.players) < len(self.setup):
            self.players.append(new_player)
            new_player.player_number = len(self.players) - 1
            for player in self.players:
                player.sendMessage("JOIN " + new_player.name + " " + str(new_player.player_number))
            return False
        else:
            return True





    def command(self, sender, command, params):
        if (command == "READY"):
            sender.ready = True
            check_advance_time()
        elif (command == "MSG"):
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
        if (time == 0): # setup the entire game # TODO I'm probably forgetting something
            random.shuffle(self.setup)
            for i in range(len(self.players)): # randomly assign roles
                self.players[i].role = self.setup[i]
                


        
        if (time % 2 == 0): # moving to night time
            # TODO process day actions
            vote_processor = self.players[0]
            for p in self.players:
                if (p.day_vote_priority > vote_processor.day_vote_priority):
                    vote_processor = p
                p.setMeeting(p.role.night_chat)
                p.role.get_night_action()
            v = vote_processor.process_day_vote(votes)
            if not(v is None):
                v.callback(v.visitor, v.visited) # do the lynch


                
        elif (time % 2 == 1): # moving to day time
            self.visits = []
            voted_chats = []
            for p in self.players: # 1. generate visits
                v = p.get_night_visit()
                if v is not None:
                    self.visits.append(v)
                if (p.night_chat not in voted_chats):
                    votes = [pl.vote for pl in self.players where pl.chat_number == p.chat_number]
                    v2 = p.process_night_vote(votes)
                    if not(v2 is None):
                        self.visits.append(v2)
            '''
            priority for night visits is this:
            1. Maf RBs 2. Town RBs 3. All role conversions 4. Everything else 5. Votes
            '''
            for v in sorted(self.visits): # 2. do all visits in priority order
                v.callback(v.visitor, v.visited)
            # 3. reset everything, dump them all into town chat
            for p in self.players:
                p.vote = -2
                p.setMeeting(1)
            
            

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
