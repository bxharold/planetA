import pytest
from dbquakes4planet import validCommandLine, num_quakes, create_connection

###### this can be broken into 2 unit tests.


DTy, DTn = "2023-03-21", ("2023-03-21", "2023-13-21", "2023-12-31", "2023-13-31", "1923-10-21")   # date yes, no
TBy1 ,TBy2, TBn1, TBn2, TBn3 = "qq321", "qq_321", "321qq", "q", "abc_123"

def test_startdate_yyy():
    assert validCommandLine(DTy, DTy, TBy1) == 0

def test_startdate_yyn1():
    assert validCommandLine(DTy, DTy, TBn1) != 0

def test_startdate_yyn2():
    assert validCommandLine(DTy, DTy, TBn2) != 0

def test_startdate_yyn3():
    assert validCommandLine(DTy, DTy, TBn3) != 0

def test_startdate_yn_t0():
    assert validCommandLine(DTy, DTn[0], TBy1) == 0

def test_startdate_yn_t1():
    assert validCommandLine(DTy, DTn[1], TBy1) != 0

def test_startdate_yn_t2():
    assert validCommandLine(DTy, DTn[2], TBy1) == 0

def test_startdate_yn_t3():
    assert validCommandLine(DTy, DTn[3], TBy1) != 0

def test_startdate_yn_t4():
    assert validCommandLine(DTy, DTn[4], TBy1) != 0


def test_countstarA():
    conn = create_connection("quakes.db")
    assert num_quakes(conn, "isspath") == 754

def test_countstarB():
    conn = create_connection("quakes.db")
    assert num_quakes(conn, "qq_20230605") == 57

def test_countstarC():
    conn = create_connection("quakes.db")
    assert num_quakes(conn, "qq_20230908") == 19

"""
    Thoughts... Develop code with an eye to unit tests.
    pytesting a "try... except" is harder, best left for vtomorrow.    

def test_create_connection_exception():  
    with pytest.raises((OperationalError)) as excinfo:  
        create_connection("xquakes.db")
    assert str(excinfo.value) == "1"   

"""


