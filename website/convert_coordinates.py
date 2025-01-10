from mgrs import MGRS
from geopy.distance import geodesic
import math
import copy

def mgrs_to_latlon(mgrs_str):
    """
    Convert an MGRS string to latitude and longitude.

    Parameters:
    mgrs_str: str : MGRS coordinate string

    Returns:
    tuple : (latitude, longitude)
    """
    m = MGRS()
    return m.toLatLon(mgrs_str)

def latlon_to_mgrs(lat, lon):
    """
    Convert latitude and longitude to MGRS string.

    Parameters:
    lat: float : Latitude
    lon: float : Longitude

    Returns:
    str : MGRS coordinate string
    """
    m = MGRS()
    return m.toMGRS(lat, lon)

def convert_mgrs_to_coordinates(mgrs_locations):
    """
    Convert multiple MGRS locations to (x,y) coordinates relative to the first location.

    Parameters:
    mgrs_locations: list : List of MGRS coordinates

    Returns:
    list : List of tuples representing (x, y) coordinates in nautical miles
    """
    # Convert the first MGRS location to latitude and longitude
    reference_latlon = mgrs_to_latlon(mgrs_locations[0])

    coordinates = []
    for mgrs in mgrs_locations:
        # Convert MGRS to latitude and longitude
        latlon = mgrs_to_latlon(mgrs)
        
        # Calculate distance from reference in nautical miles
        distance_meters = geodesic(reference_latlon, latlon).meters
        distance_nautical_miles = distance_meters / 1852  # Convert to nautical miles
        
        # Calculate heading from reference to current point
        lat1, lon1 = math.radians(reference_latlon[0]), math.radians(reference_latlon[1])
        lat2, lon2 = math.radians(latlon[0]), math.radians(latlon[1])

        dlon = lon2 - lon1
        x = math.cos(lat2) * math.sin(dlon)
        y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(dlon))
        initial_bearing = math.degrees(math.atan2(x, y))

        # Normalize to get x and y coordinates
        # x = distance * cos(heading)
        # y = distance * sin(heading)
        y_coord = distance_nautical_miles * math.cos(math.radians(initial_bearing))
        x_coord = distance_nautical_miles * math.sin(math.radians(initial_bearing))
        
        coordinates.append((round(x_coord, 4), round(y_coord, 4)))

    return coordinates

def convert_input_data(data):
    grids = [None]*len(data)
    converted_input_data = copy.deepcopy(data)
    for i, d in enumerate(data):
        grids[i]=d[0]
    relative_coords = convert_mgrs_to_coordinates(grids)
    for i, c in enumerate(converted_input_data):
        c[0]=relative_coords[i]
    return converted_input_data
    

def calculate_new_mgrs(mgrs_point, xy):
    """
    Calculate new MGRS point based on a reference MGRS point and relative distances.

    Parameters:
    mgrs_point: str : Original MGRS point
    x_distance: float : Relative x distance in nautical miles
    y_distance: float : Relative y distance in nautical miles

    Returns:
    str : New MGRS point
    """
    # Step 1: Convert MGRS to latitude and longitude
    latitude, longitude = mgrs_to_latlon(mgrs_point)
    
    # Step 2: Convert nautical miles to degrees (1 nautical mile = ~0.0005399566 degrees)
    x_distance = xy[0]
    y_distance = xy[1]
    lat_degrees_change = y_distance / 60  # 1 degree = 60 nautical miles
    lon_degrees_change = x_distance / 60   # 1 degree = 60 nautical miles

    # Step 3: Calculate new latitude and longitude
    new_latitude = latitude + lat_degrees_change
    new_longitude = longitude + lon_degrees_change

    # Step 4: Convert new latitude and longitude back to MGRS
    new_mgrs_point = latlon_to_mgrs(new_latitude, new_longitude)

    return new_mgrs_point