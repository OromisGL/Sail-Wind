import os
from gpxplotter import read_gpx_file, create_folium_map, add_segment_to_map
from gpxplotter.common import RELABEL
from datetime import datetime  
from wetterdienst import Settings
from wetterdienst.provider.dwd.observation import DwdObservationRequest
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
LATITUDE = 52.924095
LONGITUDE = 13.713948

WEATHER_DATA = {
    "wind_speed": None,
    "wind_direction": None,
    "compass_direction": None,
    "beaufort": None,
    "lat": LATITUDE,
    "lon": LONGITUDE
}


THIS_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(THIS_DIR, os.pardir))
LAKE_FILE = os.path.join(PROJECT_ROOT, "assets", "lake_set.json")

map_utils_bp = Blueprint('map_utils', __name__)

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
    
    location = (lat, lon)
    
    station = DwdObservationRequest(
    parameters=("10_minutes", "wind"),
    settings=settings
    ).filter_by_distance(latlon=location, distance=30) # Station request with in a radius of 30 km
    df = station.df.head()
    station = df[0]
    station_id = station.select("station_id").item() # Station Id for next request, can not access the data in on request 
    
    return station_id

def wind_velo(station):
    request = DwdObservationRequest(
        parameters=("10_minutes", "wind"),
        settings=settings
    ).filter_by_station_id(station_id=(station, )) # Get the Station Data
    
    values = request.values.all().df
    values = values.with_columns(pl.col("date").cast(pl.Utf8))  
    values = values.with_columns(pl.col("date").str.to_datetime())
    
    wind_speed = values.filter(pl.col("parameter") == "wind_speed").sort("date").tail(1).select("value").item()

    return wind_speed # wind speed in m/s

def wind_direct(station):
    request = DwdObservationRequest(
        parameters=("10_minutes", "wind"),
        settings=settings
    ).filter_by_station_id(station_id=(station, ))
    
    values = request.values.all().df
    values = values.with_columns(pl.col("date").cast(pl.Utf8))  
    values = values.with_columns(pl.col("date").str.to_datetime())
    
    wind_direction = values.filter(pl.col("parameter") == "wind_direction").sort("date").tail(1).select("value").item()

    return wind_direction # direction in degree

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()
    
def beafort(wind_speed):
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
    

def builld_default_map(LATITUDE, LONGITUDE):
    the_map = create_folium_map(tiles='openstreetmap', max_bounds=True)
    folium.Marker([LATITUDE, LONGITUDE], icon=folium.Icon(color='red')).add_to
    the_map.fit_bounds([[LATITUDE - 0.035, LONGITUDE - 0.035],
                        [LATITUDE + 0.035, LONGITUDE + 0.035]])
    return the_map

def lat_lon(lake_name):
    lakes = get_json(LAKE_FILE)
    for lake in lakes:
        if lake["name"] == lake_name:
            return lake["latitude"], lake["longitude"]
        
    raise ValueError(f"Lake {lake_name} not found.")

def update_WEATHER_DATA(lat, lon):
    global WEATHER_DATA 
    try:
        station = station_request(lat, lon)
        velocity = wind_velo(station)
        direction = wind_direct(station)
        compass = wind_compass(direction)
        beaufort = beafort(velocity)

        # in globalen Cache schreiben
        WEATHER_DATA.update({
            "wind_speed": velocity,
            "wind_direction": direction,
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
    while True:
        update_WEATHER_DATA(WEATHER_DATA["lat"], WEATHER_DATA["lon"])
        time.sleep(300)  # alle 5 Minuten

@map_utils_bp.route('/api/wind')
def get_wind_data():
    return jsonify(WEATHER_DATA)


def get_json(file_path):
    with open(file_path, encoding="utf-8") as f:
        return json.load(f)
    

@map_utils_bp.route('/api/wind_by_location')
def wind_by_location():
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
        return dict(loop_data = get_json(LAKE_FILE))