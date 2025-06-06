# README
## Installation
pip install --index-url https://test.pypi.org/simple/weather-tools-DrewBuck==0.1.0
## Data Used
In this program we use weather data from Australia. This data comes in the form of a CSV. It keeps track of location, min/max temp, rainfall, evaporation, sunshine, wind gust speed/direction, wind direction at 9am/3pm, wind speed at 9am/3pm, humidity at 9am/3pm, pressure at 9am/3pm, cloud coverage at 9am/3pm, temperature at 9am/3pm, rain expected today/tomorrow.

## NAME
Weather Data - This program reads data from a csv file into a python data structure

## FUNCTIONS
    main()
        The main driver of the program

    read_csv(file_name)
        :param file_name: The name of the file to read
        :return: A pandas dataframe containing the data from the CSV file
        Use pandas to read data from a CSV file into a dataframe

## FILE
   main.py

## SETUP OF MODULE
Module has files __init__.py, license.txt, manifest.in, setup.py, weather_data.py, and Data folder with our csvs. The __init__.py file is empty, so you must import things yourself. Manifest.in allows the program to use the weather data. Weather_data.py is the actual module code. Module is published to TestPyPi. 
