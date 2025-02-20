from gpxplotter import read_gpx_file, create_folium_map, add_segment_to_map
from gpxplotter.common import RELABEL
from datetime import datetime
import wetterdienst 
import folium
import branca.colormap as cm

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

def builld_default_map(latitude, longitude):
    the_map = create_folium_map(tiles='openstreetmap', max_bounds=True)
    folium.Marker([latitude, longitude], icon=folium.Icon(color='red')).add_to
    the_map.fit_bounds([[latitude - 0.05, longitude - 0.05],
                        [latitude + 0.05, longitude + 0.05]])
    return the_map



# Create client object.
dwd = DwdWeather(resolution="hourly")

# Find closest station to position.
closest = dwd.nearest_station(lon=7.0, lat=51.0)

# The hour you're interested in.
# The example is 2014-03-22 12:00 (UTC).
query_hour = datetime(2014, 3, 22, 12)

result = dwd.query(station_id=closest["station_id"], timestamp=query_hour)
print(result)