#!/usr/local/bin/python3

"""
geopy_test.py
    uses the reverse geocoding feature of the GeoPy library in Python to 
    find the nearest country, state, or ocean given a latitude and longitude, 
    The Nominatim geocoder is a free, open-source API provided by OpenStreetMap. 
Environment:
    python3  -m venv venv
    source venv/bin/activate
    pip3 install geopy
"""

from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import sys

def get_nearest_location(latitude, longitude):
    # Get the address of the input latitude and longitude
    # Initialize geolocator
    try:
        geolocator = Nominatim(user_agent="CS50p PlanetA")
        location = geolocator.reverse(f"{latitude}, {longitude}")
    except:
        print ("geolocator try failed")
        nearest_location = f"{latitude}, {longitude}"
    if location:
        print(type(location.raw))
        print(f"===> {location}")
        print(f"===> {location.raw['address']['country_code']}")
        # # Get the distance between input location and nearest location
        distance = geodesic((latitude, longitude), (location.latitude, location.longitude)).km
        location.raw["distance"] = distance   # that was easy...
    return location.raw

def main():
    lat,lon = 51.0,0.9   # London, returns United Kingdom
    lat,lon = -45,-135   # ocean.  AttributeError: 'NoneType' object has no attribute 'raw'
    lat,lon = 45,-90   #  returns wisconsin
    lat,lon = 45,-65   #  returns Nova Scotia
    lat,lon = -20.1472512,  164.12375677974939
    lat,lon = -13.664413549999999, 167.17416363186484
    lat,lon = 39.7837304, -100.445882
    lat,lon = 33,-117   # encinitas, returns california
    x = get_nearest_location(lat,lon)
    print(f"{x['address']['country_code']}, {x['address']['country']}, {x['address']['state']}, {x['distance']}")
    print(f"{x['address']['country_code']}, {x['address']['country']} ")

if __name__ == '__main__':
    main()

