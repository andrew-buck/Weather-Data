"""
This program reads data from a csv file into a python data structure
"""
import pandas
from importlib import resources
import io

def read_csv(file_name=None):
    """
    Use pandas to read data from a CSV file into a dataframe
    :param file_name: The name of the file to read
    :return: A pandas dataframe containing the data from the CSV file
    """
    if file_name is None:
        file_name = 'Data/Weather Training Data.csv'
    with resources.open_text('weather_data', file_name) as file:
            weather_data = pandas.read_csv(file)
    return weather_data