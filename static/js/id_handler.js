$(document).ready(function() {
    var tableElements = [];

    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    socket.on('reconnecting', function reconnectCallback(tries) {
        console.log('reconnecting');
        alert("Lost connection to the server, reconnecting...");
    });

    socket.on('can_messages', function(msg) {
        console.log("Received can_id");

        if(msg.timeout === 'false') {

            if($("#"+msg.id).parent().hasClass("bg-danger")) {
                $("#"+msg.id).parent().removeClass("bg-danger")
            }
            var table = document.getElementById("can_messages");
            //create a dynamic table that adds new keys and updates old values
            var value = "0".repeat(16 - msg.value.length) + msg.value
            value = value.replace(/(.{2})/g, '$1 ').toUpperCase();

            if(!(tableElements.includes(msg.id))) {
                var row = table.insertRow(-1);
                var cell1 = row.insertCell(0);
                cell1.innerHTML = msg.id;
                var cell2 = row.insertCell(1);
                cell2.id = msg.id;
                cell2.innerHTML = value;
                tableElements.push(msg.id);
            } else {
                var tempCell = document.getElementById(msg.id);
                tempCell.innerHTML = value;
            }
        } else {
            //show user that a timeout happened
            $("#"+msg.id).parent().addClass("bg-danger");
        }
    });
});