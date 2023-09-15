#!/usr/local/bin/python3

from geopy.geocoders import Nominatim

def country_state(lat,lon):
    x = get_nearest_location(lat,lon)
    if 'country_code' in x:
        if x['country_code'] == 'us':
            rv = x['state']
        else:
            rv = x['country']
    else:
        rv = x['name']
    return rv

def main():
    # print(f"1==> {get_nearest_location(33.04,-117.30)} \n")
    # print(f"2==> {get_nearest_location(43,-97)} \n")
    # print(f"3==> {get_nearest_location(0,0)} \n")
    # print(f"4==> {get_nearest_location(51,7)} \n")
    # print(f"5==> {get_nearest_location(-34,151)} \n")
    # print(f"6==> {get_nearest_location(32.299507,-64.790337)} \n")
    # print(f"7==> {get_nearest_location(-21,-175)} \n")

    print(f"1==> {country_state(33.04,-117.30)} \n")   # California
    print(f"2==> {country_state(43,-97)} \n")   # South Dakota
    print(f"3.0==> {country_state(30,-45)} \n")      # ocean natl
    print(f"3.1==> {country_state(-30,-45)} \n")      # ocean satl
    print(f"3.2==> {country_state(70,0)} \n")      # ocean artc
    print(f"3.3==> {country_state(-70,0)} \n")      # ocean sthn
    print(f"3.4==> {country_state(-30,-150)} \n")      # ocean spac
    print(f"4==> {country_state(51,7)} \n")     # Deutschland
    print(f"5==> {country_state(-34,151)} \n")  # Australia
    print(f"6==> {country_state(32.299507,-64.790337)} \n") # Bermuda
    print(f"7==> {country_state(-21,-175)} \n") # Tonga


def get_nearest_location(latitude, longitude):
    # return country, US state, or ocean associated w/ lat,lon
    nearest_location = "poodle"
    print(latitude, longitude, end="  " )
    try:
        geolocator = Nominatim(user_agent="CS50p PlanetA")
        location = geolocator.reverse(f"{latitude}, {longitude}")
    except:
        print ("geolocator try failed")
        nearest_location = { "code": "none", "name": "Nothing",   "color" : "#ffffff" }
        print(f"nearest_location fallthru={nearest_location}")
        return nearest_location
    if location:
        r = location.raw
        nearest_loc = {}
        # print(f"we have a location...{r}")
        lat = r["lat"]
        lon = r["lon"]
        if "address" in r:
            nearest_loc['code'] = "land"
            nearest_loc['color'] = ""#00ff00""
            if "country_code" in r["address"]:
                if r["address"]["country_code"] == 'us':
                    nearest_loc['name'] = r["address"]["state"]
                else:
                    nearest_loc['name'] = r["address"]["country"]
            else:  # no country, assume ocean
                nearest_loc['code'] = "ocean"
                # nearest_location = oceancolormap(lat,lon)
                nearest_loc['name'] =  "ocean"
                nearest_loc['color'] = ""#0000ff""
    else:  # no location found. use default
        nearest_loc = { "code": "none", "name": "Nothing",   "color" : "#ffffff" }
        ocm = oceancolormap(latitude, longitude)
        nearest_loc["code"] = ocm["code"]
        nearest_loc["name"] = ocm["name"]
        nearest_loc["color"] = ocm["color"]        
    print(f"nearest_location={nearest_loc}")
    return nearest_loc

def validLatLon(x):  # return 0 if not a float; no test for -180<=x<=180
    try:
        return float(x)
    except ValueError:
        return None

def revgeo(lat,lon):    #   return full JSON, or "NOWHERE" if not found
    # http://127.0.0.1:5000/revgeo?lat=33&lon=-117  (-127 is ocean, -117 is Encinitas)
    # http://127.0.0.1:5000/revgeo?lat=33.04&lon=-117.30
    # lat=request.args['lat']
    # lon=request.args['lon']
    lat,lon = validLatLon(lat), validLatLon(lon)
    if lat is None or lon is None: 
        return "value error"
    try:
        geolocator = Nominatim(user_agent="CS50p PlanetA")
        location = geolocator.reverse(f"{lat}, {lon}")
        print("loc=",location)
    except:
        print ("geolocator try failed")
        nearest_location = f"{lat}, {lon}"
    else:
        if location:
            # print("==>",location.raw["address"]["town"],"<==")
            return location.raw
        else:
            return "NOWHERE"

def oceancolormap(lat,lon):
    # The color is only meaningful when lat,lon is over an ocean.
    lat = int(float(lat))
    lon = int(float(lon))
    oceanColorList = [
        { "code": "artc", "name": "Arctic Ocean",   "color" : "#ccccff" },
        { "code": "sthn", "name": "Southern Ocean", "color" : "#cc6699" },
        { "code": "npac", "name": "North Pacific",  "color" : "#66ff33" },
        { "code": "spac", "name": "South Pacific",  "color" : "#ffff66" },
        { "code": "natl", "name": "North Atlantic", "color" : "#ccff66" },
        { "code": "satl", "name": "South Atlantic", "color" : "#ccffcc" },
        { "code": "indn", "name": "Indian Ocean",   "color" : "#ff9900" },
        { "code": "land", "name": "Land",           "color" : "#000000" },
    ]
    if lat >=60:
        rv = 0 # "artc"
    elif lat <= -60:
        rv = 1 # "sthn"
    elif lat < 12 and lon < -70:
        rv = 3 # "spac"
    elif 135 <= lon <= 180 and lat < -15:
        rv = 3 # "spac"
    elif lat < 12 and -70 < lon < 20:
        rv = 5 # "satl"
    elif lat >= 12 and -180 <= lon <= -100:
        rv = 2 # "npac"
    elif lat >=12 and -115 <= lon <= 20:
        rv = 4 # "natl"
    elif lat <= 30 and 20 <= lon <= 105:
        rv = 6 # "indn"
    elif 105 <= lon < 145 and lat < 0:
        rv = 6 # "indn"
    elif 12 <= lat <= 15 and -180 <= lon <= -83:
        rv = 2 # "npac"
    elif 105 <= lon <= 180 and lat >= -15:
        rv = 2 # "npac"
    else:
        rv = 7 # "land"
    print(rv,lat,lon)
    return oceanColorList[rv]

if __name__ == "__main__":
    main()