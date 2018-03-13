import random
from roles.enums import *
class MafiaRoom:
    players = []
    setup = None
    time = -1
    visits = []
    pcounter = 0
    ingame = False
    
    def __init__(self, setup):
        self.players = [] # MafiaPlayer objects
        self.setup = setup

    # add player to room
    def add_player(self, new_player):
        if (self.time >= 0): # game already started
            return False
        self.players.append(new_player)
        new_player.player_number = self.pcounter
        self.pcounter += 1
        if len(self.players) == 1:
            new_player.host = True
            new_player.sendMessage("HOST")
        for player in self.players:
            player.sendMessage("JOIN " + new_player.name + " " + str(new_player.player_number))
            if player is not new_player:
                new_player.sendMessage("JOIN " + player.name + " " + str(player.player_number))
        return True

    # remove player from room (quit)
    def del_player(self, old_player):
        # game hasn't started yet, just remove player from room
        if (self.time == -1):
            self.players.remove(old_player)
            for player in self.players:
                player.sendMessage("QUIT " + str(old_player.player_number))
            if old_player.host and len(self.players) > 0:
                self.players[0].host = True
                self.players[0].sendMessage("HOST")
        else: # game has started - kill player instead
            old_player.kill()


    def command(self, sender, command, params):
        if (command == "READY" and not self.ingame):
            sender.ready = True
            self.check_advance_time()
        elif (command == "MSG"):
            self.msg(sender.player_number, params, sender.chat_number)
        elif (command == "VOTE" and self.ingame):
            sender.voteFor(int(params), True)
            self.check_advance_time()
        elif (command == "ACTION" and self.ingame):
            sender.role.action(params)
            self.check_advance_time()
        elif (command == "ADDROLE" and not self.ingame):
            if (sender.host and self.time == -1):
                self.add_role(params)
        elif (command == "DELROLE" and not self.ingame):
            if (sender.host and self.time == -1):
                self.del_role(params)
        elif (command == "STARTGAME" and not self.ingame):
            if (sender.host and self.time == -1 and len(self.players) == len(self.setup)):
                self.advance_time()
                
    def gen_vote_list(self, vt):
        if (vt == "all"):
            return "VLIST " + " ".join([str(p.player_number) for p in self.players if p.alive])
        elif (vt == "not mafia"):
            return "VLIST " + " ".join([str(p.player_number) for p in self.players if p.alive and not(p.role.alignment == Alignment.mafia)])
        else:
            return [] # cult stuff, masons, etc can go here
        

    def check_advance_time(self):
        advance_day = True
        for player in self.players:
            if not(player.isReady()):
                advance_day = False
        if (advance_day):
            self.advance_time()


    def advance_time(self): # entire game cycle basically
        self.time += 1
        if (self.time == 0): # setup the entire game # TODO I'm probably forgetting something
            self.ingame = True
            random.shuffle(self.setup)
            for i in range(len(self.players)): # randomly assign roles
                self.players[i].role = self.setup[i]
                self.setup[i].player = self.players[i]
                self.setup[i].room = self
                self.players[i].sys("You are the " + self.setup[i].name + ".")
        if (self.time % 2 == 0): # moving to night time
            votes = [p.vote for p in self.players]
            vote_processor = self.players[0]
            for p in self.players:
                if (p.role.day_vote_priority > vote_processor.role.day_vote_priority):
                    vote_processor = p
                p.setMeeting(p.role.night_chat)
                p.voteFor(VOTE_NONE, False)
                p.role.get_night_action()
                p.role.get_night_vote()
            v = vote_processor.role.process_day_vote(votes)
            if len(v) > 0:
                [ve.callback(v.visitor, v.visited) for ve in v] # do the lynch + extra
            for p in self.players:
                p.evars = []
                
        elif (self.time % 2 == 1): # moving to day time
            self.visits = []
            voted_chats = []
            for p in self.players: # 1. generate visits
                v = p.role.get_night_visit()
                self.visits += v
                if not(p.role.night_chat == Meeting.none) and p.role.night_chat not in voted_chats:
                    votes = [pl.vote for pl in self.players if pl.chat_number == p.chat_number]
                    v2 = p.role.process_night_vote(votes)
                    self.visits += v2
                    voted_chats.append(p.role.night_chat)
            '''
            priority for night visits is this:
            1. Maf RBs 2. Town RBs 3. All role conversions 4. Everything else 5. Votes
            '''
            for v in sorted(self.visits): # 2. do all visits in priority order
                v.callback(v.visitor, v.visited)
            # 3. reset everything, dump them all into town chat
            for p in self.players:
                p.setMeeting(Meeting.day)
                p.voteFor(VOTE_NONE, False)
                p.role.get_day_action()
                p.role.get_day_vote()
                p.evars = []

        self.check_win()
            

    # send message to other people in this chat (day, maf night, town night, etc)
    def msg(self, s_n, message, chat_number):
        if chat_number == Meeting.none: # not in a meeting, no chat
            return
        elif not(self.ingame): # everyone chats in pregame/postgame
            for player in self.players:
                player.sendMessage("MSG " + str(s_n) + " " + message)
        elif self.players[s_n].alive: # alive chat
            for player in [p for p in self.players if p.chat_number == chat_number or not p.alive]:
                player.sendMessage("MSG " + str(s_n) + " " + message)
        else: # dead chat
            for player in [p for p in self.players if not p.alive]:
                player.sendMessage("MSG " + str(s_n) + " " + message)
                
    def vote(self, voter_n, chat_n, target_n, announce):
        if chat_n == -1 or not(self.ingame):
            return
        elif announce:
            for player in [p for p in self.players if p.chat_number == chat_n or not p.alive]:
                player.sendMessage("VOTE " + str(voter_n) + " " + str(target_n))


    # TODO offload win conditions to the role to support 3ps and multiple factions
    def check_win(self):
        alive_players = [p for p in self.players if p.alive]
        winners = []
        checked_alignments = []
        for p in alive_players:
            if (p.role.alignment not in checked_alignments):
                checked_alignments.append(p.role.alignment)
                check = p.role.check_win(alive_players)
                if check is not None:
                    winners.append(check)
        if len(winners) > 0: # someone won the game
            win_str = ", ".join(winners) + " win!"
            for p in self.players:
                p.setMeeting(Meeting.postgame)
                p.alive = True
                ingame = False
                p.sys(win_str)


    # TODO come up with a way that's actually scalable
    def add_role(self, name):
        if (name == "Villager"):
            self.setup.append(Role())
        elif (name == "Mafia"):
            self.setup.append(Mafia())
        elif (name == "Doctor"):
            self.setup.append(Doctor())
        elif (name == "Cop"):
            self.setup.append(Cop())


    def del_role(self, name):
        d = -1
        for x in range(len(self.setup)):
            if self.setup[x].name == name:
                d = x
                break
        if not(d == -1):
            self.setup.pop(x)
