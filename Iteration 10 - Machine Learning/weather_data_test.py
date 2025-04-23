"""
Test File for the project.
"""
import pytest
import pandas as pd
from itertools import islice
from weather_data import WeatherData

@pytest.fixture(scope="session")
def weather_data_instance():
    """
    WeatherData Object for testing.
    """
    return WeatherData()

def test_data_loader(weather_data_instance):
    """
    Testing that the data loader correctly gave us a pandas dataframe that isn't empty
    Accesses a private data member for this. 
    """
    assert isinstance(weather_data_instance._WeatherData__data_frame, pd.DataFrame) 
    assert not weather_data_instance._WeatherData__data_frame.empty

def test_data_loader_file_not_found():
    """
    Test that data loader correctly handles an incorrect file.
    """
    wd = WeatherData("Blah")
    df = wd._WeatherData__data_frame
    assert df.empty

def test_data_extrater_summary_empty():
    """
    Test that Data Extracter returns an empty dataframe if
    DataFrame is empty
    """
    wd = WeatherData("Blah")
    df = wd._WeatherData__extracter.summary()
    assert df.empty

def test_data_extracter_summary(weather_data_instance, capsys):
    """
    Test that data extracter summary gives a non empty
    pandas Dataframe. Test that WeatherData summary prints the
    summary. Test that when you print the object it prints the summmary.
    """
    summary = weather_data_instance._WeatherData__extracter.summary()
    weather_data_instance.summary()
    captured = capsys.readouterr()
    print(weather_data_instance)
    captured2 = capsys.readouterr()
    assert len(captured.out) > 5
    assert captured == captured2
    assert not summary.empty

def test_iter_rows(weather_data_instance):
    """
    Testing that the iterator works in our WeatherData Class.
    """
    i = 0
    for row in islice(weather_data_instance.iter_rows(), 5):
        assert row[0] == i
        assert str(row[1]).find("Location") != -1
        i += 1