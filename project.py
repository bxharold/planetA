# project.py   https://youtu.be/ZmAGIH3YjRY

def main():
    msg = """
My CS50p project consists of 2 components" planetA.py, a Flask app, and 
dbquakes4planet.py, a data retriever/aggregator. The cs50p reqts call for 
a pytest-testable "project.py" in a specific format. (See below.)

To that end, 3 functions in planetA.py (a Flask app), and dbquakes4planet.py 
have been copied here (project.py). In the "real" program files, their 
names have been prefixed with "REFACTORED_TO_project_py__" and the 
functions are imported from this "project.py" file.

My original view of this project was a web app, using Flask and Javascript,
to create an animated display of earthquakes.  Historical earthquake data is 
available, but for sanity's sake, I made a local copy (with added columns)
and that data drove the animation.  

But, rules as they are, the "project" needs a "main" and functions which 
can be pytest'ed.  Sad to say, even in my local environment, I couldn't 
get pytest to find the external libraries I used (geopy). Forget about 
trying to configure my environment under CS50p's Docker! 

Functionally, this "project.py" is a place to put some utility functions.
PlanetA.py and dbquakes4planet.py are still the real project. They can
both import the 3 functions here, and they can all run as designed.

    """
    print(msg)

"""
project.py:def main():
project.py:def oceancolormap(lat,lon):
project.py:def validCommandLine(startdate, enddate, table_name):
project.py:def createQueryString(startdate, enddate):
project.py:def create_connection(db_file):
project.py:def num_quakes(conn, table):

test_project.py:def test_num_quakes():
test_project.py:def test_oceancolormap():
test_project.py:def test_validCommandLine():

dbquakes4planet.py:def REFACTORED_TO_project_py__validCommandLine(startdate, enddate, table_name):
dbquakes4planet.py:def createQueryString(startdate, enddate):
dbquakes4planet.py:def create_connection(db_file):
dbquakes4planet.py:def f(x):
dbquakes4planet.py:def REFACTORED_TO_project_py__num_quakes(conn, table):
dbquakes4planet.py:def load_quakes_from_USGS_API(conn, table, querystring, verbose=False):
dbquakes4planet.py:def dropTableStmt(table_name):
dbquakes4planet.py:def createTableStmt(table_name):
dbquakes4planet.py:def main():
"""

"""
Your project must have a main function and three or more additional functions. At least three of those additional functions must be accompanied by tests that can be executed with pytest.

Your main function must be in a file called project.py, which should be in the “root” (i.e., top-level folder) of your project.

Your 3 required custom functions other than main must also be in project.py and defined at the same indentation level as main (i.e., not nested under any classes or functions).

Your test functions must be in a file called test_project.py, which should also be in the “root” of your project. Be sure they have the same name as your custom functions, prepended with test_ (test_custom_function, for example, where custom_function is a function you’ve implemented in project.py).

"""

import re
import sqlite3
from sqlite3 import Error


#   from planetA.py
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

# from dbquakes4planet.py
def validCommandLine(startdate, enddate, table_name):
    rv = 0
    g = re.findall(r"^20\d\d-(\d\d)-(\d\d)$", startdate)
    if not g:
        print(f"Invalid startdate {startdate}")
        return 1
    if int(g[0][0]) < 1 or int(g[0][0])>12:
        print(f"Invalid start month {startdate}  { g[0][0] }")
        return 101
    if int(g[0][1]) < 1 or int(g[0][1])>31:
        print(f"Invalid start day of month {startdate}   { g[0][1] }")
        return 102

    g = re.findall(r"^20\d\d-(\d\d)-(\d\d)$", enddate)
    if not g:
        print(f"Invalid enddate {enddate}")
        return 2
    if int(g[0][0]) < 1 or int(g[0][0])>12:
        print(f"Invalid start month {enddate}  { g[0][0] }")
        return 201
    if int(g[0][1]) < 1 or int(g[0][1])>31:
        print(f"Invalid start day of month {enddate}   { g[0][1] }")
        return 202

    if not re.findall("^[a-zA-Z_]{2}[0-9_]+$", table_name):
        print(f"Table Name '{table_name}' is not to my liking.")
        return 3
    return 0

def createQueryString(startdate, enddate):
    return f"https://earthquake.usgs.gov/fdsnws/event/1/query.geojson?starttime={startdate}%2000:00:00&endtime={enddate}%2023:59:59&minmagnitude=4.5&orderby=time"

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn


def num_quakes(conn, table):
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) as numQuakes FROM {table}")
    rows = cur.fetchall()
    return rows[0][0]


if __name__ == "__main__":
    main()

