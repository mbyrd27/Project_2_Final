function buildPie(selection) {
    d3.json(`/artists/${selection}`).then(function(data) {
        var newSVG = dimple.newSvg("#pie", 350, 250);
        var chart = new dimple.chart(newSVG, data);
        chart.setBounds(20, 50, "75%", "75%");
        chart.addMeasureAxis("p", "count")
        chart.addSeries(["count", "song"], dimple.plot.pie);
        chart.draw();
    });
}

function buildTime(selection) {
    d3.json(`/times/${selection}`).then(function(timeData) {
        var newSVG = dimple.newSvg("#times", 350, 250);
        var chart = new dimple.chart(newSVG, timeData);
        chart.setBounds(20, 20, "90%", "75%");
        chart.addCategoryAxis("x", "Time");
        chart.addMeasureAxis("y", "Count");
        chart.addSeries(null, dimple.plot.bar);
        chart.addSeries(null, dimple.plot.line);
        chart.draw();
    });
}


var streetmap = L.tileLayer("https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}", {
    attribution: "Map data &copy; <a href='https://www.openstreetmap.org/'>OpenStreetMap</a> contributors, <a href='https://creativecommons.org/licenses/by-sa/2.0/'>CC-BY-SA</a>, Imagery © <a href='https://www.mapbox.com/'>Mapbox</a>",
    maxZoom: 18,
    id: "mapbox.streets",
    accessToken: API_KEY
    });

var myMap = L.map("map", {                       
    center: [40.018554, -96.780999], 
    zoom: 3,
    });

streetmap.addTo(myMap)

var cityMarkers = [];
var cities = L.layerGroup(cityMarkers);

function datashowing(artist, clearit) {       
    d3.json(`/heatmap/${artist}`).then(function(artistdata) {
        
        //myMap.removeLayer(cities);

        if (clearit) {
            cityMarkers = []
            myMap.removeLayer(cities);
        }
        
        for (var i = 0; i < artistdata.length; i++) {
            var heat = artistdata[i].Songcount * 10000;
            //console.log(heat);
            //console.log(artistdata[i].Lat);
            //console.log(artistdata[i].Lon);
            cityMarkers.push(
            L.circle([artistdata[i].Lat, artistdata[i].Lon], {
                color: "green", 
                fillcolor: "green", 
                fillOpacity: 0.6, 
                radius: heat})
            );
        }

        // debug
        console.log(cityMarkers);

        cities = L.layerGroup(cityMarkers)
        // var baseMaps = {"Street Map": streetmap};
        // var overlayMaps = {"Song Count by City": cities};
        
        cities.addTo(myMap);

        
        // L.control.layers(overlayMaps, baseMaps, {collapsed: false}).addTo(myMap);
    
    });
}           

function init() {
    //console.log("init")
    var selector = d3.select("#dropdown");
    d3.json('/artists').then(function(artist) {
        artist.forEach((sample) => {
        selector
            .append("option")
            .text(sample)
            .property("value", sample);
        });
        
        //const firstSample = artist[0];
        //datashowing(firstSample);
        var sel = document.getElementById("dropdown");
        var something = sel.options[sel.selectedIndex].text;
        var something_else = something.replace(/\s/g, '%20');
        datashowing(something_else, false);
        buildPie(something_else);
        buildTime(something_else);
    }); 
}
function optionChanged(firstSample) {
        datashowing(firstSample, true);
        document.getElementById("pie").innerHTML = '';
        document.getElementById("times").innerHTML = '';
        buildPie(firstSample);
        buildTime(firstSample);
       }
        
init();

        



        

