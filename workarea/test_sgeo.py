import pytest
from sgeo import locate
from geopy.geocoders import Nominatim

def test_one():
    assert locate(33.036823, -117.292316) == "Encinitas"

