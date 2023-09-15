import pytest
from rgeo  import country_state

def test_one():
    assert country_state(33.04,-117.30) == "California"



