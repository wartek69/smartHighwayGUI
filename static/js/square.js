$(document).ready(function() {
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    socket.on('reconnecting', function reconnectCallback(tries) {
        console.log('reconnecting');
        alert("Lost connection to the server, reconnecting...");
    });

    socket.on('extern', function(msg) {
        console.log("Received extern event with type: "+msg.type);
        $("#extern").removeClass("bg-danger bg-success bg-yellow")

        if(msg.timeout === 'true') {
            $("#extern").addClass("bg-success");
        } else if(msg.type === 'UNKNOWN') {
            $("#extern").addClass("bg-yellow");
        } else {
            $("#extern").addClass("bg-danger");
        }

    });

    socket.on('intern', function(msg) {
        console.log("Received extern event");
        if(msg.type != undefined) {
            $("#intern").removeClass("bg-danger bg-success bg-yellow")

            if(msg.type === 'OK') {
                $("#intern").addClass("bg-success");
            } else if(msg.type === 'UNKNOWN') {
                $("#intern").addClass("bg-yellow");
            } else {
                $("#intern").addClass("bg-danger");
            }
        }

    });
});