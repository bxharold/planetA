# test_project.py
#    reverse-refactoring in order to meet cs50p's pytest rules...

import pytest
from dbquakes4planet import num_quakes, create_connection

def test_num_quakes():
    conn = create_connection("quakes.db")
    assert num_quakes(conn, "isspath") == 754
    assert num_quakes(conn, "qq_20230605") == 57
    assert num_quakes(conn, "qq_20230908") == 19

# test_oceancolormap.py
from project import oceancolormap

# testing oceancolormap is lame, but it's one of the things I can pytest without
#      running into "E   ModuleNotFoundError: No module named 'geopy'" 

def test_oceancolormap():
    assert oceancolormap(30,-45)['name'] == "North Atlantic"
    assert oceancolormap(-30,-45)['name'] == "South Atlantic"
    assert oceancolormap(70,0)['name'] == "Arctic Ocean"
    assert oceancolormap(-70,0)['name'] == "Southern Ocean"
    assert oceancolormap(-30,-150)['name'] == "South Pacific"


from dbquakes4planet import validCommandLine

# these values are used so the asserts appear simpler..
DTy, DTn = "2023-03-21", ("2023-03-21", "2023-13-21", "2023-12-31", "2023-13-31", "1923-10-21")   # date yes, no
TBy1 ,TBy2, TBn1, TBn2, TBn3 = "qq321", "qq_321", "321qq", "q", "abc_123"    # table names yes, no

def test_validCommandLine():
    assert validCommandLine(DTy, DTy, TBy1) == 0
    assert validCommandLine(DTy, DTy, TBn1) != 0
    assert validCommandLine(DTy, DTy, TBn2) != 0
    assert validCommandLine(DTy, DTy, TBn3) != 0
    assert validCommandLine(DTy, DTn[0], TBy1) == 0
    assert validCommandLine(DTy, DTn[1], TBy1) != 0
    assert validCommandLine(DTy, DTn[2], TBy1) == 0
    assert validCommandLine(DTy, DTn[3], TBy1) != 0
    assert validCommandLine(DTy, DTn[4], TBy1) != 0

