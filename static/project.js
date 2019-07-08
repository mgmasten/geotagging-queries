document.addEventListener("DOMContentLoaded", contentLoaded);

function contentLoaded() {
     document.getElementById("submit").addEventListener("click", submission);
}

function submission() {
  var query = document.getElementById("query").value;
  console.log(query);
  //document.getElementById("displayQuery").innerHTML = query;
  $.getJSON($SCRIPT_ROOT + '/map', {query: query}, function(data) {
        plotMarkers(data);
      })
}

// Loop through the results array and place a marker for each
// set of coordinates.
function plotMarkers(results) {
 for (var i = 0; i < results.locations.length; i++) {
    var coords = results.locations[i];
    var latLng = new google.maps.LatLng(coords['lat'],coords['lon']);
    var marker = new google.maps.Marker({
      position: latLng,
      map: map
    });
 }
}
