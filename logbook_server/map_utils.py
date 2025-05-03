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
from flask import flash


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

velocity = 0
direction = 0
compass = 'N'
beaufort = 0

def update_weather_data(lat, lon):
    global velocity
    global direction
    global compass
    global beaufort
    while True:
        try:
            station = station_request(lat, lon)
            velocity = wind_velo(station)
            direction  = wind_direct(station) # in Grad (0 = Norden, 90 = Osten, 180 = Süden, 270 = Westen)
            compass = wind_compass(direction)
            print(type(compass))
            beaufort = beafort(velocity)
            
            if (velocity and direction):
                wind_speed = velocity
                wind_direction = direction
                compass_direction = compass
                print(compass_direction)
                getBeauforScale = beaufort
            else:
                flash(f"Keine Daten von Station {station}")
                
        except Exception as e:
            flash(f'Keine Wetterdaten: {e}')
        # time.sleep(200)
        
        return wind_speed, wind_direction, compass_direction, getBeauforScale, direction

# threading.Thread(target=update_weather_data, args=(52.924095, 13.713948), daemon=True).start()

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
    

def builld_default_map(latitude, longitude):
    the_map = create_folium_map(tiles='openstreetmap', max_bounds=True)
    folium.Marker([latitude, longitude], icon=folium.Icon(color='red')).add_to
    the_map.fit_bounds([[latitude - 0.035, longitude - 0.035],
                        [latitude + 0.035, longitude + 0.035]])
    return the_map