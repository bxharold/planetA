#!/usr/local/bin/python3
from geopy.geocoders import Nominatim

def locate(lat,lon):
    geolocator = Nominatim(user_agent="Encinitas PlanetA")
    location = geolocator.reverse(f"{lat}, {lon}")
    print (location.raw)
    return location.raw['address']['town']

def main():
    x = locate(33.036823, -117.292316)
    print (x)

if __name__ == "__main__":
    main()

