# test_oceancolormap.py

import pytest

from project import oceancolormap

# testing oceancolormap is lame, but it's one of the things I can pytest without
# from commented_out_geopy.geocoders import Nominatim
#      running into "E   ModuleNotFoundError: No module named 'geopy'" 
# ugh, can't import from oceancolormap, pytest still looks for geopy.

def test_natl():
    assert oceancolormap(30,-45)['name'] == "North Atlantic"

def test_satl():
    assert oceancolormap(-30,-45)['name'] == "South Atlantic"

def test_artc():
    assert oceancolormap(70,0)['name'] == "Arctic Ocean"

def test_sthn():
    assert oceancolormap(-70,0)['name'] == "Southern Ocean"

def test_spac():
    assert oceancolormap(-30,-150)['name'] == "South Pacific"

