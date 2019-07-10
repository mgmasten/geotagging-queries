var redIcon = new L.Icon({
  iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

document.addEventListener("DOMContentLoaded", contentLoaded);

function contentLoaded() {
     document.getElementById("submit").addEventListener("click", submission);
}

function submission() {
  var query = document.getElementById("query").value;
  var numResults = document.getElementById("numResults").value;
  console.log(query);
  console.log(numResults);

  document.getElementById("loaderid").style.visibility = "visible";
  document.getElementById("loadingMessage").innerHTML = "Running your search...";

  $.getJSON($SCRIPT_ROOT + '/map', {query: query, numResults: numResults}, function(data) {
        document.getElementById("loaderid").style.visibility = "hidden";
        document.getElementById("loadingMessage").innerHTML = "";
        plotMarkers(data);
      })
}

// Loop through the results array and place a marker for each
// set of coordinates.
function plotMarkers(results) {
 markersGroup.clearLayers();
 for (var i = 0; i < results.locations.length; i++) {
    var coords = results.locations[i];
    var latLng = L.latLng(coords['lat'], coords['lon']);
    L.marker(latLng, {icon: redIcon}).addTo(markersGroup);
    };
}
