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
        // Fetching the Data from flask api 
        fetch(`/track/api/wind_by_location?location=${encodeURIComponent(locationName)}`)
                .then(resp => {
                if (!resp.ok) throw new Error(`Status ${resp.status}`);
                return resp.json();
            })
            .then(data => {
                // Globale Defaults updaten
                window.defaultLat    = data.lat;
                window.defaultLon    = data.lon;
                window.initialLake   = locationName;

                console.log("New defaults:", window.initialLake, window.defaultLat, window.defaultLon);

                // Animation for the Location Change
                mapInstance.flyTo([data.lat, data.lon], 13, { animate: true, duration: 1.5 });
                windMarker.setLatLng([data.lat, data.lon]);

                // Overlay updates
                document.getElementById('wind-speed')
                        .textContent = `Velocity: ${data.wind_speed} m/s`;
                document.getElementById('wind-strength')
                        .textContent = `Wind Strength: ${data.beaufort}`;
                document.getElementById('wind-direction')
                        .textContent = `Direction: ${data.compass_direction}`;

                const arrow = document.getElementById('wind-arrow');
                arrow.src            = `data:image/png;base64,${data.wind_arrow}`;
                arrow.style.transform= `rotate(${data.wind_direction}deg)`;
                document.getElementById('wind-info').style.display = 'block';
            })
            .catch(err => console.error("Error loading wind data:", err));
    };

    // init the Buttons on base.html with click function and color change
    document.addEventListener("DOMContentLoaded", () => {
        const mapEl = document.getElementById("map");
        // load data-Attributes from #map
        const lat0  = parseFloat(mapEl.dataset.defaultLat);
        const lon0  = parseFloat(mapEl.dataset.defaultLon);
        const lake0 = mapEl.dataset.initialLake;

        console.log(mapEl.dataset);
        // init map with default values 
        initMap(lat0, lon0);
        // set the default global
        window.defaultLat  = lat0;
        window.defaultLon  = lon0;
        window.initialLake = lake0;

        // add click event for all buttons
        document.querySelectorAll(".lake-button").forEach(btn => {
            btn.addEventListener("click", () => {
                // change active status
                document.querySelectorAll(".lake-button")
                        .forEach(b => b.classList.remove("active"));
                btn.classList.add("active");

                // get only the data from the active buttons 
                loadWindData(btn.dataset.lake);
            });
        });

        // load the data from the active Buttons
        const activeBtn = document.querySelector(".lake-button.active") || document.querySelector(".lake-button");
        if (activeBtn) {
            loadWindData(activeBtn.dataset.lake);
        }
    });
