var mymap = L.map('mapid', {
     worldCopyJump: true,
     maxBounds: [ [-90, -180], [90, 180]]
}).setView([2.8, -210], 2);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
   id: 'world-map',
   attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
   subdomains: 'abc'
   }).addTo(mymap);

var markersGroup = L.layerGroup().addTo(mymap);
