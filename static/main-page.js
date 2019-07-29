// Where should this go?
// Define a red marker icon
var redIcon = new L.Icon({
  iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

$("#resultLanguage").chosen();

document.addEventListener("DOMContentLoaded", contentLoaded);
// Create map object
mymap = L.map('mapId', {
     worldCopyJump: true,
     maxBounds: [ [-90, -180], [90, 180]]
     }).setView([2.8, -210], 2);

var mapLanguage = "local";

// Link to tile sources
localLangsLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
     id: 'local-langs-map',
     attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
     subdomains: 'abc'
}).addTo(mymap);

englishLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
     id: 'english-map',
     attribution: 'Tiles &copy; Esri &mdash; Source: Esri, DeLorme, NAVTEQ, USGS, Intermap, iPC, NRCAN, Esri Japan, METI, Esri China (Hong Kong), Esri (Thailand), TomTom, 2012'
});

// Make LayerGroup for markers for easy clearing
markersGroup = L.layerGroup().addTo(mymap);


function contentLoaded() {
     document.getElementById("submit").addEventListener("click", submission);
     document.getElementById("mapLanguage").addEventListener("click", changeMapLanguage);
}

function submission() {
  var query = document.getElementById("query").value;
  var numResults = document.getElementById("numResults").value;
  var resultLanguage = $("#resultLanguage").chosen().val();
  console.log(resultLanguage);

  document.getElementById("loaderContainer").style.visibility = "visible";
  console.log({data: {query: query, numResults: numResults, resultLanguage: resultLanguage}});

  //$SCRIPT_ROOT = request.script_root | tojson | safe;     // Is it okay to eliminate this?
  /*$.post('/map', {query: query, numResults: numResults}, function(data) {
        document.getElementById("loaderContainer").style.visibility = "hidden";
        plotMarkers(data);
   }, "json");*/

   $.ajax({
    type: 'POST',
    url: '/map',
    contentType: 'application/json; charset=utf-8',
    dataType: 'json',
    data: JSON.stringify({query, numResults, resultLangugage})
}).done(function(data) {
      document.getElementById("loaderContainer").style.visibility = "hidden";
      plotMarkers(data);
});
}

function changeMapLanguage() {
     var languageChecked = $("input[type='radio'][name='mapLanguage']:checked").val();
     if (languageChecked != mapLanguage) {
          mapLanguage = languageChecked;
          if (mapLanguage == "local") {
               englishLayer.remove();
               localLangsLayer.addTo(mymap);
          } else if (mapLanguage == "english") {
               localLangsLayer.remove();
               englishLayer.addTo(mymap);
          }
     }
}

// Loop through the results array and place a marker for each set of coordinates.
function plotMarkers(results) {
     markersGroup.clearLayers();  // Clear previous markers
     for (var i = 0; i < results.locations.length; i++) {
          var coords = results.locations[i];
          var frequency = results.frequencies[i];
          var latLng = L.latLng(coords[0], coords[1]);
          var marker = L.marker(latLng, {icon: redIcon}).addTo(markersGroup);

          var popupMessage = frequency.toString() + " result"
          if (frequency > 1) {
               popupMessage = popupMessage + "s";
          }

          // Bind popup. Opens on mouseover, closes on mouseout
          marker.bindPopup(popupMessage);
          marker.on('mouseover', function (e) { this.openPopup(); });
          marker.on('mouseout', function (e) { this.closePopup(); });
     };
}
