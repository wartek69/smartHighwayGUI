$(document).ready(function() {
     var marker = undefined;
     var carIcon = L.icon({
        iconUrl: 'car.png',
        shadowUrl: 'car.png',

        iconSize:     [100, 100], // size of the icon
        shadowSize:   [50, 64], // size of the shadow
        iconAnchor:   [22, 94], // point of the icon which will correspond to marker's location
        shadowAnchor: [4, 62],  // the same for the shadow
        popupAnchor:  [-3, -76] // point from which the popup should open relative to the iconAnchor
    });

    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    //receive details from server
    socket.on('newgps', function(msg) {
        console.log("Received gps latitude" + msg.gps_lat);
        info_string = '<p>Gps latitude: ' + msg.gps_lat.toString() + '</p>';
        info_string = info_string + '<p>Gps longitude: ' + msg.gps_lon.toString() + '</p>'
        info_string = info_string + '<p>Car speed: ' + msg.speed.toString() + '</p>'
        $('#log').html(info_string);

        if (marker != undefined) {
              map.removeLayer(marker);
        };
        marker = L.marker([msg.gps_lat, msg.gps_lon]).addTo(map);

    });

    var map = L.map('mapid').setView([51.22, 4.40], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

});