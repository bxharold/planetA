#!/usr/local/bin/python3
#  dbquakes4planet.py:  Create tables for PlanetA Flask web app.
#  Command-line utility. Edits querystring to set date range, grabs USGS data.
#  Parses the JSON response, and creates a new table in quakes.db 
#  argv[1], argv[2] are startdate, enddate (resp.)
#  argv[3] names the table to be created in quakes.db 
#  CS50p/pytest changes tagged by REFACTORED_TO_project_py__  Code "moved" to project.py

querystring = "https://earthquake.usgs.gov/fdsnws/event/1/query.geojson?starttime=2023-01-20%2000:00:00&endtime=2023-03-21%2023:59:59&minmagnitude=4.5&orderby=time"

import json, requests, re, sys
import sqlite3
from sqlite3 import Error
from datetime import datetime
from project import num_quakes, create_connection, validCommandLine   # CS50p/pytest change.

# # get startdate, enddate, table_name from command; confirm valid
startdate = "2023-03-20"
enddate = "2023-03-21"
table_name = "newquakes000"

def REFACTORED_TO_project_py__validCommandLine(startdate, enddate, table_name):
    # x = re.findall(r"^20\d\d-\d\d-\d\d$", startdate)
    # if  not x:
    #     return "Invalid startdate"
    rv = 0
    #if not (g := re.findall(r"^20\d\d-(\d\d)-(\d\d)$", startdate) ):
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

def REFACTORED_TO_project_py__create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn

def f(x):
    x = datetime.utcfromtimestamp(x/1000).strftime('%Y-%m-%d %H:%M:%S')
    return x

def REFACTORED_TO_project_py__num_quakes(conn, table):
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) as numQuakes FROM {table}")
    rows = cur.fetchall()
    # for row in rows:
    #     print("Take your pick: ", rows[0][0], rows, row[0] )
    return rows[0][0]

def load_quakes_from_USGS_API(conn, table, querystring, verbose=False):
    if verbose:
        print(querystring)
     # !! TABLE IS MODIFIED, NOT REPLACED
    co=0
    response = requests.get(querystring)  # "Do. Or do not. There is no try." 
    with response:
        j = json.loads(response.text)
        for jk in j['features']:
            tim = jk['properties']['time']
            loc = jk['properties']['place']
            lat = jk['geometry']['coordinates'][1]
            lon = jk['geometry']['coordinates'][0]
            mag = jk['properties']['mag']
            dep = jk['geometry']['coordinates'][2]
            q = f"insert into {table} (tim,mag,lat,lon,dep,loc) " 
            q = q + f" values ({tim}, {mag}, {lat}, {lon}, {dep}, \"{loc}\" )"
            if verbose:
                print("insert = ", q)
            conn.execute(q)
            co=co+1
        conn.commit()
    return co

def dropTableStmt(table_name):
    return f"DROP TABLE IF EXISTS '{table_name}';"

def createTableStmt(table_name):
    return f"""
    CREATE TABLE IF NOT EXISTS "{table_name}" ( 
        id INTEGER PRIMARY KEY,
        tim INTEGER, 
        mag REAL,
        lat REAL,
        lon REAL,
        dep REAL,
        loc TEXT
    );
    """

def main():
    if len(sys.argv) != 4:
        sys.exit("Require 3 args -- startdate  enddate table_name")
    [startdate, enddate, table_name]  = [sys.argv[1], sys.argv[2], sys.argv[3]]
    x = validCommandLine(startdate, enddate, table_name)
    if x != 0:
        usage = f"Usage: {sys.argv[0]} startdate  enddate table_name\n"
        usage += "Date format is yyyy-mm-dd  Table name matches ^[a-zA-Z_]{2}[0-9_]+$\n"
        usage += f"E.g., ./dbquakes4planet.py  2022-07-04 2022-07-05  xx_12345"
        sys.exit(f"{usage}\nAbandon ship.")
    else:
        querystring = createQueryString(startdate, enddate)
        print("===> API request: ", querystring)
        database = "quakes.db"         
        conn = create_connection(database)
        cur = conn.cursor()
        sqlDropStmt = dropTableStmt(table_name)
        print(sqlDropStmt)
        sqlCreateTableStmt = createTableStmt(table_name)
        print(sqlCreateTableStmt)
        cur.execute(sqlDropStmt)
        cur.execute(sqlCreateTableStmt)
        load_quakes_from_USGS_API(conn, table_name, querystring)
        print(f"{num_quakes(conn, table_name)} rows inserted into {database}:{table_name} ")
        sys.exit("ok")

if __name__ == '__main__':
    main()

"""
CREATE TABLE IF NOT EXISTS "{table_name}" ( 
    id INTEGER PRIMARY KEY,
    tim INTEGER,  --  1679431761328 is ms; 1679431761 is sec.  
    --  usage: SELECT datetime(1679431761328 / 1000, 'unixepoch');  
    --  https://www.sqlite.org/lang_datefunc.html
    mag REAL,
    lat REAL,
    lon REAL,
    dep REAL,
    loc TEXT
);
"""
# END dbquakes4planet.py   ---o---     
