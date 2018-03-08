from twisted.python import log
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketServerProtocol
from autobahn.twisted.websocket import WebSocketServerFactory


rooms = {}

# MafiaProtocol is the client object
# has a .sendMessage(str) function
class MafiaPlayer(WebSocketServerProtocol):
    def __init__(self): # new player
        self.name = "--"
        self.room = None
        self.role = None
        self.chat_number = -1
        self.player_number = -1
        self.alive = True
        self.vote = -2
        
    def onMessage(self, payload, isBinary):
        if (isBinary):
            payload = payload.encode()
        print(payload)
        
        tokens = payload.split(" ")
        command = tokens[0]
        rest = ' '.join(payload.split(" ")[1:])
        
        if (command == "JOIN"): # join room (game)
            try:
                room_number = int(tokens[1])
                if room_number in rooms:
                    self.room = rooms[room_number]
                    res = self.room.add_player(self)
                    if (res) sendMessage("JOIN " + self.name)
                    else self.sendMessage("ERROR")
            except: # not a number, no number, etc
                self.sendMessage("ERROR")

        elif (command == "NAME"): # set name
            try:
                self.name = tokens[1]
                self.player_number = int(tokens[2])
            except:
                pass

        elif not(self.room is None): # let the room handle this message
            self.room.command(self, command, rest)
        else: # no room
            sendMessage("ERROR")
        
    def vote(self, vote_n):
        if (vote_n == self.vote): # unvote
            self.vote = -2
            self.ready = False
        else:
            self.vote = vote_n
            self.ready = True

    def ready(self): # check if voted and actions are done
        return self.ready and self.role.ready

    def onOpen(self):
        self.room = None
        print("Client connected")


    def onClose(self, wasClean, code, reason):
        print("Client disconnected")

if __name__ == '__main__':
    factory = WebSocketServerFactory("ws://127.0.0.1:9001",debug=True)
    factory.protocol = MafiaPlayer
    reactor.listenTCP(9001,factory)
    reactor.run()
