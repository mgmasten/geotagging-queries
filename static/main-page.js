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

$('.multiSelect').chosen({
     width: "50%"
});

$('.select').chosen({
     width: "50%"
});

document.addEventListener('DOMContentLoaded', contentLoaded);
// Create map object
mymap = L.map('mapId', {
  worldCopyJump: true
  /*maxBounds: [[-90, -180], [90, 180]]*/
}).setView([2.8, -210], 1);

var mapLanguage = "local";

// Link to tile sources
var localLangsLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  id: 'local-langs-map',
  attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
  subdomains: 'abc'
}).addTo(mymap);

var englishLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
  id: 'english-map',
  attribution: 'Tiles &copy; Esri &mdash; Source: Esri, DeLorme, NAVTEQ, USGS, Intermap, iPC, NRCAN, Esri Japan, METI, Esri China (Hong Kong), Esri (Thailand), TomTom, 2012'
});

// Make LayerGroup for markers for easy clearing
markersGroup = L.layerGroup().addTo(mymap);

function contentLoaded() {
  $('.submitButton').on('click', submission);
  document.getElementById('mapLanguage').addEventListener('click', changeMapLanguage);

  $('.multiSelect').on('change', function(event, params) {
    if (params.selected == 'selectAll') {
      $('option').prop('selected', true);
      $(this).trigger('chosen:updated');
    } else if (params.deselected == 'selectAll') {
      $('option').prop('selected', false);
      $(this).trigger('chosen:updated');
    }
  });

  $('.popupArrow').on('click', showResults);
}

function submission() {
  var query = document.getElementById('query').value;
  var numResults = document.getElementById('numResults').value;
  var resultLanguage = $('#resultLanguage').chosen().val();
  var resultCountry = $('#resultCountry').chosen().val();
  var searchLanguage = $('#searchLanguage').chosen().val();
  var searchCountry = $('#searchCountry').chosen().val();
  var filter = $('#filtering').prop("checked") ? '0' : '1';
  var safe = $('#safeSearch').prop("checked") ? 'on' : 'off';

  document.getElementById('loaderContainer').style.visibility = "visible";
  //console.log({query, numResults, searchOptions: {resultLanguage, resultCountry}} );

  //$SCRIPT_ROOT = request.script_root | tojson | safe;     // Is it okay to eliminate this?
  let payload = {query, numResults, searchOptions: { resultLanguage, resultCountry, searchLanguage, searchCountry, filter, safe} };
  $.ajax('/map', {
    type: 'post',
    data: JSON.stringify(payload),
    dataType: 'json',
    contentType: 'application/json',
    success: function(data) {
      document.getElementById('loaderContainer').style.visibility = "hidden";
      plotMarkers(data);
    }
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

    popupMessage += '&nbsp&nbsp&nbsp<button class="popupArrow" onclick=showResults()>view</button>';
    //\u26BC

    popupMessage += '<div class="resultsDisplay"><br><br><ul>'
    for (var j = 0; j < results.urls[i].length; j++) {
      popupMessage += '<li><a class="myLinks" href=' + results.urls[i][j][0] + ' target="_blank">' + results.urls[i][j][1] + '</a><span class="domain">  (' + results.urls[i][j][2] + ')</span></li>'
}

    popupMessage += '</ul></div>'

    // Bind popup. Opens on mouseover, closes on mouseout
    var popup = L.popup().setContent(popupMessage);
    marker.bindPopup(popup);

    marker.on('mouseover', function (e) { this.openPopup(); });
    /*marker.on('mouseout', function (e) { this.closePopup(); });*/
  }
}

function showResults() {
  //$('.resultsDisplay').css('display', 'inline');
  markersGroup.eachLayer(function (layer) {
    if (layer.isPopupOpen()) {
      content = layer.getPopup().getContent();
      index = content.indexOf('<ul');
      index2 = content.indexOf('</div>');
      content = content.substr(index, index2);
      console.log(content);
      latLng = layer.getPopup().getLatLng();
      L.popup({maxWidth: 400}).setContent(content).setLatLng(latLng).openOn(mymap);
      return;
    }
});
}
