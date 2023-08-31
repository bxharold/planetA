# Project:  planetA  
## Full-stack Flask app using Python, Sqlite, Javascript

### External APIs:  USGS, ISS, Nominatim
  *   open-notify.org      for realtime ISS location
  *   earthquake.usgs.gov  for earthquake data
  *   Nominatim            library for reverse geolocation

## planetA has 3 components: 
- earthquake sequence visualization, 
- ISS tracker, 
- a data aggregator utility "dbquakes4planet.py"
- The display for earthquakes and ISS is an HTML5 canvas.

## Earthquake visualizer:

The browser front-end  displays locations, magnitudes, and time intervals of a set of earthquakes.
A separate app, "dbquakes4planet.py", retrieves earthquake data extracts from USGS (JSON) and stores the info (with additional calculated columns) in a sqlite database "quakes.db".

In the browser, I use javascript to scale and schedule the animation,
based on the time difference between successive earthquake events.

The /loadActiveQuakeTable route retrieves the earthquake events from the
local backend, and returns a JSON response. The browser intializes a global
javascript object with this, and getJSON's the /loadActiveQuakeTableParams
route to return parameters that govern the display.

## ISS Tracker:

This displays the location of the International Space Station in real time.

The route /issdata accesses the api.open-notify.org/iss-now.json API which
provides the latitude/longitude. It then uses the nominatim API for
reverse geolocation, mapping lat/lon coords to a country or ocean. I added
a route to drill down to (approx) the specific ocean.

## Development Notes:

The javascript animation requirements for ISS Tracker
were quite simple: Every 5 seconds, get a location, draw a dot, repeat.
HTML canvas and javascript's setInterval() were very appropriate for the
realtime display updates.

For the earthquakes, I added a backend database, which I populated off-line.
The rationale for off-line is two-fold:  (1) the data is historical and nearly static
(although magnitudes and depths can be revised), and (2) I'm doing this project 
as an exercise in Flask, SQlite, JSON, and writing REST API endpoints. Not in web UI.

This animation in javascript was more complicated than I expected, not as 
trivial as the "setTimeout()" that I used for ISS Tracker.
I wanted an explicit "delay" in the javascript loop that generated a sequence
of DOM updates, drawing a programmatically-determined-sized dot on the canvas 
and updating text areas with a delay time based on a call to a route that 
I defined in planetA.py. 
Javascript's async/await/promise approach turned out to be appropriate for this.

## My motivation for this particular project:
For the record, this is my final project for CS50p. I first stumbled 
onto CS50 when I was building a browser-based front-end controller
for an Arduino project. After watching the CS50 lecture 9 on Flask/Jinja2,
I enrolled in CS50, and then CS50p.  It seemed "poetic" for my
final project to be a full-stack app.

I wrote ISS Tracker to get more practice in Flask/Python web development
and the REST API programming model (consuming and writing API endpointss.)

I wrote the Quakes component because I wanted to "watch" the progression
of earthquakes in condensed time.

## In hindsight:

1. I spent way more time with javascript than I expected.

1. "Problems worthy of attack prove their worth by fighting back." (Piet Hein,
creator of the Soma puzzle).
So, for a self-designed learning project, I'd say this was good.  

1. This was a good excuse to finally learn how to use Git and GitHub.

1. I should've used python virtual environments...  I had a reason to install Python 3.11 on my dev Mac, but I regret it now.  


# Notes:
- 66planetA is the session version that worked on mac but glitched on rpi.
- egrep -n "^@ap|^def" planetA.py > defs
- 7/25/2023, reordering functions before printing.
   dropping post route in index.
   removed param name=session['name'], passed to greet -- ??
   found typo (acivetable), reordered
- 8/30/2023, posting to github, preparing for sadness as I try to port this to a Raspberry Pi that has none of the libraries installed, and is running Python 3.7, not 3.11
- to preview markdown in vscode:  split editor for side-by-side.  That's all.

this is a normal line of text
  * this is the first level of bullet points, made up of <space><space>*<space>
    * this is more indented, composed of <space><space><space><space>*<space>