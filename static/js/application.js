$(document).ready(function() {
     var gps_marker = undefined;
     var eebl_marker = undefined;

     //TODO fix the use of own icons
     var carIcon = L.AwesomeMarkers.icon({
        icon: 'fa-car-side'
     });

    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port);

    //receive details from server
    socket.on('newgps', function(msg) {
        //first remove the marker
        if (gps_marker != undefined) {
              map.removeLayer(gps_marker);
        };

        if(msg.timeout === "false") {
            console.log("Received gps coordinates");
            info_string = '<p>Gps latitude: ' + msg.gps_lat.toString() + '</p>';
            info_string = info_string + '<p>Gps longitude: ' + msg.gps_lon.toString() + '</p>'
            info_string = info_string + '<p>Car speed: ' + msg.speed.toString() + '</p>'

        gps_marker = L.marker([msg.gps_lat, msg.gps_lon]).addTo(map);
        } else {
            info_string ="Location: NaN"
        }
        $('#log').html(info_string);
    });

    socket.on('eebl_extern', function(msg) {
        console.log("Received eebl_extern");
        //first remove the marker
        if (eebl_marker != undefined) {
                  map.removeLayer(eebl_marker);
        };

        if (msg.timeout === "false") {
            info_string = '<p>eebl_lat: ' + msg.eebl_lat.toString() + '</p>';
            info_string = info_string + '<p>eebl_longitude: ' + msg.eebl_lon.toString() + '</p>'
            info_string = info_string + '<p>eebl_speed: ' + msg.speed.toString() + '</p>'
            eebl_marker = L.marker([msg.eebl_lat, msg.eebl_lon]).addTo(map);
        } else {
            info_string = 'Extern: NaN'
        }
        $('#eeblextern').html(info_string);
    });

     socket.on('eebl_intern_det', function(msg) {
        console.log("Received eebl_intern_det");
        info_string = '<p>eebl_lat: ' + msg.eebl_lat.toString() + '</p>';
        info_string = info_string + '<p>eebl_longitude: ' + msg.eebl_lon.toString() + '</p>'
        info_string = info_string + '<p>eebl_speed: ' + msg.speed.toString() + '</p>'
        $('#eeblintern').html(info_string);
    });

     socket.on('eebl_intern', function(msg) {
        console.log("Received eebl_intern");
        info_string = '<p>' + msg.info + '</p>';
        $('#eeblintern').html(info_string);
    });

     socket.on('vehicle_state', function(msg) {
        console.log("Received vehicle_state");
        info_string = '<p> Type: ' + msg.type + ' Value: ' + msg.value + '</p>';
        $('#vehicle_state').html(info_string);
    });


    var map = L.map('mapid').setView([51.22, 4.40], 13);
    /*
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);*/
    L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox.streets',
    accessToken: 'pk.eyJ1Ijoid2FydGVrIiwiYSI6ImNqcnVkdHo4NzB1MTA0OW44eG5kYzNyaDAifQ.nzK-P-BOrc2aw_C4lmidTA'
    }).addTo(map);

});