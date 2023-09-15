import pytest
#from geopy.geocoders import Nominatim
import geopy
from planetA import revgeo, Nominatim

def test_encinitas():
    rv = revgeo(33.04,-117.30)["address"]["town"]
    assert rv == "Encinitas"

