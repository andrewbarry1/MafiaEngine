var app = require('express')();
var http = require('http').Server(app);
var io = require('socket.io')(http);
var cookieParser = require('cookie-parser');
var cookie = require('cookie');
app.use(cookieParser());

app.get('/', function(req, res){
    if(hasAuthCookie(req)) {
        res.sendFile(__dirname + '/index.html');
    }
    else res.redirect('/authorize.html');
});

app.get('/game', function(req, res){
    if(hasAuthCookie(req)) {
        res.sendFile(__dirname + '/game.html');
    }
    else res.redirect('/authorize.html');
});

app.get('/authorize.html', function(req, res){
    res.sendFile(__dirname + '/authorize.html');
});

app.get('/common.js', function(req, res){
    res.sendFile(__dirname + '/common.js');
});

app.get('/chat.css', function(req, res){
    res.sendFile(__dirname + '/chat.css');
});

function hasAuthCookie(req) {
    var username = req.cookies["name"];
    return username !== undefined;
}

var globalLobbyCount = 0;
//game ids -> players
var gamesTable = {};
//players -> Game objects
var playersTable = {};
//gameIds -> Game objects
var games = {};
var currentLobby = null;

function removeA(arr) {
    var what, a = arguments, L = a.length, ax;
    while (L > 1 && arr.length) {
        what = a[--L];
        while ((ax= arr.indexOf(what)) !== -1) {
            arr.splice(ax, 1);
        }
    }
    return arr;
}

function Lobby(id) {
    //this.roomId = id;
    this.channel = "lobby" + id + "-" + new Date().toUTCString();
    this.players = new Array();
    this.closed = false;
    this.host = null;
    
    Lobby.lobbies[this.channel] = this;
    
    this.getLobbyChannel = function () {
        return this.channel;
    };
    
    var updateHost = function(dumb) {
        io.to(dumb.channel).emit("host", dumb.host);
    };
    
    this.addPlayer = function (name, socket) {
        //let others in lobby know that this player joined (including the joiner)
        io.to(this.channel).emit("join", name);
        //now tell the joiner who all is in the game
        this.players.forEach(function(p) {
            io.to(socket.id).emit("join", p);
        });
        this.players.push(name);
        if(this.host === null) {
            this.host = name;
        }
        updateHost(this);
    };
    
    this.removePlayer = function (name) {
        this.players = removeA(this.players, name);
        io.to(this.channel).emit("leave", name);
        if(name === this.host) { //if player was host, pick another host
            if(this.players.length === 0) this.host = null;
            else this.host = this.players[0];
            updateHost(this);
        }
    };
}
Lobby.lobbies = {};

function Game(lobby) {
    this.channel = lobby.channel;
    this.players = {};
    Game.omniscientString = "omniscient-P1z4CrB3A5R9NGrYD9Wi";
    
    this.addPlayer = function (playerid) {
        this.players[playerid] = new Array(); //event cache
        if(playerid !== Game.omniscientString)
            playersTable[playerid] = this;
    };
    
    this.addPlayer(Game.omniscientString);
    lobby.players.forEach(this.addPlayer, this);
    
    this.addPayload = function (playerid, payloadArray) {
        this.players[playerid] = this.players[playerid].concat(payloadArray);
    };
    
    this.addToOmniscient = function (payloadArray) {
        this.addPayload(Game.omniscientString, payloadArray);
    };
    
    this.addToAllPlayers = function (payloadArray) {
        Object.keys(this.players).forEach(function(key) {
            this.addPayload(key, payloadArray);
        }, this);
    };
}

var engineSocket = null;
//This is a secret cookie that only the engine will know
var engineSecret = 'zy9nkf224UQYveoO5cc4VgsRHztI8uXIVLF9HLn8';

io.on('connection', function(socket){
    //check whether player was in a game. If they were, resend list of events
    //else put them in the lobby
    if(socket.handshake.headers.cookie === undefined) {
        console.log("WARN: Socket.IO connection from cookie-less client from " 
                + socket.handshake.addresss);
        return;
    }
    var cookies = cookie.parse(socket.handshake.headers.cookie);
    if(cookies.enginesecret !== undefined) {
        //code reserved for engine interaction only
        var ip = socket.handshake.address;
        if(cookies.enginesecret !== engineSecret) {
            console.log("WARN: Client claiming engine with wrong secret from " + ip);
            socket.disconnect(true);
            return;
        }
        if(engineSocket !== null) {
            if(engineSocket.connected === true) {
                console.log("WARN: Engine trying to connect from " + ip + 
                        " when engine connection still alive.");
                socket.disconnect(true);
                return;
            }
        }
        console.log("Engine connected from " + ip);
        engineSocket = socket;
        socket.on('update', function(results, channel) {
            //console.log(results);
            var game = games[channel];
            results.forEach((r) => {
                var payloads = r["js_payloads"];
                game.addToOmniscient(payloads);
                if(r.is_broadcast) {
                    game.addToAllPlayers(payloads);
                    io.to(channel).emit('ui', payloads);
                }
                else {
                    //use player id not socket id in case of reconnects
                    r.receivers.forEach((playerid) => {
                        game.addPayload(playerid, payloads);
                        io.to(channel).emit(playerid, payloads);
                    });
                }
            });
        });
        return;
    }
    var name = cookies.name;
    var game = playersTable[name];
    var lobby;
    if(game === undefined) { //go to lobby
        if(currentLobby === null) { //create a new lobby
            currentLobby = new Lobby(globalLobbyCount++);
        }
        socket.join(currentLobby.getLobbyChannel());
        currentLobby.addPlayer(name, socket);
        lobby = currentLobby;
    }
    else { // go back to game
        socket.join(game.channel);
        io.to(game.channel).emit(name, game.players[name]);
    }
    
    socket.on('disconnect', function(){
        //only remove player from the channel if game hasn't started yet
        if(game === undefined)
            lobby.removePlayer(name);
    });
    socket.on('close lobby', function(){
        var lobby = currentLobby;
        if(!(lobby.getLobbyChannel() in socket.rooms))
            return; //protect against fast clickers. Don't clear currentLobby if client's lobby is already closed
        currentLobby = null;
        lobby.closed = true;
        io.to(lobby.getLobbyChannel()).emit('confirm closed');
    });
    socket.on('setup update', function(inputs) {
        io.to(lobby.getLobbyChannel()).emit('setup update', inputs);
    });

    socket.on('msg', function(msg) {
        var playerChannel = playersTable[name].channel;
        io.to(engineSocket.id).emit('engine', playerChannel, name, msg);
    });
socket.on('chat', function(msg){
    io.to(lobby.getLobbyChannel()).emit('chat', msg);
  });
socket.on('request game', function(setup) {
    if(!lobby.closed) {
        io.to(socket.id).emit('control', "alert('Lobby must be closed first');");
        return;
    }
    io.to(lobby.channel).emit('game start');
    gamesTable[lobby.channel] = new Array();
    games[lobby.channel] = new Game(lobby);
    setup.channel = lobby.channel;
    io.to(engineSocket.id).emit('startgame', setup);
  });
});
http.listen(3000, function(){
  console.log('listening on *:3000');
});
