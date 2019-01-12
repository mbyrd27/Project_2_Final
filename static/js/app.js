// TEST
// var URL = "/map"
// d3.json(URL).then(function(response) {
//     for (var i = 0; i < response.length; i++) {
//         var station = response[i]
//         console.log(station.Callsign)
//     }
// })


function createMap(radioStations) {
    var lightmap = L.tileLayer("https://api.mapbox.com/styles/v1/mapbox/light-v9/tiles/256/{z}/{x}/{y}?access_token={accessToken}", {
        attribution: "Map data &copy; <a href=\"http://openstreetmap.org\">OpenStreetMap</a> contributors, <a href=\"http://creativecommons.org/licenses/by-sa/2.0/\">CC-BY-SA</a>, Imagery © <a href=\"http://mapbox.com\">Mapbox</a>",
        maxZoom: 18, 
        id: "mapbox.light", 
        accessToken: API_KEY
    });

    var baseMaps = {
        "Light Map": lightmap
    };

    var overlayMaps = {
        "Radio Stations": radioStations
    };

    var map = L.map("map", {
        center: [40.018554, -96.780999], 
        zoom: 3.8, 
        layers: [lightmap, radioStations]
    });

    L.control.layers(baseMaps, overlayMaps, {collapsed:true}).addTo(map);
}

function dropPoints(response) {
    var radioMarkers = [];
    for (var i=0; i < response.length; i++) {
        var station = response[i]

        var radioMarker = L.marker([station.Lat, station.Lon])
          .bindPopup("<h4>" + station.City + "</h4>" +
          "<hr><p><b>Callsign:</b> " + station.Callsign + "</p>" +
          "<p><b>Median City Age:</b> " + station.MedianAge + "</p>" +
          "<p><b>Top played Artist:</b> " + station.Most_common_artist + "</p>");

        radioMarkers.push(radioMarker);
    }
    createMap(L.layerGroup(radioMarkers));
}

var URL = "/map"
d3.json(URL, dropPoints);