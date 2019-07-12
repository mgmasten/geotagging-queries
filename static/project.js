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

document.addEventListener("DOMContentLoaded", contentLoaded);

function contentLoaded() {
     document.getElementById("submit").addEventListener("click", submission);
}

function submission() {
  var query = document.getElementById("query").value;
  var numResults = document.getElementById("numResults").value;

  document.getElementById("loaderAndMessage").style.visibility = "visible";

  //$SCRIPT_ROOT = request.script_root | tojson | safe;     // Is it okay to eliminate this?
  $.getJSON('/map', {query: query, numResults: numResults}, function(data) {
        document.getElementById("loaderId").style.visibility = "hidden";
        document.getElementById("loadingMessageId").innerHTML = "";
        plotMarkers(data);
      })
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
