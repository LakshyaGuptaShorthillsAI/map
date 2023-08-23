import folium
import geopandas as gpd
from shapely.geometry import Point
from geopy.geocoders import Nominatim
import json

# Load state borders shapefile data
shapefile_path = './states_and_city_datasets/ne_110m_admin_1_states_provinces.shp'
gdf = gpd.read_file(shapefile_path)

def getCityCoordinatesFromNames(file_path):
    city_coordinates = {}
    # Read the json file
    with open(file_path) as f:
        json_data = json.load(f)
        city_names = json_data["cities"]
    geolocator = Nominatim(user_agent="my_geocoder")

    # Get coordinates for each city
    for city_name in city_names:
        location = geolocator.geocode(city_name)
        if location:
            city_coordinates[city_name] = (location.latitude, location.longitude)
    return city_coordinates
    # for city,coord in city_coordinates.items():
    #     print(city,coord)

def getStateForCoordinates(city_coordinates):
    # Create a GeoDataFrame from the coordinates
    cities=[city for city in city_coordinates.keys()]
    coordinates = [coords for coords in city_coordinates.values()]
    geom = [Point(coord[1], coord[0]) for coord in coordinates]
    dataframe = gpd.GeoDataFrame(geometry=geom)

    # Perform a spatial join to find the state corresponding to each coordinate
    result = gpd.sjoin(dataframe, gdf, how="inner", op="within")
    return result

def map():
    coordinates = getCityCoordinatesFromNames('usa_data.json')
    result = getStateForCoordinates(coordinates)
    
    # print(coordinates['Monmouth'])

    # for city, coords in coordinates.items():
    #     print(city,coords)
    # print(result['name'])
    
    # Create a map centered at a specific location
    m = folium.Map(location=[coordinates['Monmouth'][0],coordinates['Monmouth'][1]], zoom_start=5)

    # Filter the GeoDataFrame to include only the selected states
    selected_states_gdf = gdf[gdf['name'].isin(result['name'])]
    
    # print(selected_states_gdf)

    # Add state borders to the map
    folium.Choropleth(
        geo_data=selected_states_gdf,
        fill_opacity=0,
        line_opacity=0.5,
        line_weight=2,
        line_color='red',
        color='lightpink'
    ).add_to(m)

    # Add coordinates to the map
    for city,coord in coordinates.items():
        folium.CircleMarker(
            location=[coord[0], coord[1]],
            radius=5,
            color='yellow',
            fill=True,
            fill_color='red',
            fill_opacity=1,
            tooltip=f"{city}"
        ).add_to(m)

    # Save the map to an HTML file
    m.save('map1.html')
    
mapObj = map()
