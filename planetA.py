#!/usr/local/bin/python3
# planetA.py  is a full-stack Flask app.  I'll let Chat-GPT write a full blurb.
#    66planetA is the session version that worked on mac but glitched on rpi.
#    egrep -n "^@ap|^def" planetA.py > defs
#    7/25/2023, reordering functions before printing. 
#    dropping post route in index.
#    removed param name=session['name'], passed to greet -- ??
#    found typo (acivetable), reordered
#
# The project planetA has 3 compomnents: earthquake display, ISS tracker,
# and a data aggregator utility "dbquakes4planet.py"
# The display for earthquakes and ISS is an HTML canvas.

# Earthquake visualizer:
# This displays locations, magnitudes, and time intervals of a set of earthquakes.
# "dbquakes4planet.py" retrieves earthquake data extracts from USGS, and stores
# the info (with additional calculated columns) in a sqlite database "quakes.db".

# In the browser, I use javascript to scale and schedule the animation,
# based on the time difference between successive earthquake events.

# The /loadActiveQuakeTable route retrieves the earthquake events from the
# local backend, and returns a JSON response. The browser intializes a global
# javascript object with this, and getJSON's the /loadActiveQuakeTableParams
# route to returns parameters that govern the display.

# ISS Tracker:
# This displays the location of the International Space Station.
#
# The route /issdata accesses the api.open-notify.org/iss-now.json API which
# provides the latitude/longitude. It then uses the nominatim API for
# reverse geolocation, which maps lat/lon to a country or ocean. I added
# a route to drill down to (approx) the specific ocean.
#
# Development Notes:
# ISS Tracker was written to better familiarize myself with the Flask API
# programming model (consuming and creating APIs.)  The animation requirements
# were quite simple: Every 5 seconds, get a location, draw a dot, repeat.
# HTML canvas and javascript's setInterval() were very appropriate for the
# realtime display updates.

# Earthquakes added a backend database, and more API endpoints. Animation
# was more complicated -- I wanted an explicit "delay" in javascript that
# enabled the DOM updates to occur within a javascript loop. I used the
# async/await/promise approach for this.

# 7/7/2023: Animation is working. Scaled deltat is now wired in.
# Can't switch between worldi and worldq images yet. The names are in a static file.
# I have to set the localhost port from hard-coded 5000 to QPORT manually in both planetA.py and planetjs.js

# cat ../planetA.py ../static/planetjs.js layout.html index.html greet.html isschart.html quakechart.html kwaks.html 
# quakedata.html oceans.html ../whereisthis.py ../dbquakes4planet.py ../issrecorder.py ../Planetnotes.txt > ../spoo721

from flask import Flask, jsonify, render_template, request, redirect, session, url_for, flash
import sqlite3
from sqlite3 import Error
import datetime, json, requests, os, subprocess, time, re, random
from geopy.geocoders import Nominatim

app = Flask(__name__)
app.secret_key = "any random string"
worldmap = 'worldi'

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn

def niceDate(ts):
    return datetime.datetime.utcfromtimestamp(ts).strftime('%H:%M:%S')

def f(x):
    x = datetime.datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S')
    return x

def cpu_util():
  cpu_util_cmd = "ps -A -o %cpu | awk '{s+=$1} END {print s \"%\"}'"
  dev = os.popen(cpu_util_cmd)
  cpu_util_raw = dev.read()
  return cpu_util_raw.strip()

def cpu_temp(vhostname):
    if vhostname != "HiMac2.local":
        dev = os.popen('/opt/vc/bin/vcgencmd measure_temp')
        cpu_temp_raw = dev.read()[5:-3]
        return cpu_temp_raw.strip()
    else:
        return "n/a on Mac"

def hostname():
  dev = os.popen("hostname")
  hn = dev.read()
  return hn.strip()

def countstar(table):
    try:
        conn = create_connection(session['database'])
        cursor = conn.cursor()
        # sql = f"SELECT count() FROM '{table}';"
        cursor.execute( "SELECT count() FROM ?;", table)
        rv = cursor.fetchone()
        rv = rv[0]
    except sqlite3.Error as error:
        print(f"Failed to execute countstar", error)
    finally:
        if conn:
            conn.close()
    return rv

def listTables():
    print("listTables --- ", session)
    try:
        conn = create_connection(session['database'])
        sql_query = """SELECT name FROM sqlite_master WHERE type='table';"""  #     gotta block isspath
        print(session['database'], sql_query)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        print( f"List of tables in {session['database']}")
        rva = cursor.fetchall()
        rv = []
        for item in rva:
            rv.append(item[0])
        print(rv)
    except sqlite3.Error as error:
        print("Failed to execute the sqlite_master query", error)
    finally:
        if conn:
            conn.close()
    return rv


#############  index, sessions  #############################################

@app.route("/")
def index():
    # print("index")
    # session['database'] = "quakes.db"
    # session['activetable'] = "colortest"
    # session['name'] = ""
    # session['note'] = ""
    # session.modified = True
    # return render_template("index.html")
    return redirect('/clearsession')

@app.route("/greet", methods=["GET"])
def greet():
    name=request.args['name']
    clearsession()     # ???
    session['name'] = name if len(name) > 0 else "Guest"
    note = f"new session for {session['name']} at {datetime.datetime.now().strftime('%X')}"
    session['note'] = note
    session.modified = True
    return render_template("greet.html", note=note)

@app.route("/clearsession", methods=["GET", "POST"])
def clearsession():
    session['name'] = ""
    session['note'] = ""
    session['database'] = "quakes.db"
    session['activetable'] = ""
    session.modified = True
    return render_template("index.html")
    # return redirect('/')

@app.route("/table", methods=["GET"])
def table():
    session['activetable'] = request.args['t']
    session.modified = True
    return render_template("index.html")
    # return redirect('/')

#############  iss   ###################################################

@app.route("/issdata", methods=["GET"])
def issdata():
    dtime = datetime.datetime.now().strftime("%x %a %H:%M:%S.%f")
    obj = requests.get("http://api.open-notify.org/iss-now.json")
    oj = obj.json()   # <class 'dict'> -- so I can add to it.
    oj["nicedate"] = niceDate(oj['timestamp'])
    vhostname = hostname()
    oj['temperature'] = cpu_temp(vhostname)
    oj['hostname'] = vhostname
    oj['utilization'] = cpu_util()
    ojlat = oj['iss_position']['latitude']
    ojlon = oj['iss_position']['longitude']
    oj['geolocation'] = get_nearest_location(ojlat,ojlon)
    oj = jsonify(oj)
    oj.headers.add('Access-Control-Allow-Origin', '*')
    return oj

@app.route("/isschart", methods=["GET"])
def isschart():
    msg = "ISS location, real-time updates with reverse geolocation information."
    obj = requests.get("http://api.open-notify.org/iss-now.json")
    oj = obj.json()   # <class 'dict'> -- so I can add to it.
    oj["nicedate"] = niceDate(oj['timestamp'])
    ojlat = oj['iss_position']['latitude']
    ojlon = oj['iss_position']['longitude']
    ojloc = get_nearest_location(ojlat,ojlon)
    print("isschart", ojlat, ojlon, ojloc)
    oj['geolocation'] = ojloc
    print (oj['timestamp'])
    print (oj['nicedate'])
    print (oj['iss_position']['latitude'], oj['iss_position']['longitude'])
    return render_template("isschart.html", msg=msg, img=worldmap,
                name=session['name'], note=session['note'], oj=oj)

#############  quakes  ###################################################

@app.route("/deltat", methods=["GET"])   # route is only used in dev
def deltat():         # code is inline in get_quakedata()
    qid = request.args['qid']
    dt = -1
    if qid == 1:
        return 100
    try:
        conn = create_connection(session['database'])
        sql = f"SELECT tim FROM '{session['activetable']}' where id = {qid}"
        cursor = conn.cursor()
        cursor.execute(sql)
        rv = cursor.fetchone()
        cur = rv[0]
        sql = f"SELECT tim FROM '{session['activetable']}' where id = {int(qid) -1}"
        cursor = conn.cursor()
        cursor.execute(sql)
        rv = cursor.fetchone()
        prev = rv[0]
        dt = (prev - cur ) /1000
    except sqlite3.Error as error:
        print(f"Failed to execute {sql}", error)
    finally:
        if conn:
            conn.close()
    dt = jsonify( (dt,) )
    dt.headers.add('Access-Control-Allow-Origin', '*')
    return dt

@app.route("/qeventdata", methods=["GET"])
def qeventdata():           # For unit test. Return one row of the unaugmented table
    q = request.args['q']   # http://127.0.0.1:5000/qeventdata?q=19
    try:
        q = int(q)
    except:
        print("ValueError -- send a flash?")
        q = 0
    qdata = get_quakedata()   # list of tuple
    if q >= len(qdata) or q < 0:
        print(f"index {q} out of bounds, returning first tuple")
        q = 0
    t = qdata[q]  # tuple
    oj = {}
    oj["id"] = t[0]
    oj["magn"] = t[2]
    oj["lat"] = t[3]
    oj["lon"] = t[4]
    oj["date"] = t[7]
    oj["deltat"] = t[8]
    oj["loc"] = t[6]
    oj["activetable"] = session['activetable']
    oj["activetablesize"] = len(qdata)
    oj = jsonify(oj)
    oj.headers.add('Access-Control-Allow-Origin', '*')
    return oj

@app.route("/loadActiveQuakeTable", methods=["GET"])
def loadActiveQuakeTable():
    tablename = request.args['tablename']  #  sanitize
    x = re.search("[^a-zA-Z0-9_]", tablename )
    if x is not None:
        tablename = "dummy"   # Q&D
    session['activetable'] = tablename
    session.modified = True
    rowsplus = get_quakedata()      # rowsplus is a list
    jrowsplus = jsonify(rowsplus)   # jrowsplus is a flask response
    jrowsplus.headers.add('Access-Control-Allow-Origin', '*')
    return jrowsplus

@app.route("/loadActiveQuakeTableParams", methods=["GET"])
def loadActiveQuakeTableParams():
    # kw = kwakParams(request.args['tablename'])
    kw = kwakParams( session['activetable'])   # kw is a dict
    jkw = jsonify(kw)        # jkw is a flask.wrappers.Response
    jkw.headers.add('Access-Control-Allow-Origin', '*')
    return jkw

@app.route("/kwaks", methods=["GET"])
def kwaks():
    msg = "Use external app dbquakes4planet.py to create additonal tables. "
    kwaktables = listTables()
    kwaktables.insert(0,"Select...")
    return render_template("kwaks.html", msg=msg, kwaktables=kwaktables, img='worldq')

@app.route("/quakedata", methods=["GET", "POST"])
def quakedata():
    if session['activetable'] == "":
        msg="Select a table. "
        flash(f"{msg}")
        return redirect('/kwaks')
    else:
        rowsplus = get_quakedata()
        msg = "USGS earthquake data with added date/time and Delta-T columns. \
            Parsed geojson data stored locally in sqlite: "
        # the row indices in the response depend on the ordering.  IDs are 15,16.
        # flash(f"quakedata: {session['activetable']}") # flash is more trouble than it's worth
        return render_template("quakedata.html", msg=msg, rows=rowsplus, img='worldq')

def kwakParams(table):  # returns dict.
    try:
        kw = {}
        print("kwakParams ---", session)
        conn = create_connection(session['database'])
        sql = f"SELECT min(tim) as timmin, max(tim) as timmax, max(tim)-min(tim) as timdiff, \
            min(tim) as timminT, max(tim) as timmaxT FROM '{table}';"
        cursor = conn.cursor()
        cursor.execute(sql)
        rv = cursor.fetchone()
        rv = list(rv)
        rv = list(map(lambda x: round(x/1000), rv))
        kw["timmin"] = rv[0]
        kw["timmax"] = rv[1]
        kw["timdiff"] = rv[2]
        kw["timminPP"] = f(rv[0])
        kw["timmaxPP"] = f(rv[1])
        # get count here
        sql = f"SELECT count(*) FROM '{table}';"
        cursor = conn.cursor()
        cursor.execute(sql)
        rv = cursor.fetchone()
        kw["rowCount"] = rv[0]
        kw["database"] = f"{session['database']}"
        kw["activetable"] = table
        session['activetable'] = table
        session.modified = True
        print("kwakParams kw dict", kw)
    except sqlite3.Error as error:
        print(f"kwakParams Failed to execute {sql}", error)
    finally:
        if conn:
            conn.close()
    return kw

def get_quakedata():     # used by routes /quakedata and /get_quakedata_limit_2
    # returns a full augmented table
    print(f"{session['database']} / {session['activetable']}")
    dbconn = create_connection(session['database'])
    cur = dbconn.cursor()
    cur.execute(f"SELECT * FROM '{session['activetable']}' ORDER BY tim DESC")  # tim is in msec
    # id  TimeStamp  Magnitude  Latitude  Lon  Depth  Location
    rowsplus = []   # used for augmented rows
    firstRow, prevt = True, -1
    for row in cur:
        # append column: formatted date
        y = ( f(int(row[1]/1000)), )   # timestamp is in milliseconds
        # append columns:  seconds since previous quake
        # Don't forget to adjust the template's table's counter
        currt = int(row[1])
        if firstRow:
            prevt = currt
            firstRow = False
        dt = int((currt - prevt) / 1000)
        prevt = currt
        delta = ( -dt, )
        hms = ( niceDate(-dt), )  ## more readable for large intervals.
        rowsplus.append(row + y + delta + hms)
    return rowsplus

@app.route("/get_quakedata_JSON", methods=["GET"])  # used for development
def get_quakedata_JSON():
    rowsplus = get_quakedata()
    # print(type(rowsplus))      # <class 'list'>   actually, a list of tuple
    # print(type(rowsplus[0]))   # <class 'tuple'>
    oj = jsonify(rowsplus)     # <class 'flask.wrappers.Response'>
    oj.headers.add('Access-Control-Allow-Origin', '*')
    return oj

@app.route("/get_isspath_JSON", methods=["GET"])  # used for development
def get_isspath_JSON():
    isspath = get_isspath()
    oj = jsonify(isspath)     # <class 'flask.wrappers.Response'>
    oj.headers.add('Access-Control-Allow-Origin', '*')
    return oj

def get_isspath():
    dbconn = create_connection(session['database'])
    cur = dbconn.cursor()
    cur.execute(f"SELECT * FROM 'isspath' ORDER BY rowid")
    # rowid  tim lat lon nicedate loc
    # rowsplus = []   # # srsly?
    # for row in cur:
    #     rowsplus.append(row)
    rowsplus = cur.fetchall()
    return rowsplus

#############  ocean, geo  #################################################

def get_nearest_location(latitude, longitude):
    # return country, US state, or ocean color associated w/ lat,lon
    try:
        geolocator = Nominatim(user_agent="CS50p PlanetA")
        location = geolocator.reverse(f"{latitude}, {longitude}")
    except:
        print ("geolocator try failed")
        nearest_location = f"{latitude}, {longitude}"
    else:
        if location:
            print(f"we have a location...{location.raw}")
            if location.raw["address"]["country_code"] == 'us':
                nearest_location = location.raw["address"]["state"]
            else:
                nearest_location = location.raw["address"]["country"]
            nearest_loc = {}
            nearest_loc['code'] = "land"
            nearest_loc['name'] = nearest_location
            nearest_loc['color'] = ""#00ff00""
            nearest_location = nearest_loc
        else:  # assume ocean
            nearest_location = oceancolormap(latitude,longitude)
            #  { "code": "artc", "name": "Arctic Ocean",   "color" : "#ccccff" },
    finally:
        print(f"nearest_location={nearest_location}")
    return nearest_location

@app.route("/oceancolor", methods=["GET"]) # map ocean lat,lon to color
def oceancolor(): # http://127.0.0.1:5000/oceancolor?lat=10&lon=20
    #            return { "code":"indn", "color":"#ff9900","name":"Indian" }
    lat=request.args['lat']
    lon=request.args['lon']
    col =  oceancolormap(lat,lon)
    dj = jsonify(col)
    dj.headers.add('Access-Control-Allow-Origin', '*')
    return dj

def validLatLon(x):  # return 0 if not a float; no test for -180<=x<=180
    try:
        return float(x)
    except ValueError:
        return None

@app.route("/revgeo", methods=["GET"])   # only used for testing
def revgeo():    #   return full JSON, or "NOWHERE" if not found
    # http://127.0.0.1:5000/revgeo?lat=33&lon=-117  (-127 is ocean, -117 is Encinitas)
    # http://127.0.0.1:5000/revgeo?lat=33.04&lon=-117.30
    lat=request.args['lat']
    lon=request.args['lon']
    lat,lon = validLatLon(lat), validLatLon(lon)
    if lat is None or lon is None:
        return "value error"
    try:
        geolocator = Nominatim(user_agent="CS50p PlanetA")
        location = geolocator.reverse(f"{lat}, {lon}")
        print(location)
    except:
        print ("geolocator try failed")
        nearest_location = f"{lat}, {lon}"
    else:
        if location:
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

@app.route("/oceans", methods=["GET"])
def oceans():
    msg = "This route is used to test reverse geolocation code for ocean locations."
    return render_template("oceans.html" , msg=msg, img='worldi')


if __name__ == "__main__":
    QPORT = 5055
    app.run(host="0.0.0.0", port=QPORT, debug=True)

# END planetA.py   ---o---     ---o---     ---o---     ---o---     ---o---
