// Initialize map centered on Pakistan
const map = L.map('map').setView([30.3753, 69.3451], 5);

// Add OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 18,
  attribution: '© OpenStreetMap'
}).addTo(map);

// Marker list provided by Flask
const cityMarkers = JSON.parse(document.getElementById("city-markers").textContent);

// Add markers
cityMarkers.forEach(city => {
  L.marker([city.lat, city.lng])
    .addTo(map)
    .bindPopup(`<strong>${city.name}</strong>`);
});
