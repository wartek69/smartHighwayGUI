$(document).ready(function() {
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    //receive details from server
    socket.on('newgps', function(msg) {
        console.log("Received gps latitude" + msg.gps_lat);
        info_string = '<p>Gps latitude: ' + msg.gps_lat.toString() + '</p>';
        info_string = info_string + '<p>Gps longitude: ' + msg.gps_lon.toString() + '</p>'
        info_string = info_string + '<p>Car speed: ' + msg.speed.toString() + '</p>'


        $('#log').html(info_string);
    });
});

