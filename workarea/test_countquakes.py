import pytest
from dbquakes4planet import num_quakes, create_connection

def test_countstarA():
    conn = create_connection("quakes.db")
    assert num_quakes(conn, "isspath") == 754

def test_countstarB():
    conn = create_connection("quakes.db")
    assert num_quakes(conn, "qq_20230605") == 57

def test_countstarC():
    conn = create_connection("quakes.db")
    assert num_quakes(conn, "qq_20230908") == 19


