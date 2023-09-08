#!/usr/local/bin/python3
# creates a csv file with iss location info       issrecorder.py

import time, datetime, urllib.request, json
from geopy.geocoders import Nominatim

url = "http://api.open-notify.org/iss-now.json"

def debugCurrentLocation():
    with urllib.request.urlopen(url) as response:
        html = response.read()   # returns type is <class 'bytes'>
        #  b'{"timestamp": 1689881524, "message": "success", 
        #     "iss_position": {"latitude": "-40.6869", "longitude": "153.4892"}}'
        htmlj = json.loads(html)  # <class 'dict'> 
        print(type(htmlj), htmlj)
        print(htmlj['timestamp'])
        print(htmlj['iss_position']['latitude'])

def get_nearest_location(latitude, longitude): 
    # Input: latitude and longitude
    # returns info from Nominatim geolocator.reverse
    try:
        geolocator = Nominatim(user_agent="CS50p PlanetA")
        location = geolocator.reverse(f"{latitude}, {longitude}")
    except:
        print ("geolocator try failed")
        nearest_location = f"{latitude}, {longitude}"
    else: 
        if location:
            if location.raw["address"]["country_code"] == 'us':
                nearest_location = location.raw["address"]["state"]
            else:
                nearest_location = location.raw["address"]["country"]
        else:  # assume ocean; no oceancolor (as in planetA.py)
            nearest_location = "ocean"
    # finally:
    #     print(f"nearest_location={nearest_location}") 
    return nearest_location

def fullCurrentLocation(i):  # isschart panel expects lat,lon,timestamp,nicedate,loc
    try:
        with urllib.request.urlopen(url) as response:
            r = response.read()
            rj = json.loads(r)
            print(type(rj), rj)  # <class 'dict'> 
            tim = rj['timestamp']
            lat = rj['iss_position']['latitude']
            lon = rj['iss_position']['longitude']
            print(rj['timestamp'], rj['iss_position']['latitude'],rj['iss_position']['longitude'])
            nicedate = datetime.datetime.utcfromtimestamp(tim).strftime('%H:%M:%S')
            loc = get_nearest_location(lat, lon)
            # msg = f"{rj['timestamp']},{rj['iss_position']['latitude']},{rj['iss_position']['longitude']}"
            msg = f"{tim},{lat},{lon},{nicedate},{loc}"
            with open('isspath.csv','a') as file:
                print(msg)
                print(msg, file=file)
    except:
        print(f"fullCurrentLocation error, step {i}")

def currentLocation():
    with urllib.request.urlopen(url) as response:
        r = response.read()    # returns type is <class 'bytes'>
        rj = json.loads(r)     # type(rj) is <class 'dict'> 
        print(rj['timestamp'], rj['iss_position']['latitude'],rj['iss_position']['longitude'])
        with open('isspath.csv','a') as file:  
            msg = f"{rj['timestamp']},{rj['iss_position']['latitude']},{rj['iss_position']['longitude']}"
            print(msg, file=file)

for i in range(1 * 92 * 3):  # orbits * minutes/orbit * samples/minute` 
    fullCurrentLocation(i)
    time.sleep(20)

"""
#### I plan to hard-code the table, maybe block it from the "list tables"
# demo file:   isspath-americas.csv

.mode csv
DROP TABLE IF EXISTS "isspath";
CREATE TABLE IF NOT EXISTS "isspath" ( 
    -- id INTEGER PRIMARY KEY,  -- use builtin rowid instead
    tim INTEGER, 
    lat REAL,
    lon REAL,
    nicedate TEXT,
    loc varchar(20)
);
.import isspath.csv isspath
.mode columns
select * from isspath;
select count(*) from isspath;
-- select * from isspath order by rowid desc;

"""

