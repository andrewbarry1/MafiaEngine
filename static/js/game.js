$(function () {
    var socket = new WebSocket("ws://mafia.tapioca.world/ws");
    var name = readCookie("name");
    var players = {}
    var room = parseInt($('#room').text());
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
	// unimplemented: HOST
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
	    var voter = players[voterN].name;
	    if (votedN == -2) {
		sysMessage(voter + " unvotes");
		players[voterN].vote = "";
	    }
	    else if (votedN == -1) {
		sysMessage(voter + " votes for no one.");
		players[voterN].vote = "no one";
	    }
	    else {
		var voted = players[parseInt(tokens[2])].name;
		players[voterN].vote = voted;
		sysMessage(voter + " votes for " + voted);
	    }
	    refreshPlayerList();
	    
	}
	else if (tokens[0] == "VLIST") {
	    if (tokens.length == 1) return; // Nothing to vote for, do not make select
	    var options = tokens[1].split(',');
	    var h_str = "<select id='vote'>";
	    for (var x = 0; x < options.length; x++) {
		var o = parseInt(options[x]);
		for (var p in players) {
		    if (players.hasOwnProperty(p) && o == p) {
			h_str += "<option value='" + p + "'>" + players[p].name + "</option>";
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
	    $('#messages').append('<li class="sys">________________________</li>');
	    refreshPlayerList();
	}
	else if (tokens[0] == "DEAD") {
	    players[parseInt(tokens[1])].alive = false;
	    if (name == players[parseInt(tokens[1])].name) { // it was you
		$('#voteSection').html("");
	    }
	    refreshPlayerList();
	}
	else if (tokens[0] == "JOIN") {
	    var pn = parseInt(tokens[2]);
	    players[pn] = {name:tokens[1], vote:"", alive:true};
	    refreshPlayerList();
	}
	else if (tokens[0] == "QUIT") {
	    delete players[parseInt(tokens[1])];
	    refreshPlayerList();
	}
    }

    function refreshPlayerList() {
	$('#playerBox').html("");
	for (var n in players) {
	    if (players.hasOwnProperty(n)) {
		var votestr = "";
		var cstr = "";
		if (players[n].vote != "") {
		    votestr = " votes " + players[n].vote;
		}
		if (!players[n].alive) {
		    cstr = " class='dead'";
		}
		$('#playerBox').append("<li" + cstr + ">" + players[n].name + votestr + "</li>");
	    }
	}
    }
    
    function onClose() { /* TODO */ }

    // TODO roll these into once function
    function chatMessage(n, msg) {
	var name = players[n].name;
	$('#messages').append('<li><b>'+name+':</b> '+msg+'</li>');
	var objDiv = document.getElementById("messagediv");
	objDiv.scrollTop = objDiv.scrollHeight;
    }

    function deadChatMessage(n, msg) {
	var name = players[n].name;
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
