import random
from visit import Visit
from roles.enums import *
class MafiaRoom:
    players = []
    setup = None
    time = -1
    visits = []
    
    def __init__(self, setup):
        self.players = [] # MafiaPlayer objects
        self.setup = setup

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
            sender.vote(int(params))
            check_advance_time()
        elif (command == "ACTION"):
            sender.role.action(params)
            check_advance_time()

    def gen_vote_list(self, vt):
        if (vt == "all"):
            return "VOTE " + " ".join([str(p.player_number) for p in self.players if p.alive])
        elif (vt == "not mafia"):
            return "VOTE " + " ".join([str(p.player_number) for p in self.players if p.alive and not(p.alignment == Alignment.mafia)])
        else:
            return [] # cult stuff, masons, etc can go here
            

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
            vote_processor = self.players[0]
            for p in self.players:
                if (p.day_vote_priority > vote_processor.day_vote_priority):
                    vote_processor = p
                p.setMeeting(p.role.night_chat)
                p.vote(VOTE_NONE)
                p.role.get_night_action()
                p.role.get_night_vote()
            v = vote_processor.process_day_vote(votes)
            if len(v) > 0:
                [ve.callback(v.visitor, v.visited) for ve in v] # do the lynch + extra
            for p in self.players:
                p.evars = []
                
        elif (time % 2 == 1): # moving to day time
            self.visits = []
            voted_chats = []
            for p in self.players: # 1. generate visits
                v = p.get_night_visit()
                self.visits += v
                if p.night_chat == Meeting.none or p.night_chat not in voted_chats:
                    votes = [pl.vote for pl in self.players if pl.chat_number == p.chat_number]
                    v2 = p.process_night_vote(votes)
                    self.visits += v2
                    voted_chats.append(p.night_chat)
            '''
            priority for night visits is this:
            1. Maf RBs 2. Town RBs 3. All role conversions 4. Everything else 5. Votes
            '''
            for v in sorted(self.visits): # 2. do all visits in priority order
                v.callback(v.visitor, v.visited)
            # 3. reset everything, dump them all into town chat
            for p in self.players:
                p.setMeeting(Meeting.day)
                p.vote(VOTE_NONE)
                p.role.get_day_action()
                p.role.get_day_vote()
                p.evars = []

        check_win()
            

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


    # TODO offload win conditions to the role to support 3ps and multiple factions
    def check_win(self):
        alive_players = [p for p in self.players if p.alive]
        winners = []
        checked_alignments = []
        for p in alive_players:
            if (p.alignment not in checked_alignments):
                checked_alignments.append(p.alignment)
                check = p.check_win(alive_players)
                if check is not None:
                    winners.append(check)
        if len(winners) > 0: # someone won the game
            pass # TODO move to postgame chat
