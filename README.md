# Project:  PlanetA  
#### Video Demo:  <URL HERE>
#### Description: `PlanetA` is a full-stack Flask app that uses Python, Sqlite and Javascript to implement a browser-based graphical display that shows, in compressed time, the locations and relative magnitudes of earthquakes.  It also has the option to display the path (in real time) of the International Space Station (ISS). 

## PlanetA has 3 components: 
  1. Earthquake sequence visualization 
  1. ISS tracker 
     - The display for earthquakes and ISS is Web browser and an HTML5 canvas.
  1. A data aggregator utility `dbquakes4planet.py`
     - command-line program generating Sqlite tables for the earthquake sequence visualization component

## USGS earthquake data aggregator:
`dbquakes4planet.py` is a command-line program that pulls earthquake event data within a specified data range from the online USGS database. It stores extracts (with additional calculated columns to handle the earthquake animation) in tables in a local Sqlite database `quakes.db`.

## Earthquake visualizer:
The browser front-end displays an animation of locations, magnitudes, and time intervals of a set of earthquakes. The UI presents a pulldown list of all available tables that were created by the earthquake data aggregator app, `dbquakes4planet.py`.

In the browser, I use the javascript async/await/promise approach to schedule the steps if the animation, based on the time difference between successive earthquake events.
I use an HTML5 canvas for the visual display, with a background image that shows, for reference, tectonic plate boundaries.

The `/loadActiveQuakeTable` route retrieves the earthquake events from the
local backend Sqlite database, and returns this as a JSON response to the browser. The browser intializes a global javascript object with this, and getJSON's 
the `/loadActiveQuakeTableParams`
route to return parameters that govern the display.

## ISS Tracker:
This displays the location of the International Space Station in real time, with an update every 5 seconds.

The route /issdata accesses the api.open-notify.org/iss-now.json API which
provides the latitude/longitude. It then uses the nominatim API for
reverse geolocation, mapping lat/lon coords to a country or ocean. I added
a route to drill down to (approx) the specific ocean. 

## External APIs:  USGS, ISS, Nominatim
  *   open-notify.org      for realtime ISS location
  *   earthquake.usgs.gov  for earthquake data
  *   Nominatim            API and library for reverse geolocation

## Files:
  - planetA.py
  - dbquakes4planet.py
  - project.py
  - quakes.db
  - issrecorder.py
  - isspath-americas.csv
  - static/planetstyle.css
  - static/planetjs.js
  - static/landocean.jpg
  - static/blueplates.jpg
  - static/whitegray.jpg
  - static/grayplates.jpg
  - templates/footer.html
  - templates/greet.html
  - templates/index.html
  - templates/isschart.html
  - templates/kwaks.html
  - templates/layout.html
  - templates/oceans.html
  - templates/quakechart.html
  - templates/quakedata.html

# Development Notes:

The realtime ISS location data comes from the open-notify.org JSON API. 

The javascript animation for ISS Tracker is quite simple: 
Every 5 seconds, get a location, draw a dot, repeat. HTML canvas and javascript's 
setInterval() were appropriate for the realtime display updates.

For the earthquake data, I used a local backend database which I populated off-line 
from the USGS earthquake JSON API. For each date range (specified as command-line
parameters to `dbquakes4planet.py`), I create a separate table, with added 
calculated columns to simplify the animation display.  This list of tables
is presented in the "Earthquake Sequencer" tab as a selection list.

The earthquakes animation in javascript was not as trivial as the "setTimeout()" 
that I used for ISS Tracker. I wanted an explicit "delay" in the javascript loop 
that generated a sequence of DOM updates, drawing a programmatically-determined-sized 
dot on the canvas and updating text areas with a delay time based on a call to a route 
that I defined in planetA.py. I used Javascript's async/await/promise approach for this.

## My motivation for this particular project:
Some background: I first stumbled onto CS50 a year ago when I was building a browser-based front-end controller for an Arduino/Raspberry PI project. 
I had decided to use a REST framework, 
but I had very little experience with REST APIs.  After watching the CS50
lecture 9 on Flask/Jinja2, I backtracked, completed CS50, and then enrolled in CS50p. 
It seemed "natural" for my CS50p final project to be a full-stack Flask app. 

### Why earthquakes?
My interest in watching the progression of earthquakes in condensed time 
started with a display at the Yellowstone Visitor Center, a globe with
blinking lights. I decided the CS50p final project provided a good excuse to
build a web version. 

## Implementation Stages:
### A first step:
I wrote the ISS Tracker component as a "Hello, World" to get more practice in 
Flask/Python web development and the REST API programming model (consuming 
and writing API endpoints.) The tracker called the /isspath route, which
in turn retrieved the JSON from the open-notify.org API. At this point, the 
/isspath did not include the reverse geolocation functionality.
The animation just used a simple javascript setTimeout() loop.  

### Working with the local backend database
The next steps were to build the earthquake data aggregator app, `dbquakes4planet.py`,
store a few tables, build the web UI that enabled selecting the table and displaying
the data on a web page. The UI is under the "Earthquake Sequencer" tab, which goes to
the /kwaks route. The "Raw Earthquake Data" link, which goes to the /quakedata route,
displays the selected table's data.

### Developing the canvas animation:
At its core, my animation, or sequential updating of the canvas, is `repeat {draw; delay}`. Javascript has no built-in "delay". The async await/promise model that could
implement a delay was new to me, and so I added a simple "demo" mode to
ISS Tracker. This is implemented in the route /get_isspath_JSON.

### Displaying the earthquakes
Combining these steps, I built the display for the earthquakes. The plan was
to iterate over the table, and draw a dot after waiting for an amount of time
proportional to the difference in time between events. The async await/promise 
model gave me the "delay" functionality.

### How to highlight the last dot drawn? 
Essentially, for the N^th^ quake in my table, I wanted to draw the first N-1 dots in black, and then the N^th^ in red.
In the Processing environment (which is optimized for graphics displays), I could loop over N (the number of quakes), 
and refresh the entire image at each iteration. That is not feasible with a browser canvas. 

The solution was in a lyric to a Rolling Stones song that I had heard a day earlier:

  -  *I see a red dot and I want it painted black.* 

I.e., for every new quake, repaint the previous dot black, then paint the new quake red.  

### Adding reverse geolocation:
I wanted the ISS Tracker to display the geographic location in addition to the
latitude and longitude, similar to the earthquake feed. To do this, in the
/issdata route, I took the ISS location (http://api.open-notify.org/iss-now.json)
lat/lon data, and appended the geolocation data from the Nominatim API library.

### Porting to a Raspberry Pi for testing
The Flask app is only known by its IP and port# (I have no local DNS.) 
I set a javascript vbl QPORT as a URI prefix (e.g., http://192.168.1.13:8787) 
To make my app IP- and port-independent, I specify the port as an arg when 
I start the Flask server. I let Python build the rest of the protocol-ip-port 
string, and I pass that (via render_template) to each page that contains 
javascript to do getJSON() requests back to routes in the Flask app. 
(I do this once, in layout.html) 
To make the vbl QPORT accessible in javascript, I use a script in the page body:
  - `<script> QPORT="{{QPORT|safe}}"</script>`


## In hindsight:
1. I spent way more time with javascript than I expected.
    -  Graphics was easy; animation harder.
    -  This was a good exercise in flask/js 2-way communication.
2. To quote Piet Hein, creator of the Soma puzzle, "Problems worthy of attack prove their worth by fighting back."  I intentionally designed this to be a learning project, and I can confidentally say that it proved its worth.  
3. This was a good excuse to finally learn how to use Git and GitHub.
4. I should've used python virtual environments earlier on... ☹️
   
 
#   ^^^^^^^^^^^^^^^^^    CUT HERE   ^^^^^^^^^^^^^^^^^^^^^
# Notes:
- 7/25/2023, reordering functions before printing.
     -  dropping post route in index.
     -  removed param name=session['name'], passed to greet -- ??
     -  found typo (acivetable), reordered
- 8/30/2023, preparing for sadness as I try to port this to a Raspberry Pi that has none of the libraries installed, and is running Python 3.7, not 3.11
- 8/31/2023~, moved to git and github. still using HiMac2:~/qvcs50p/planetA for pre-stagnig dev.  diff's to follow.
- 9/5/2023, specify port# on startup, and pass QPORT (http://IP:port) to javascript so it can refer back to the Flask app (which is only known by its IP and port.)
- The rationale for off-line is two-fold:  (1) the data is historical and nearly static
(although magnitudes and depths can be revised), and (2) I'm doing this project 
as an exercise in Flask, SQlite, JSON, and writing REST API endpoints. Not in web UI.
- removing this from oceans.html:
<pre>
    Notes:  The JS vbl QPORT is a URI prefix; e.g., http://192.168.1.13:8787  
    To make my app IP- and port-independent for testing on my Mac and Raspberry Pi, 
    I specify the port as an arg when I start the Flask server. I let Python build  
    the rest of the protocol-ip-port string, and I pass that to each page that  
    contains javascript to do getJSON() requests back to the Flask app.
    The Flask app is only known by its IP and port# (No DNS). To make the vbl  
    QPORT accessible in javascript, I use a script in the page body(!) 
           <em>&lt;script&gt;QPORT="{{QPORT|safe}}"&lt;/script&gt;</em>

    For example, 
        async function loadActiveQuakeTable(name) { 
            endpoint = QPORT+"/loadActiveQuakeTable?tablename="+name
            rowsplus = $.getJSON(endpoint, async function(x) {
            ...
            endpoint = QPORT+"/loadActiveQuakeTableParams?tablename="+name
            kwparams = $.getJSON(endpoint, async function(x) {
            ... 

</pre>

# YOUR PROJECT TITLE
#### Video Demo:  <URL HERE>
#### Description:
TODO

Step 1 of 3
Create a short video (that’s no more than 3 minutes in length) in which you present your project to the world, as with slides, screenshots, voiceover, and/or live action. Your video should somehow include your project’s title, your name, your city and country, and any other details that you’d like to convey to viewers. See howtogeek.com/205742/how-to-record-your-windows-mac-linux-android-or-ios-screen for tips on how to make a “screencast,” though you’re welcome to use an actual camera. Upload your video to YouTube (or, if blocked in your country, a similar site) and take note of its URL; it’s fine to flag it as “unlisted,” but don’t flag it as “private.”

Step 2 of 3
Create a README.md text file (named exactly that!) in your ~/project folder that explains your project. This file should include your Project Title, the URL of your video (created in step 1 above) and a description of your project. You may use the below as a template.

# YOUR PROJECT TITLE
#### Video Demo:  <URL HERE>
#### Description:
TODO
If unfamiliar with Markdown syntax, you might find GitHub’s Basic Writing and Formatting Syntax helpful. If you are using the CS50 Codespace and are prompted to “Open in CS50 Lab”, you can simply press Cancel to open your file in the Editor. You can also preview your .md file by clicking the ‘preview’ icon as explained here: Markdown Preview in vscode. Standard software project READMEs can often run into the thousands or tens of thousands of words in length; yours need not be that long, but should at least be several hundred words that describe things in detail!

Your README.md file should be minimally multiple paragraphs in length, and should explain what your project is, what each of the files you wrote for the project contains and does, and if you debated certain design choices, explaining why you made them. Ensure you allocate sufficient time and energy to writing a README.md that documents your project thoroughly. Be proud of it! If it is too short, the system will reject it.

Execute the submit50 command below from within your ~/project directory (or from whichever directory contains README.md file and your project’s code, which must also be submitted), logging in with your GitHub username and password when prompted. For security, you’ll see asterisks instead of the actual characters in your password.

Step 3 of 3
Be sure to visit your gradebook at cs50.me/cs50x a few minutes after you submit. It’s only by loading your Gradebook that the system can check to see whether you have completed the course, and that is also what triggers the (instant) generation of your free CS50 Certificate and the (within 30 days) generation of the Verified Certificate from edX, if you’ve completed all of the other assignments. Be sure to claim your free certificate (by following the link at the top of your gradebook) before 1 January 2023.

Don’t skip the above step! The course is not considered complete until you do the above and see the green banner saying you’ve completed the course. If you do not do the above prior to 1 January 2023, your status in the course will be subject to the carryover rules in the FAQ. The staff will not make any manual corrections in early 2023 based on this being skipped!

That’s it! Your project should be graded within a few minutes. If you don’t see any results in your gradebook, best to resubmit (running the above submit50 command) with only your README.md file this time. No need to resubmit your form.

