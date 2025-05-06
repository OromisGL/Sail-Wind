import os
from gpxplotter import read_gpx_file, create_folium_map, add_segment_to_map
from gpxplotter.common import RELABEL
from datetime import datetime  
from wetterdienst import Settings
from wetterdienst.provider.dwd.observation import DwdObservationRequest
from wetterdienst.metadata.period import Period
import polars as pl
import folium
from folium.plugins import FloatImage
import base64
import branca.colormap as cm
import time
import threading
from flask import flash, Blueprint, request, jsonify, json
import zlib

# default Werbellinsee
LATITUDE = 52.933333
LONGITUDE = 13.716667

# Dict for all relevant Data (at the moment) 
WEATHER_DATA = {
    "wind_speed": None,
    "wind_direction": None,
    "compass_direction": None,
    "beaufort": None,
    "lat": LATITUDE,
    "lon": LONGITUDE
}

# using the os libary for getting file Paths
THIS_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(THIS_DIR, os.pardir))
LAKE_FILE = os.path.join(PROJECT_ROOT, "assets", "lake_set.json")

# instance of the map utils api 
map_utils_bp = Blueprint('map_utils', __name__)

# Settings wor Wetterdinst requests
settings = Settings(
    ts_shape="long",         # Ausgabe als lange Tabelle
    ts_humanize=True,        # Parameter verständlicher anzeigen
    ts_convert_units=True    # Werte in SI-Einheiten umwandeln
) 

line_options = {'weight': 8}
color_by = 'Velocity / km/h'

linear = cm.LinearColormap(
    ['green', 'yellow', 'red'],
    vmin=2, vmax=20
)
linear.caption = RELABEL.get(color_by, color_by)


def build_map(path):
    """
    Builds Folium Map with a Color linear for visulizing the speed in km/h.
    """
    the_map = create_folium_map(tiles='openstreetmap')
    for track in read_gpx_file(path):
        for i, segment in enumerate(track['segments']):
            line = folium.ColorLine(positions=segment['latlon'], colormap=linear,
                                    colors=segment[color_by][:-1], control=False, **line_options)
            line.add_to(the_map)
    the_map.add_child(linear)
    boundary = the_map.get_bounds()
    the_map.fit_bounds(boundary, padding=(3, 3))

    # To display the map in a Jupyter notebook:
    return the_map
#for track in read_gpx_file('2022/2022-07-30_s_gelb_Steffen_elli.gpx'):
#   print(track)
#    print("end track")


def station_request(lat, lon):
    """
    Search for the Next DWD Weatherstation near the location at lat lon. 
    Starts at radius 5km and increments by 5km until 30km.
    When reaches 40km it breaks with Exception.
    """
    location = (lat, lon)
    distance_min = 5
    distance_max = 40
    step = 5
    
    while distance_min <= distance_max:
        try:
            station = DwdObservationRequest(
            parameters=("10_minutes", "wind"), 
            settings=settings).filter_by_distance(latlon=location, distance=distance_min) # Station request with in a radius of 30 km
            
            df = station.df
            
            if df.shape[0] == 0:
                raise ImportError(f"Sation not in {distance_min} km")
            
            first = station.df.head(1)[0]
            
            station_id = first.select("station_id").item()# Station Id for next request, can not access the data in on request
            
            return station_id
        
        except FileNotFoundError:
            distance_min += step
        
        except Exception as e:
            print(f"Search radius increments by 5km at {distance_min} km radius""")
            distance_min += step
            
    raise RuntimeError(
        f"""
        Keine Station mit Winddaten gefunden im Umkreis bis {distance_max} km um {location}
        """
        )


def wind_data_fetch(station):
    """
    Loads in a requncy of 10 min all new wind Data from the Station.
    Combines fetching wind speed and direction and gets the the most recent data.
    """
    request = DwdObservationRequest(
        parameters=("10_minutes", "wind"),
        periods=Period.RECENT,
        settings=settings,
    ).filter_by_station_id(station_id=(station, )) # Get the Station Data
    
    df = request.values.all().df
    
    latest = (
        df.sort("date")
        .group_by("parameter")
        .agg(pl.last("value").alias("value"))
    )

    wind_speed = latest.filter(pl.col("parameter") == "wind_speed").select("value").item()
    wind_direction = latest.filter(pl.col("parameter") == "wind_direction").select("value").item()
    
    return {"wind_speed": wind_speed, "wind_direction": wind_direction}


def encode_image(image_path):
    """
    Opens the wind arrow .png and encodes the file. 
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()
    
    
def beafort(wind_speed):
    """
    Gets the value of the beaufort scale for Wind Speed visulization.
    """
    if wind_speed <= 0.2:
        return 0
    if wind_speed <= 1.5:
        return 1
    if wind_speed <= 3.3:
        return 2
    if wind_speed <= 5.4:
        return 3
    if wind_speed <= 7.9:
        return 4
    if wind_speed <= 10.7:
        return 5
    if wind_speed <= 13.8:
        return 6
    if wind_speed <= 17.1:
        return 7
    if wind_speed <= 20.7:
        return 8
    if wind_speed <= 24.4:
        return 9
    if wind_speed <= 28.4:
        return 10
    if wind_speed <= 32.6:
        return 11
    
    return 12
    

def wind_compass(wind_direction):
    """
    Getting the compass-litterals from the wind direction in degrees.
    """
    if wind_direction <= 10 or wind_direction in range(341, 361):
        return 'N'
    if wind_direction in range(11, 31):
        return 'N/NO'
    if wind_direction in range(31, 51):
        return 'NO'
    if wind_direction in range(51, 71):
        return 'O/NO'
    if wind_direction in range(71, 101):
        return 'O'
    if wind_direction in range(101, 121):
        return 'O/SO'
    if wind_direction in range(121, 141):
        return 'SO'
    if wind_direction in range(141, 161):
        return 'S/SO'
    if wind_direction in range(161, 191):
        return 'S'
    if wind_direction in range(191, 211):
        return 'S/SW'
    if wind_direction in range(211, 231):
        return 'SW'
    if wind_direction in range(231, 251):
        return 'W/SW'
    if wind_direction in range(251, 281):
        return 'W'
    if wind_direction in range(281, 301):
        return 'W/NW'
    if wind_direction in range(301, 321):
        return 'NW'
    if wind_direction in range(321, 341):
        return 'N/NW'


def lat_lon(lake_name):
    """
    extracting the lat and lon values based on the Lake Name from LAKE_FILE json.
    """
    lakes = get_json(LAKE_FILE)
    for lake in lakes:
        if lake["name"] == lake_name:
            return lake["latitude"], lake["longitude"]
        
    raise ValueError(f"Lake {lake_name} not found.")


def update_WEATHER_DATA(lat, lon):
    """
    Function Calls:
    
    [station_request, wind_data_fetch, wind_compass, beafort]
    
    After extractiong all the Data from the Function Calls the WEATHER_DATA global gets new Values.
    """
    global WEATHER_DATA 
    try:
        station = station_request(lat, lon)
        latest = wind_data_fetch(station)
        print(latest)
        compass = wind_compass(latest["wind_direction"])
        beaufort = beafort(latest["wind_speed"])

        # in globalen Cache schreiben
        WEATHER_DATA.update({
            "wind_speed": latest["wind_speed"],
            "wind_direction": latest["wind_direction"],
            "compass_direction": compass,
            "beaufort": beaufort,
            "lat": lat,
            "lon": lon
        })

    except zlib.error as e:
        print(f"[zlib Fehler beim Dekomprimieren]: {e}")
    except Exception as e:
        print(f"[Fehler beim Abrufen der Wetterdaten]: {e}")


def weather_updater():
    """
    Calls the Main Function. Is target of the Thread in __init__.py. Duaration 5 min for the next call.
    """
    while True:
        update_WEATHER_DATA(WEATHER_DATA["lat"], WEATHER_DATA["lon"])
        time.sleep(300)  # alle 5 Minuten

@map_utils_bp.route('/api/wind')
def get_wind_data():
    """
    returns a json of the WEATHER_DATA Dict.
    """
    return jsonify(WEATHER_DATA)


def get_json(file_path):
    """
    Opens a json file.
    """
    with open(file_path, encoding="utf-8") as f:
        return json.load(f)
    

@map_utils_bp.route('/api/wind_by_location')
def wind_by_location():
    """
    Asks for the Lake Name and returns the new weather Data for the new Location in a json. 
    """
    lake_name = request.args.get("location")
    
    try:
        lat, lon = lat_lon(lake_name)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
    update_WEATHER_DATA(lat, lon)
    return jsonify(WEATHER_DATA)


def get_lake_data(app):
    @app.context_processor
    def injection():
        """
        Makes the data in Lake File json iterrable for the Javascript function loadWindData in static/script.js.
        """
        return dict(loop_data = get_json(LAKE_FILE))