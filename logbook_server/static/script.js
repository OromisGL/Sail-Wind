// Creating instances 

let mapInstance, windMarker;
    
// init of the Map Leaflet 
function initMap(lat, lon) {
    mapInstance = L.map('map').setView([lat, lon], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(mapInstance);
    windMarker = L.marker([lat, lon]).addTo(mapInstance);
}

// Global Function for loading the winddata 
window.loadWindData = function(locationName) {
console.log("loadWindData called with:", locationName);

// Fetching the Data from flask api 
fetch(`/track/api/wind_by_location?location=${encodeURIComponent(locationName)}`)
    .then(response => {
    if (!response.ok) {
        throw new Error(`Network response was not ok (${response.status})`);
    }
    return response.json();
    })
    .then(data => {
    // Animation for the Location Change
    mapInstance.flyTo([data.lat, data.lon], 13, {
        animate: true,
        duration: 3
    });

    // Setting new Maker
    windMarker.setLatLng([data.lat, data.lon]);

    // Wind-Overlay updater
    document.getElementById('wind-speed')
            .textContent    = `Velocity: ${data.wind_speed} m/s`;
    document.getElementById('wind-strength')
            .textContent    = `Wind Strength: ${data.beaufort}`;
    document.getElementById('wind-direction')
            .textContent    = `Direction: ${data.compass_direction}`;

    // Update the Arrow in wind-info
    const arrow = document.getElementById('wind-arrow');
    arrow.src    = `data:image/png;base64,${data.wind_arrow}`;
    arrow.style.transform = `rotate(${data.wind_direction}deg)`;

    document.getElementById('wind-info').style.display = 'block';
    })
    .catch(err => console.error("Error loading wind data:", err));
};

// init the Buttons on base.html with click function and color change
document.addEventListener("DOMContentLoaded", () => {
        // Set default value: Werbellinsee
        const defaultLat = window.DEFAULT_LAT ;
        const defaultLon = window.DEFAULT_LON ;
        const initialLake = window.INITIAL_LAKE_NAME;

        initMap(defaultLat, defaultLon);

    // Bind the Buttons to the click function and update the the screen after clicked
    document.querySelectorAll(".lake-button").forEach(btn => {

        btn.addEventListener("click", function() {

            document.querySelectorAll(".lake-button").forEach(b => {
                b.classList.remove("active");
            });

            this.classList.add("active");

            loadWindData(btn.dataset.lake);
        });
    });

    // Init the default Visit on the Map
    if (initlake) {
        loadWindData(initialLake);
    }
});