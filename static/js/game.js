$(function () {
    var socket = new WebSocket("ws://mafia.tapioca.world/ws");
    var name = readCookie("name");
    var players = {}
    var room = parseInt($('#room').text());
    var time = -1;
    var useRealName = true;
    var id_order = []
    
    socket.onopen = announceSelf;
    socket.onmessage = onMessage;
    socket.onclose= onClose;
    
    function announceSelf() {
	
	socket.send("NAME " + name); // TODO technically a race condition
	socket.send("JOIN " + room);
    }
    
    $('form').submit(function(){
        var message = $('#m').val().trim();
        if(message.length === 0) return false; //don't send empty messages
	$('#m').val('');
	
	// DEBUG COMMANDS
	if (message == "/START") {
	    socket.send("STARTGAME");
	}
	else if (message.startsWith("/VOTENL")) {
	    socket.send("VOTE -1");
	}
	else if (message.startsWith("/UNVOTE")) {
	    socket.send("VOTE -2");
	}
	else if (message.startsWith("/VOTE")) {
	    for (var k in players)
		if (players.hasOwnProperty(k) && message.split(" ")[1] == players[k].name)
		    socket.send("VOTE " + k);
	}
	else {
	    socket.send("MSG " + message);
	}
	return false;
    });
    
    
    function onMessage(mesg) {
	var msg = mesg.data;
	console.log(msg);
	var tokens = msg.split(' ');
	if (tokens[0] == "MSG") {
	    var sc = 0, i = 0;
	    while (sc < 2) if (msg.charAt(i++) == ' ') sc++;
	    chatMessage(parseInt(tokens[1]), msg.substring(i));
	}
	else if (tokens[0] == "DEADMSG") {
	    var sc = 0, i = 0;
	    while (sc < 2) if (msg.charAt(i++) == ' ') sc++;
	    deadChatMessage(parseInt(tokens[1]), msg.substring(i));
	}
	else if (tokens[0] == "SYS") {
	    var sc = 0, i = 0;
	    while (sc == 0) if (msg.charAt(i++) == ' ') sc++;
	    sysMessage(msg.substring(i));
	}
	else if (tokens[0] == "VOTE") {
	    var voterN = parseInt(tokens[1]);
	    var votedN = parseInt(tokens[2]);
	    var voter = players[voterN].dname;
	    if (votedN == -2) {
		sysMessage(voter + " unvotes");
		players[voterN].vote = "";
	    }
	    else if (votedN == -1) {
		sysMessage(voter + " votes for no one.");
		players[voterN].vote = "no one";
	    }
	    else {
		var voted = players[parseInt(tokens[2])].dname;
		players[voterN].vote = voted;
		sysMessage(voter + " votes for " + voted);
	    }
	    refreshPlayerList();
	    
	}
	else if (tokens[0] == "VLIST") { // TODO alphabetize vote list
	    if (tokens.length == 1) return; // Nothing to vote for, do not make select
	    var options = tokens[1].split(',');
	    var h_str = "<select id='vote'>";
	    for (var x = 0; x < options.length; x++) {
		var o = parseInt(options[x]);
		for (var p in players) {
		    if (players.hasOwnProperty(p) && o == p) {
			h_str += "<option value='" + p + "'>" + players[p].dname + "</option>";
		    }
		}
	    }
	    h_str += "<option value='-1'>No one</option>"
	    h_str += "<option value='-2'> </option>"
	    h_str += "</select>"
	    $('#voteSection').html(h_str);
	    $('#vote').val("-2");
	    $('#vote').change(function() {
		$('#vote option:selected').each(function() {
		    var voting = $(this).val();
		    socket.send("VOTE " + voting);
		});
	    });
	}
	else if (tokens[0] == "CHAT") {
	    //$('#messages').html(""); // TODO tabbed pages for logs?
	    $('#voteSection').html("");
	    for (var n in players) {
		if (players.hasOwnProperty(n)) {
		    players[n].vote = "";
		}
	    }
	    time += 1;
	    var timestr = "";
	    if (time % 2 == 0) timestr = "Night ";
	    else timestr = "Day ";
	    timestr += (Math.floor(time / 2) + 1);
	    $('#messages').append('<li class="sys">_____________________' + timestr + '____________________</li>');
	    useRealName = false; // use deck names during the game
	    refreshPlayerList();
	}
	else if (tokens[0] == "DEAD") {
	    players[parseInt(tokens[1])].alive = false;
	    if (name == players[parseInt(tokens[1])].name) { // it was you
		$('#voteSection').html("");
	    }
	    refreshPlayerList();
	}
	else if (tokens[0] == "NAME") { // rename player.
	    players[parseInt(tokens[1])].dname = tokens[2];
	    useRealName = false;
	    shufflePlayers();
	    refreshPlayerList();
	}
	else if (tokens[0] == "REVEAL") {
	    useRealName = true;
	    refreshPlayerList();
	}
	else if (tokens[0] == "JOIN") {
	    var pn = parseInt(tokens[2]);
	    players[pn] = {name:tokens[1], dname:tokens[1], vote:"", alive:true, id:pn};
	    id_order.push(pn);
	    refreshPlayerList();
	}
	else if (tokens[0] == "HOST") {
	    sysMessage("You are now the host.");
	    $('#voteSection').html("<button id='startButton'>Start Game</button>");
	    $('#startButton').click(function() {
		socket.send("STARTGAME");
	    });
	}
	else if (tokens[0] == "QUIT") {
	    var pn = parseInt(tokens[1]);
	    delete players[pn];
	    id_order.splice(id_order.indexOf(pn), 1);
	    refreshPlayerList();
	}
    }

    function shufflePlayers() {
	for (let i = id_order.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [id_order[i], id_order[j]] = [id_order[j], id_order[i]];
	}
    }

    function refreshPlayerList() {
	$('#playerBox').html("");
	console.log("REFRESHING")
	for (var x = 0; x < id_order.length; x++) {
	    var n = id_order[x];
	    var votestr = "";
	    var cstr = "";
	    if (players[n].vote != "") {
		votestr = " votes " + players[n].vote;
	    }
	    if (!players[n].alive) {
		cstr = " class='dead'";
	    }
	    var namestr = players[n].dname;
	    if (useRealName && players[n].name == players[n].dname) {
		namestr = players[n].name;
	    }
	    else if (useRealName) {
		namestr = players[n].dname + "(" + players[n].name + ")";
	    }

	    var build = namestr + votestr;
	    if (players[n].name == name) {
		build = "<u>" + build + "</u>";
	    }
	    $('#playerBox').append("<li" + cstr + ">" + build + "</li>");
	}
    }
    
    function onClose() {
	sysMessage("Connection to server lost. :(");
    }

    // TODO roll these into once function
    function chatMessage(n, msg) {
	var name = players[n].dname;
	if (useRealName) {
	    name = players[n].name;
	}
	$('#messages').append('<li><b>'+name+':</b> '+msg+'</li>');
	var objDiv = document.getElementById("messagediv");
	objDiv.scrollTop = objDiv.scrollHeight;
    }

    function deadChatMessage(n, msg) {
	var name = players[n].dname;
	$('#messages').append('<li class="dead"><b>'+name+':</b> '+msg+'</li>');
	var objDiv = document.getElementById("messagediv");
	objDiv.scrollTop = objDiv.scrollHeight;
    }
    
    function sysMessage(msg) {
	$('#messages').append('<li class="sys">'+msg+"</li>");
	var objDiv = document.getElementById("messagediv");
	objDiv.scrollTop = objDiv.scrollHeight;			    
    }
    
});
