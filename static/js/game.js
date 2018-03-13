$(function () {
    var socket = new WebSocket("ws://mafia.tapioca.world/ws");
    var name = readCookie("name");
    var names = {}
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
	socket.send("MSG " + message);

	
	// DEBUG COMMANDS
	if (message == "/START") socket.send("STARTGAME");
	else if (message.startsWith("/VOTE"))
	    for (var k in names)
		if (names.hasOwnProperty(k) && message.split(" ")[1] == names[k])
		    socket.send("VOTE " + k);
	
	$('#m').val('');
	return false;
    });
    
    
    function onMessage(mesg) {
	var msg = mesg.data;
	console.log(msg);
	// unimplemented: VLIST, HOST, QUIT
	var tokens = msg.split(' ');
	if (tokens[0] == "MSG") {
	    var sc = 0, i = 0;
	    while (sc < 2) if (msg.charAt(i++) == ' ') sc++;
	    chatMessage(parseInt(tokens[1]), msg.substring(i));
	}
	else if (tokens[0] == "SYS") {
	    var sc = 0, i = 0;
	    while (sc == 0) if (msg.charAt(i++) == ' ') sc++;
	    sysMessage(msg.substring(i));
	}
	else if (tokens[0] == "VOTE") {
	    var voterN = parseInt(tokens[1]);
	    var votedN = parseInt(tokens[2]);
	    var voter = names[voterN];
	    if (votedN != -2) {
		var voted = names[parseInt(tokens[2])];
		sysMessage(voter + " votes for " + voted);
	    }
	    else {
		sysMessage(voter + " unvotes");
	    }
	}
	else if (tokens[0] == "CHAT") {
	    //$('#messages').html(""); // TODO lol
	    $('#messages').append('<li class="sys">________________________</li>');
	}
	else if (tokens[0] == "JOIN") {
	    names[parseInt(tokens[2])] = tokens[1];
	    refreshPlayerList();
	}
	else if (tokens[0] == "QUIT") {
	    delete names[parseInt(tokens[1])];
	    refreshPlayerList();
	}
    }

    function refreshPlayerList() {
	$('#playerBox').html("");
	for (var n in names) {
	    if (names.hasOwnProperty(n)) {
		$('#playerBox').append("<li>" + names[n] + "</li>");
	    }
	}
    }
    
    function onClose() { /* TODO */ }
    function chatMessage(n, msg) {
	var name = names[n];
	$('#messages').append('<li><b>'+name+':</b> '+msg+'</li>');
	var objDiv = document.getElementById("messagediv");
	objDiv.scrollTop = objDiv.scrollHeight;
    }
    
    function sysMessage(msg) {
	$('#messages').append('<li class="sys">'+msg+"</li>");
	var objDiv = document.getElementById("messagediv");
	objDiv.scrollTop = objDiv.scrollHeight;			    
    }
    
});
