

//   planetjs.js  for isschart.html and quakechart.html
QPORT = "{{QPORT}}"    // provided by planetA.py

wm = {
    imwid : 1000, imht : 500,
    maxlat : 90,  minlat : -90, maxlon : 180, minlon : -180,
    }

const delay = ms => new Promise(res => setTimeout(res, ms));

rowsplus = []

function updateKwaksPanel(kwparams) {
    $("#daterangefromPP").html(kwparams['timminPP'])
    $("#daterangetoPP").html(kwparams['timmaxPP'])
    $("#timmin").html(kwparams['timmin']) 
    $("#timmax").html(kwparams['timmax'])
    $("#timdiff").html(kwparams['timdiff'])
    $("#databaseAndActiveTable").html(kwparams['database']+'/'+kwparams['activetable'])
    $("#quakerow").text(kwparams['rowCount']-1)
}

async function loadActiveQuakeTable(name) { 
    endpoint = QPORT+"/loadActiveQuakeTable?tablename="+name
    rowsplus = $.getJSON(endpoint, async function(x) {
        rowsplus = JSON.stringify(x)    // rowsplus is global
        console.log(rowsplus) 
        rowsplus = JSON.parse(rowsplus)
        console.log(rowsplus)
    })
    .done(function() {
        console.log( "loadActiveQuakeTable complete" );
        $("#databaseAndActiveTable").text("loaded "+ name)
    });
    await delay(200)
    endpoint = QPORT+"/loadActiveQuakeTableParams?tablename="+name
    kwparams = $.getJSON(endpoint, async function(x) {
        kwparams = JSON.stringify(x)
        console.log(kwparams)  
        kwparams = JSON.parse(kwparams)
        console.log("kwparams=", kwparams)
        await delay(100)
        })
        .done(function() {
            console.log( "loadActiveQuakeTableParams complete" );
            updateKwaksPanel(kwparams)
        });
}

$(document).ready(function() {

function lon2x(lon) {    // used for the plotly maps
    m = wm.imwid / (wm.maxlon - wm.minlon)
    rv = m * (lon - wm.minlon)
    return rv
}

function lat2y(lat) {        // used for the plotly maps
    m = wm.imht / (wm.maxlat - wm.minlat)
    rv = m * (lat - wm.minlat)
    return  wm.imht - rv
}

function LatLonGrid(wim) {
    var canvas = document.getElementById("canv");
    var ctx = canvas.getContext("2d");
    var img = document.getElementById("worldq");
    ctx.drawImage(img, 0, 0); 
    ctx.fillStyle = "#7f7f7f";
    ctx.font = "10px Arial";
    for ( lat=-90; lat<=90; lat+=15){
        a1 = lon2x(wm.minlon)
        a2 = lon2x(wm.maxlon)
        b = lat2y(lat)          // fractional line height. Nice.
        ctx.fillRect(a1,b, a2, 0.25 ); ctx.fillText(Math.round(lat),a1+45,b);
    }
    ctx.fillStyle = "#0f0f0f";
    ctx.font = "10px Arial";
    for ( lon=-180; lon<=180; lon+=30){
        a = lon2x(lon)
        b1 = lat2y(wm.minlat)
        b2 = lat2y(wm.maxlat)
        ctx.fillRect(a,b2, 0.25 ,b1); ctx.fillText(Math.round(lon),a+5,b1);
    }
}

$("#latlongrid").click(function() {    // invoked by  window.onload in layout :(
    LatLonGrid()
})

$("#update").click(function() {      
    $("#getISSjson").click()
});
    
$("#getISSjson").click(function(){       
    $.getJSON(QPORT+"/issdata", function(x) {  
        dd = JSON.stringify(x)
        $("#issmsg").html(dd)
        dd = JSON.parse(dd)
        $("#f1").html(dd['iss_position']['latitude'])
        $("#f2").html(dd['iss_position']['longitude'])
        $("#geolocation").html(dd['geolocation']['name'])
        updateLocation(dd)
    });
})

function updateLocation(dd) {     // ISS   
    ctx.fillStyle = "#FF0000";
    ctx.font = "10px Arial";
    a = lon2x(dd['iss_position']['longitude'])
    b = lat2y(dd['iss_position']['latitude'])
    ctx.fillRect(a, b, 3,8);  
    $("#timestamp").html(dd['timestamp'])
    $("#nicedate").html(dd['nicedate'])
    $("#latitude").html(dd['iss_position']['latitude'])
    $("#longitude").html(dd['iss_position']['longitude'])
    // $("#temperature").html(dd['temperature'])
    // $("#utilization").html(dd['utilization'])
    // $("#hostname").html(dd['hostname'])
    $("#geolocation").html(dd['geolocation']['name'])
}

function drawISSdot(x) {     // ISS   tim,lat,lon,nicedate,loc
    ctx.fillStyle = "#FF0000";
    ctx.font = "10px Arial";
    a = lon2x(x[2])
    b = lat2y(x[1])
    ctx.fillRect(a, b, 3, 8);  
    $("#timestamp").html(x[0])
    $("#nicedate").html(x[3])
    $("#latitude").html(x[1])
    $("#longitude").html(x[2])
    $("#geolocation").html(x[4])
}

// ---------------------------------------------- quakes

$("#loadv4").click( function() {  // dev only, invoked by oceans. async not needed here.
    refresh_map_image('worldi') 
    endpoint=QPORT+"/get_quakedata_JSON"  // a list of lists, array[11], but not a dict
    $.getJSON(endpoint,   async  function(x) {  // AHA. async is needed here for the await
        console.log("===> get_quakedata_JSON")  
        console.log(x)  // this is the full array of quake data
        console.log("===> get_quakedata_JSON")  
        let qevent = JSON.stringify(x)   // a string
        console.log("qevent, after JSON.stringify(x)", typeof qevent, "!", qevent)
        qevent = JSON.parse(qevent)   // an array, the same as before...
        console.log(qevent == x, typeof qevent, typeof x)  // ... false, object, object.
        console.log("qevent, after JSON.parse(qevent)", typeof qevent, "!", qevent)
        for (i=qevent.length-1; i>=0; i--) {
            delaytime = 50;   // constant time intervals
            await delay(delaytime);  // gorks unless $.getJSON's function is async
            qev = qevent[i]
            $("#quakemsg").html(JSON.stringify(qev))  
            // console.log(qev)
            // stringify is used to display the passed value of qev.
            // qev is already a JS object, so it can be dereferenced. 
            quakeLocation(qev[3], qev[4],"#ff00ff", qev[2] )
        }
    });
})

$("#isspathv4").click( function() { // Dev. Used to test JS await-promise based animation.
    refresh_map_image('worldi') 
    endpoint=QPORT+"/get_isspath_JSON"  // a list of lists, array[11], but not a dict
    $.getJSON(endpoint,   async  function(x) {  // async is needed here for the await
        let qevent = JSON.stringify(x)   // a string
        qevent = JSON.parse(qevent)   
        delaytime = 30; 
        if (document.getElementById('goslow').checked)  {
            delaytime = 500;  
        }
        for (i=0; i<qevent.length; i++) {
            await delay(delaytime);  // gorks unless $.getJSON's function is async
            qev = qevent[i]
            $("#issmsg").html(JSON.stringify(qev))  
            console.log(qev[4])
            drawISSdot(qev)
        }
    });
})

$("#updateQevent").click(function() {   
    $("#getQEVENTjson").click()
});

function postpendToSelectList(listname, id, dat, loc, magn ) {
    var x = document.getElementById(listname);
    N = id
    var option = document.createElement("option");
    option.text = dat + "..." + magn;
    x.add(option);  // adds to bottom of list; 
    var option = document.createElement("option");
    option.text = loc;
    x.add(option);  // adds to bottom of list; 
    var option = document.createElement("option");
    option.text = "~    ~     ~     ~     ~     ~     ~     ~     ~     ~"
           + "    ~     ~     ~     ~     ~     ~     ~     ~     ~     " + N ;
    x.add(option);  // adds to bottom of list; 
    xx = $("#mySelect option").length
    x.selectedIndex = xx-1;
}

async function quakeLocation(lat, lon, color, magn) {      
    ctx.fillStyle = color;
    y = lat2y(lat)
    x = lon2x(lon)
    m = (magn-3)
    m = m * 3
    ctx.beginPath(); ctx.arc(x, y, m, 0, 2*Math.PI); ctx.fill();
}

async function getQEvent() {             
    console.log("getQEvent")
    quakerow = $("#quakerow").text();
    console.log("quakerow in getQEvent", quakerow)
    if (quakerow>=0) {
        $("#getQEVENTjson").click()
    } else {
        alert("reached end of data")
    }
    return quakerow
}

$("#nextqevent").click( function() {   
    quakerow = $("#quakerow").text() 
    // dd = [1, 1679..., 7.5, 33.0, -117.3, 3.0, 'Encinitas, CA', '2023...', -10, '23:59:50']
    // id tim mag lat lon dep loc datepp deltat deltat(hms)    
    dd = rowsplus[quakerow]
    if(quakerow>=0) { 
        postpendToSelectList("mySelect", dd[0], dd[7], dd[6], dd[2] )
        console.log(quakerow)
        { // the previous dot... "Paint it black"
            lat = rowsplus[quakerow][3]
            lon = rowsplus[quakerow][4]
            mag = rowsplus[quakerow][2]
            // quakeLocation(lat, lon, "#6D4C41", mag)   // brown 
            quakeLocation(lat, lon,    "#000000", mag)   // black 
        }
        if ( quakerow > 0) 
        { // paint it bright
            lat = rowsplus[quakerow-1][3]
            lon = rowsplus[quakerow-1][4]
            mag = rowsplus[quakerow-1][2]
            quakeLocation(lat, lon, "#ff0000", mag)  // red
        }
        quakerow -= 1
        $("#quakerow").text(quakerow)
    } else {
        console.log("wtf?")
        return
    }
});

$("#allqevents").click(async function() {    // THIS IS kwaks VERSION 
    refresh_map_image('worldq')  // 
    console.log("allqevents")
    $('#mySelect').empty();
    const cliptime = $("#cliptime").val() * 1000 // sec
    $("#quakerow").text( kwparams['rowCount']-1 )
    delaytime = 250  // s/b function delta,  daterangefrom + deltat/dateinterval
    for (let i=0; i<kwparams['rowCount']-1; i++) {
        rp = rowsplus[i]
        // console.log(i,"  rp= ", rp)
        deltat = rp[8]
        tmin = kwparams['timmin']
        tmax = kwparams['timmax']
        tdiff = kwparams['timdiff']
        /* 
        tdiff and cliptime determine the fractional amount of cliptime that deltat represents.
        e.g., if cliptime=10 and tdiff=86, then deltat=8.6 yields delaytime=1 sec = 1000 msec.
        deltat/tdiff is the fractional amount of cliptime.
        */
        delaytime = deltat/tdiff * cliptime
        // console.log(tmin,tmax,  deltat, tdiff, cliptime, delaytime)
        $("#nextqevent").click()
        await delay(delaytime);    
    }
});

// --------------------------------------- oceans
function oceanDot(lat, lon, color, txt) {   // only used for calibration/testing
    console.log("oceanDot: ", lat, lon, color, txt)
    dotwid = 12; dotht = 12
    // dotwid = 6; dotht = 6
    ctx.fillStyle = color;
    ctx.font = "12px Arial";
    y = lat2y(lat)
    x = lon2x(lon)
    ctx.fillRect( x-dotwid/2, y-dotht/2, dotwid, dotht); 
    ctx.fillStyle = "#000000";
    ctx.fillText(txt,x-dotwid/2, y-dotht/2);
}

function getOceanColor(lat,lon){
    // http://127.0.0.1:5000/oceancolor?lat=60&lon=137
    endpoint=QPORT+"/oceancolor?lat="+lat+"&lon="+lon
    console.log("=="+QPORT+"=="+endpoint+"==")
    dd = $.getJSON(endpoint, function(x) {
        dd = JSON.stringify(x) // {"code":"spac","color":"#ffff66","name":"South Pacific"}
        dd = JSON.parse(dd)
    });
    return dd
}

async function oceansLoop() {   // used to test "await delay"
    for ( i = -45; i <= 45; i+=45) { for ( j = -180; j <= 180; j+=45) {
    // for ( i = -67.5; i <= 67.5; i+=22.5) { for ( j = -180; j <= 180; j+=22.5) {
    // for ( i = -55; i <= 65; i+=5) { for ( j = -150; j <= 180; j+=7) {
            dd = getOceanColor(i,j)
            await delay(10 + Math.random()*100 ) 
            // console.log("getOceanColor ", i,j,dd["code"],dd["color"],dd["name"])
            oceanDot(i,j, dd["color"], dd["code"])
    }}
}

$("#oceans").click(function() {   // used to check "await delay"
    refresh_map_image('worldi') 
    oceansLoop()
});

function refresh_map_image(wim) {
    console.log("refresh_map_image " + wim)    // {{img}} not available here
    var img = document.getElementById(wim);
    ctx.drawImage(img, 0, 0);
    // $("#latlongrid").click() 
    LatLonGrid(wim) 
}

var canvas = document.getElementById("canv");
var ctx = canvas.getContext("2d");
// refresh_map_image('worldq')

});   // end ready

// === timer for ISS. This is the older approach. refer to HiMac2:~/qvcs50p/jpromise 
timerID = 0
timerCounter = 0;
timerStop = false
function startTimer() {  
    if (timerID == 0) {  // don't start a 2nd timer
        timerStop = false
        timerCounter=0
        timerID = setInterval(myTimer, 10000);
        console.log("start timer." + timerID)
        $("#loopsteps").html(timerCounter)
    }
}
function stopTimer() {
    clearInterval(timerID);
    timerID = 0
    timerStop = true
    console.log("stop timer.")
}
function myTimer() {
    console.log("timer " + timerCounter)
    timerCounter = timerCounter + 1
    if (timerCounter%10000==0 || timerStop) {
        stopTimer()  
    } else {  
        $("#loopsteps").html(timerCounter)
        $("#getISSjson").click()
    }
}
// === end timer 
// END planetjs.js   ---o---     ---o---     ---o---    
