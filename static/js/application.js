$(document).ready(function() {
     var gps_marker = undefined;
     var eebl_marker = undefined;
     var tableElements = [];
     var zoom = 17;
     var firstMsg = true;
     var stopicontimeout = 5000;

     //icon names are from the font awesome website!
     var carIcon = L.AwesomeMarkers.icon({
         prefix: 'fa',
         extraClasses: 'fas',
         iconColor: 'green',
         icon: 'car-side'
     });

     var stopIcon = L.AwesomeMarkers.icon({
         prefix: 'fa',
         extraClasses: 'fas',
         iconColor: 'red',
         icon: 'ban'
     });

     //example on how to load in an icon locally, not used
     var greenIcon = L.icon({
         iconUrl: 'static/leaf-orange.png',
         shadowUrl: 'static/leaf-shadow.png',
         iconSize:     [38, 95], // size of the icon
         shadowSize:   [50, 64], // size of the shadow
         iconAnchor:   [22, 94], // point of the icon which will correspond to marker's location
         shadowAnchor: [4, 62],  // the same for the shadow
         popupAnchor:  [-3, -76] // point from which the popup should open relative to the iconAnchor
     });


    //Init map
    var map = L.map('mapid').setView([0, 0], zoom);

    /* Another set of tiles -> didn't use them because of lag in rendering
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);*/

    L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox.streets',
    accessToken: 'pk.eyJ1Ijoid2FydGVrIiwiYSI6ImNqcnVkdHo4NzB1MTA0OW44eG5kYzNyaDAifQ.nzK-P-BOrc2aw_C4lmidTA'
    }).addTo(map);

    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port);

    socket.on('reconnecting', function reconnectCallback(tries) {
        console.log('reconnecting');
        alert("Lost connection to the server, reconnecting...");
    });
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

            gps_marker = L.marker([msg.gps_lat, msg.gps_lon], {icon: carIcon}).addTo(map);
            //only center the map on first gps message
            if(firstMsg) {
                map.flyTo([msg.gps_lat, msg.gps_lon], zoom);
                // uncomment to change the map center without animation
                // map.panTo([msg.gps_lat, msg.gps_lon]);
                firstMsg = false;
            }

        } else {
            info_string ="Location: NaN"
            firstMsg = true;
        }
        $('#log').html(info_string);
    });

    socket.on('eebl_extern', function(msg) {
        console.log("Received eebl_extern");
        if (msg.timeout === "false") {
            info_string = '<p>eebl_lat: ' + msg.eebl_lat.toString() + '</p>';
            info_string = info_string + '<p>eebl_longitude: ' + msg.eebl_lon.toString() + '</p>'
            info_string = info_string + '<p>eebl_speed: ' + msg.speed.toString() + '</p>'
            var eebl_markerr = L.marker([msg.eebl_lat, msg.eebl_lon], {icon: stopIcon}).addTo(map)
                .bindPopup('\nlon: ' + msg.eebl_lon + ' \nlat: ' + msg.eebl_lon + '\nspeed: ' + msg.speed );
            setTimeout(function() {
                map.removeLayer(eebl_markerr);
            }, stopicontimeout);
        } else {
            info_string = '<p>eebl_lat: NaN</p>\n' +
                ' <p>eebl_longitude: NaN</p>\n' +
                ' <p>eebl_speed: NaN</p>'
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

        if(msg.timeout === 'false') {

            if($("table").hasClass("bg-danger")) {
                $("table").removeClass("bg-danger")
            }
            var table = document.getElementById("vehicle_state");
            //create a dynamic table that adds new keys and updates old values
            if(!(tableElements.includes(msg.type))) {
                var row = table.insertRow(0);
                var cell1 = row.insertCell(0);
                cell1.innerHTML = msg.type;
                var cell2 = row.insertCell(1);
                cell2.id = msg.type;
                cell2.innerHTML = msg.value;
                tableElements.push(msg.type);
            } else {
                var tempCell = document.getElementById(msg.type);
                tempCell.innerHTML = msg.value;
            }
        } else {
            //show user that a timeout happened
            $("table").addClass("bg-danger");
        }


    });



});