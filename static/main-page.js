// Define colored marker icons for map
// Source: https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/

// Define a red icon
var redIcon = new L.Icon({
  iconUrl: '/static/icons/marker-icon-2x-red.png',
  shadowUrl: '/static/icons/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

// Define a blue icon
var blueIcon = new L.Icon({
  iconUrl: '/static/icons/marker-icon-2x-blue.png',
  shadowUrl: '/static/icons/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

// Make the selection boxes for search options nicer using Chosen
// See script and https://harvesthq.github.io/chosen/
$('.multiSelect').chosen({
  width: "50%"
});

$('.wideSelect').chosen({
  width: "50%"
});

$('#dateUnit').chosen({
  disable_search: true,
  width: "15%"
})

// Add listener to do setup
document.addEventListener('DOMContentLoaded', contentLoaded);

// Create Leaflet map object
mymap = L.map('mapId', {
  worldCopyJump: true
}).setView([20, -210], 2);

// Initialize map language to local languages
var mapLanguage = "local";

// Add map layers with the map tiles
// Local language tiles come from OpenStreetMap
var localLangsLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  id: 'local-langs-map',
  attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
  subdomains: 'abc'
}).addTo(mymap);

// English tiles come from arcGIS
var englishLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
  id: 'english-map',
  attribution: 'Tiles &copy; Esri &mdash; Source: Esri, DeLorme, NAVTEQ, USGS, Intermap, iPC, NRCAN, Esri Japan, METI, Esri China (Hong Kong), Esri (Thailand), TomTom, 2012'
});

// Make LayerGroups for both types of markers for easy addition and removal
// Types of markers are for the two geolocation methods
var ipMarkersGroup = L.layerGroup().addTo(mymap);
var scrapingMarkersGroup = L.layerGroup().addTo(mymap);

// Set both types of markers to be initially visible
var ipMarkersVisible = 'true';
var scrapingMarkersVisible = 'true';

// Tracks whether some results couldn't be geolocated
var locationFailure = false;
var nonlocatedMessage = '';

// Sets position of legend using Leaflet's DomUtil
// Controlled with Leaflet so that it always appears in the top right of map
function placeLegend() {
  var legend = L.control({
    position: 'topright'
  });

  legend.onAdd = function(mymap) {
    return $('#legend').get(0);
  };
  legend.addTo(mymap);
}

//
function placeNonlocatedDisplay() {
  var nonlocatedDisplay = L.control({
    position: 'bottomleft'
  });

  nonlocatedDisplay.onAdd = function(mymap) {
    return $('#nonlocatedDisplay').get(0);
  };
  nonlocatedDisplay.addTo(mymap);

  // Stop map from scrolling instead of nonlocatedDisplay
  L.DomEvent.disableScrollPropagation(L.DomUtil.get('nonlocatedDisplay'));

}


// Setup done when DOM content is loaded
function contentLoaded() {
  // Add actions for submit buttons, change in map language
  $('.submitButton').on('click', submission);
  $('#mapLanguage').on('click', changeMapLanguage);

  // Add logic for selection and deselection of all multiselect options
  $('.multiSelect').on('change', function(event, params) {
    if (params.selected == 'selectAll') {
      $('option').prop('selected', true);
      $(this).trigger('chosen:updated');
    } else if (params.deselected == 'selectAll') {
      $('option').prop('selected', false);
      $(this).trigger('chosen:updated');
    }
  });

  // Show details of results when button in marker popup is clicked
  $('.showResultsButton').on('click', showResults);

  placeLegend();
  placeNonlocatedDisplay();

  // Add action to toggle visibility of a type of marker when that part of the legend is clicked
  $('#ipLegend').on('click', toggleIpMarkers);
  $('#scrapingLegend').on('click', toggleScrapingMarkers);
}

// Actions taken when a search is submitted
function submission() {
  // Get submitted values
  var query = $('#query').val();
  var numResults = $('#numResults').val();
  var ipAddress = $('#ipAddress').prop("checked") ? 'true' : 'false';
  var scraping = $('#scraping').prop("checked") ? 'true' : 'false';
  var resultLanguage = $('#resultLanguage').chosen().val();
  var resultCountry = $('#resultCountry').chosen().val();
  var searchLanguage = $('#searchLanguage').chosen().val();
  var searchCountry = $('#searchCountry').chosen().val();
  var resultType = $('#resultType').chosen().val();
  var filter = $('#filtering').prop("checked") ? '0' : '1';
  var safe = $('#safeSearch').prop("checked") ? 'on' : 'off';
  var domains = $('#domains').val();
  var domainAction = $("input[type='radio'][name='domainAction']:checked").val();
  var dateRestrict = 'qdr:' + $('#dateUnit').chosen().val() + document.getElementById('dateNumber').value;

  // Make loader visible
  $('#loaderContainer').css('visibility', 'visible');

  // Hide and clear the box of results that couldn't be geolocated
  if ($('#nonlocatedDisplay').length) {
    $('#nonlocatedDisplay').css('visibility', 'hidden');
    $('#nonlocatedDisplay').html('');
  }

  // Create payload to the backend
  let payload = {
    query,
    numResults,
    ipAddress,
    scraping,
    searchOptions: {
      resultLanguage,
      resultCountry,
      searchLanguage,
      searchCountry,
      resultType,
      filter,
      safe,
      domains,
      domainAction,
      dateRestrict
    }
  };

  // Send request to backend
  $.ajax('/map', {
    type: 'post',
    data: JSON.stringify(payload),
    dataType: 'json',
    contentType: 'application/json',
    success: function(data) {
      // Hide loader
      $('#loaderContainer').css('visibility', 'hidden');
      plotAllMarkers(data);
    }
  });
}

// Swaps out the map tiles when the map language is changed
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

// Plot all the markers for one markersGroup
function plotMarkers(type, results, icon, markersGroup) {
  for (var i = 0; i < results.locations.length; i++) {
    var coords = results.locations[i];
    var frequency = results.frequencies[i];
    if (coords != null) {
      var latLng = L.latLng(coords[0], coords[1]);
      var marker = L.marker(latLng, {
        icon: icon
      }).addTo(markersGroup);

      // Construct the message for the popup
      // Display frequency of results for this coordinate
      var popupMessage = frequency.toString() + " result"
      if (frequency > 1) {
        popupMessage = popupMessage + "s";
      }

      // Add a button to show details of the results
      popupMessage += '&nbsp&nbsp&nbsp<button class="showResultsButton" onclick=showResults()>view</button>';

      popupMessage += '<div class="resultsDisplay"><br><br><ul>'

      // Add list of links (clickable) and their domains
      for (var j = 0; j < results.urls[i].length; j++) {
        popupMessage += '<li>';
        popupMessage += '<a class="myLinks" href=' + results.urls[i][j][0] + ' target="_blank">' + results.urls[i][j][1] + '</a>';
        popupMessage += '<span class="domain">  (' + results.urls[i][j][2] + ')</span>';
        popupMessage += '</li>';
      }

      popupMessage += '</ul></div>'

      // Set popup content and bind popup to marker.
      var popup = L.popup().setContent(popupMessage);
      marker.bindPopup(popup);

      // Marker opens on mouseover. Stays open on mouseout
      marker.on('mouseover', function(e) {
        this.openPopup();
      });

    // If coordinate is null, add the url to the list of sites that couldn't be geolocated
    } else {
      locationFailure = true;
      if (type == 'scraping') {
        for (var j = 0; j < results.urls[i].length; j++) {
          nonlocatedMessage += '<li>';
          nonlocatedMessage += '<a class="myLinks" href=' + results.urls[i][j][0] + ' target="_blank">' + results.urls[i][j][1] + '</a>';
          nonlocatedMessage += '<span class="domain">  (' + results.urls[i][j][2] + ')</span>';
          nonlocatedMessage += '</li>';
        }
      }
    }
  }
}

// Plot both sets of markers
function plotAllMarkers(results) {
  // Clear previous markers
  ipMarkersGroup.clearLayers();
  scrapingMarkersGroup.clearLayers();

  // Initialize
  nonlocatedMessage = '<b>Could not scrape location of:</b><br><br><ul class="ul2">';
  locationFailure = false;

  // Plot ip location results, if they exist
  if (results.ip.length != 0) {
    plotMarkers('ip', results.ip, redIcon, ipMarkersGroup);
  }

  // Plot scraping location results, if they exist
  if (results.scraping.length != 0) {
    plotMarkers('scraping', results.scraping, blueIcon, scrapingMarkersGroup);
  }

  // Adjust map zoom to best see markers (dependent on whether search options are open)
  if ($('#searchOptions').css('display') == 'none') {
    mymap.setZoom(2);
  } else {
    mymap.setZoom(1);
  }

  // If some results couldn't be geolocated, display them
  if (locationFailure) {
    nonlocatedMessage += '</ul>';
    addNonlocatedMessage(nonlocatedMessage);
  }
}

function addNonlocatedMessage(nonlocatedMessage) {
  $('#nonlocatedDisplay').html(nonlocatedMessage);
  $('#nonlocatedDisplay').css('visibility', 'visible');
}

// Loop through both layers of markers to find the popup that is open
// Get the hidden content (the url details) and display in a new popup in the same location
function showResults() {
  ipMarkersGroup.eachLayer(function(layer) {
    if (layer.isPopupOpen()) {
      content = layer.getPopup().getContent();
      index = content.indexOf('<ul');
      index2 = content.indexOf('</div>');
      content = content.substr(index, index2);
      latLng = layer.getPopup().getLatLng();
      L.popup({
        maxWidth: 400
      }).setContent(content).setLatLng(latLng).openOn(mymap);
      return;
    }
  });

  scrapingMarkersGroup.eachLayer(function(layer) {
    if (layer.isPopupOpen()) {
      content = layer.getPopup().getContent();
      index = content.indexOf('<ul');
      index2 = content.indexOf('</div>');
      content = content.substr(index, index2);
      latLng = layer.getPopup().getLatLng();
      L.popup({
        maxWidth: 400
      }).setContent(content).setLatLng(latLng).openOn(mymap);
      return;
    }
  });
}

// Display and hide the Google search options
function toggleSearchOptions() {
  if ($('#searchOptions').css('display') == 'none') {
    $('#searchOptions').css('display', 'inline');
    $('#mapId').css('width', '50%');
    $('#mapId').css('float', 'left');
    $('#toggleSearchOptions').prop('value', 'Hide search options');
  } else {
    $('#searchOptions').css('display', 'none');
    $('#mapId').css('width', '90%');
    $('#mapId').css('float', 'none');
    $('#toggleSearchOptions').prop('value', 'Show search options');
  }
}

// Toggle visibility of ip markers and the strikethrough of the legend text
function toggleIpMarkers() {
  if (ipMarkersVisible) {
    ipMarkersGroup.remove();
    $('#ipLegendLabel').css('text-decoration', 'line-through');
    ipMarkersVisible = false;
  } else {
    ipMarkersGroup.addTo(mymap);
    $('#ipLegendLabel').css('text-decoration', 'none');
    ipMarkersVisible = true;
  }
}

// Toggle visibility of scraping markers and the strikethrough of the legend text
function toggleScrapingMarkers() {
  if (scrapingMarkersVisible) {
    scrapingMarkersGroup.remove();
    $('#scrapingLegendLabel').css('text-decoration', 'line-through');
    scrapingMarkersVisible = false;
  } else {
    scrapingMarkersGroup.addTo(mymap);
    $('#scrapingLegendLabel').css('text-decoration', 'none');
    scrapingMarkersVisible = true;
  }
}
