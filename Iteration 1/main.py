"""
This program reads data from a csv file into a python data structure
"""
import pandas

def read_csv(file_name):
    """
    Use pandas to read data from a CSV file into a dataframe
    :param file_name: The name of the file to read
    :return: A pandas dataframe containing the data from the CSV file
    """
    weather_data = pandas.read_csv(file_name)
    return weather_data

def main():
    """
    The main driver of the program
    """
    weather_data = read_csv("australia-weather-data/Weather Training Data.csv")
    print(weather_data.describe())

if __name__ == "__main__":
    main()
