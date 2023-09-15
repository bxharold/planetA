#!/usr/local/bin/python3
# planetA.py  CS50p final project. Full-stack Flask app.  See README.md

from flask import Flask, jsonify, render_template, request, redirect, session, url_for, flash
import sqlite3
from sqlite3 import Error
import datetime, json, requests, os, subprocess, time, re, random, sys, socket
from geopy.geocoders import Nominatim
from project import oceancolormap  # CS50p/pytest change.

app = Flask(__name__)
app.secret_key = "any random string"
worldmap = 'worldi'

def hostIP():
  hn = ([l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0])
  print("one-liner: ", hn)  # food for thought!
  return hn

# running locally, 
host_ip = hostIP()
QPORT = f"http://{host_ip}:5000/"
# on CS50's Docker, I have to specify QPORT explicitly:
# QPORT = "https://bxharold-code50-28027098-gxw7wp4pgvw2ppq5.github.dev/"


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

def listTables():
    print("listTables --- ", session)
    try:
        conn = create_connection(session['database'])
        sql_query = """SELECT name FROM sqlite_master WHERE type='table' AND name not like 'isspath';"""  
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

@app.route("/readme", methods=["GET"])
def readme():
    return render_template("README.md")



#############  index, sessions  #############################################

@app.route("/")
def index():
    # QPORT = f"http://{request.headers.get('Host')}"
    return redirect('/clearsession')

@app.route("/greet", methods=["GET"])
def greet():
    name=request.args['name']
    clearsession()     # ???
    session['name'] = name if len(name) > 0 else "Guest"
    note = f"new session for {session['name']} at {datetime.datetime.now().strftime('%X')}"
    session['note'] = note
    session.modified = True
    # QPORT = f"http://{request.headers.get('Host')}"
    return render_template("greet.html", note=note, QPORT=QPORT)

@app.route("/clearsession", methods=["GET", "POST"])
def clearsession():
    session['name'] = ""
    session['note'] = ""
    session['database'] = "quakes.db"
    session['activetable'] = ""
    session.modified = True
    # QPORT = f"http://{request.headers.get('Host')}"
    print(QPORT)
    return render_template("index.html", QPORT=QPORT)

@app.route("/table", methods=["GET"])
def table():
    session['activetable'] = request.args['t']
    session.modified = True
    # QPORT = f"http://{request.headers.get('Host')}"
    return render_template("index.html", QPORT=QPORT)
    # return redirect('/')

#############  iss   ###################################################

@app.route("/issdata", methods=["GET"])
def issdata():
    dtime = datetime.datetime.now().strftime("%x %a %H:%M:%S.%f")
    obj = requests.get("http://api.open-notify.org/iss-now.json")
    oj = obj.json()   # <class 'dict'> -- so I can add to it.
    oj["nicedate"] = niceDate(oj['timestamp'])
    vhostname = hostIP()  # hostname()
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
    # QPORT = f"http://{request.headers.get('Host')}"
    print(QPORT)
    return render_template("isschart.html", msg=msg, img=worldmap,
                name=session['name'], note=session['note'], oj=oj, QPORT=QPORT)

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
    # QPORT = f"http://{request.headers.get('Host')}"
    return render_template("kwaks.html", msg=msg, kwaktables=kwaktables, img='worldq', QPORT=QPORT)

@app.route("/quakedata", methods=["GET", "POST"])
def quakedata():
    if session['activetable'] == "":
        msg=">>> Select a table."
        flash(f"{msg}")
        return redirect('/kwaks')
    else:
        rowsplus = get_quakedata()
        msg = "USGS earthquake data with added date/time and Delta-T columns. \
            Parsed geojson data stored locally in sqlite: "
        # the row indices in the response depend on the ordering.  IDs are 15,16.
        # flash(f"quakedata: {session['activetable']}") # flash is more trouble than it's worth
        # QPORT = f"http://{request.headers.get('Host')}"
        return render_template("quakedata.html", msg=msg, rows=rowsplus, img='worldq', QPORT=QPORT)

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

def get_isspath():  # isspath-americas goes over the US and SA
    dbconn = create_connection(session['database'])
    cur = dbconn.cursor()
    cur.execute(f"SELECT * FROM 'isspath' ORDER BY rowid") 
    # rowid  tim lat lon nicedate loc
    rowsplus = cur.fetchall()
    return rowsplus

#############  ocean, geo  #################################################

def OLD_get_nearest_location(latitude, longitude):
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

def get_nearest_location(latitude, longitude):
    # return country, US state, or ocean associated w/ lat,lon
    nearest_location = ""
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
            print("==>",location.raw["address"]["town"],"<==")
            return location.raw
        else:
            return "NOWHERE"

def REFACTORED_TO_project_py__oceancolormap(lat,lon):
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
    # QPORT = f"http://{request.headers.get('Host')}"
    print(f"-->QPORT={QPORT}=")
    return render_template("oceans.html" , msg=msg, img='worldi', QPORT=QPORT)

if __name__ == "__main__":
    # if len(sys.argv) != 2:
    #     sys.exit(f"usage: {sys.argv[0]}  [port#]\n")
    # app.run(host="0.0.0.0", port=sys.argv[1], debug=True)
    # can't specify port in CS50 Docker; replace this with
    app.run(host="0.0.0.0", port=5000, debug=True)

# END planetA.py   ---o---     ---o---     ---o---     ---o---     ---o---
