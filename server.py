from twisted.python import log
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketServerProtocol
from autobahn.twisted.websocket import WebSocketServerFactory
from roles.visit import Visit
from roles.role import Role
from roles.mafia import Mafia
from roles.cop import Cop
from roles.doctor import Doctor
from roles.enums import *
from room import MafiaRoom
rooms = {}

# MafiaProtocol is the client object
# has a .sendMessage(str) function
class MafiaPlayer(WebSocketServerProtocol):
    def __init__(self): # new player
        self.name = "--"
        self.dname = "--"
        self.room = None
        self.role = None
        self.chat_number = Meeting.pregame
        self.player_number = -1
        self.alive = True
        self.vote = VOTE_NL
        self.evars = []
        self.host = False
        self.ready = False
        
    def onMessage(self, payload, isBinary):
        if (isBinary):
            payload = payload.encode()
        print(str(self.player_number) + " " + payload)
        
        tokens = payload.split(" ")
        command = tokens[0]
        rest = ' '.join(payload.split(" ")[1:])
        
        if (command == "JOIN"): # join room (game)
            try:
                room_number = int(tokens[1])
                if room_number in rooms:
                    self.room = rooms[room_number]
                    res = self.room.add_player(self)
                    if (res):
                        self.sendMessage("JOINED")
                    else:
                        self.sendMessage("ERROR")
                else: # TODO send command to redirect to index?
                    pass
            except: # not a number, no number, etc
                self.sendMessage("ERROR")

        elif (command == "NAME"): # set name
            try:
                self.name = tokens[1]
                # self.player_number = int(tokens[2])
            except:
                pass

        elif not(self.room is None): # let the room handle this message
            self.room.command(self, command, rest)
        else: # no room
            self.sendMessage("ERROR")
        
    def voteFor(self, vote_n, announce):
        if vote_n == VOTE_NONE: # unvote
            self.vote = VOTE_NONE
            self.ready = False
        else:
            self.vote = vote_n
            self.ready = True
        self.room.vote(self.player_number, self.chat_number, vote_n, announce)

    def kill(self):
        if not(self.alive):
            return
        if "save" not in self.evars:
            self.alive = False
            for player in self.room.players.values():
                player.sys(self.dname + ", the " + self.role.name + ", is dead.")
                player.sendMessage("DEAD " + str(self.player_number))

    def setMeeting(self, meet_n):
        self.chat_number = meet_n
        self.vote = VOTE_NONE
        self.sendMessage("CHAT " + str(meet_n))

    def sys(self, msg):
        self.sendMessage("SYS " + msg)

    def isReady(self): # check if voted and actions are done
        r = (self.ready) and (self.role.ready)
        return r

    def onOpen(self):
        self.room = None
        print("Client connected")


    def onClose(self, wasClean, code, reason):
        if self.room is not None:
            self.room.del_player(self)
        print("Client disconnected")

if __name__ == '__main__':
    # DEBUG create room
    # TODO how do you create a room from the website (ws connect to this server and use a MAKEROOM command?
    rooms[0] = MafiaRoom([Role(), Role(), Role(), Doctor(), Cop(), Mafia(), Mafia()], "dkc.txt")


    
    factory = WebSocketServerFactory("ws://127.0.0.1:9001",debug=True)
    factory.protocol = MafiaPlayer
    reactor.listenTCP(9001,factory)
    reactor.run()
