# Instructions
1. Install dependencies: `pip install -r requirements.txt`
2. Create database: `python3 database.py`
3. Train forecasting models: `python3 model.py`
4. Run the webapp: `python3 app.py`

# Final Changes
For my final changes to the app I added a summary feature to my webpage that allows you to see the summary from the weatherdata module. I also added in clearer comments to code in each module. Lastly, I removed unused features from weather_data.py, styles.css, and model.py.

# App Description
This app creates a database for our weather data. Using that data we create machine learning models that can forecast weather up to 7 days into the future. We also have a Weather data module that works on the data in the database by creating graphs and summaries. A web app is built using all of these features, creating a user interface that allows easy interaction with our data.  

# Changes made per phase:
## Phase 1
Read the weather data into a pandas dataframe
## Phase 2 - Deployed a module for pip
My module lets you work with the weather data using a pandas dataframe
## Phase 3 - Created classes
Created the weather data module that contains classes that all allow me to work with the weather data. I decided not to continue updated my module for pip as it was a lot of extra work.
## Phase 4 - Iterators
I created a logger, added in error handling, and created a generator/iterator over my weather data. 
## Phase 5 - Pytest
Created testing for the weatherdata app. 
## Phase 6 - Matplotlib
Creating graphing functionality for the data. Each graph uses functional programming to create the graph.
## Phase 7 - Async/Multiprocessing
Create the ability for my app to use asyncronous programming and multiprocessing to allow for faster running.
## Phase 8 - Spark
I got rid of my pandas dataframe and replaced it with a spark dataframe so I could run my app on multiple clusters. I also had to stop using Async/Multiprocessing features so that I could utilize the clusters of apache spark. 
## Phase 9 - Web app
I had to get rid of spark and go back to pandas dataframes, as I was having a hard time getting spark to work with flask. I had to change my graphing functionality to return the graphs as an image. I then created a web app using flask to create a user interface for my data.
## Phase 10 - Machine Learning
Utilized machine learning to create forecasts on my weather data. Added the forecasts to my web app for users to utilize. 

# App
## Modules
- flask
- flask_sqlalchemy
- sqlalchemy
- weather_data
- io
- base64
- matplotlib.pyplot
- models.multivariate_forecaster

## Features
- Visualize weather data with various charts
- View and manage weather data records
- Insert new weather records
- Delete existing weather records
- Generate weather forecasts using machine learning models
- Display summary statistics for weather data

# Weather_Data
## Modules
- pandas
- logging
- matplotlib
- matplotlib.pyplot
- functools (reduce)
- os
- sqlite3
- sqlalchemy

## Classes
### WeatherData
WeatherData(file: str = None) -&gt; None

A class to manage and process weather data.

This class loads weather data from a CSV file or database, stores it in a pandas DataFrame,
and provides functionality to extract, graph, and summarize the data.

### Attributes:
__data_frame: A pandas DataFrame containing weather data.  
__extracter: An instance of the DataExtracter class used for data visualization and summarization.

#### Methods:
\_\_init__(self, file: str = None) -&gt; None  
    Initializer for the WeatherData class. Loads weather data from a file and setting up helper classes to process data.  
    :param file: The name of a file to be read into a dataframe.

update_from_database(self, db_path='weather.db') -> int
    Updates the internal pandas DataFrame with any new data from SQLite database. 
    :param db_path: Path to the SQLite database file  
    :return: Number of new records added 

\_\_str__(self) -> str  
    Provides a string representation of the weather data summary.  
    The summary is the same as the output to the summary method.   
    :return: A string that comes from the Pandas describe dataframe.

summary(self) -> None  
    Print out a summary of weather data. 
    The summary is generated using the private helper class DataExtracter, which
    uses a pandas DataFrame describe() method to provide information about the data.

iter_rows(self)  
    Use data extracters generator to iterate over rows of our Pandas DataFrame.  
    :yeild: A row of the Pandas DataFrame.

daily_rain(self, location) -> matplotlib.figure.Figure  
    Use the data extracter to create a graph of daily rain in a location.  
    :param location: The location you want to graph.  
    :return: A matplotlib figure object

weekly_rain(self, location) -> matplotlib.figure.Figure  
    Use data extracter to create a graph of weekly rain in a location.  
    :param location: The location you want to graph.  
    :return: A matplotlib figure object

daily_humidity(self, location) -> matplotlib.figure.Figure  
    Use data extracter to create a graph of daily humidity in a location.  
    :param location: The location you want to graph.  
    :return: A matplotlib figure object

daily_temperature(self, location) -> matplotlib.figure.Figure  
    Use data extracter to create a graph of daily temperature in a location.  
    :param location: The location you want to graph.  
    :return: A matplotlib figure object

windy_days(self, location) -> matplotlib.figure.Figure  
    Use dataextracter to create a chart of windy days in a location.  
    :param location: The location you want to graph.  
    :return: A matplotlib figure object

### __DataLoader
__DataLoader(file : str = None) -&gt; None  

Private helper class to load weather data from a CSV file or database.

This class is responsible for reading the weather data into a pandas DataFrame.

#### Methods:
\_\_init__(self, file : str = None) -&gt; None  
    Initializes the DataLoader class with a Pandas DataFrame by reading the csv file.  
    :param file: The name of a csv file to load into a DataFrame. Leave as None if you want the default.

read_database(db_path='weather.db') -> pandas.DataFrame
    Read data directly from a SQLite database into a pandas DataFrame.  
    :param db_path: Path to the SQLite database file  
    :return: A pandas DataFrame containing the data from the database

read_csv(file_name: str = None) -&gt; pandas.DataFrame  
    Use Pandas to read data from a CSV file into a DataFrame. There is a default file.  
    :param file_name: The name of the file to read, leave file_name as None to access it.  
    :return: A pandas dataframe containing the data from the CSV file

### DataExtracter
DataExtracter(data_frame) -&gt; None  

Helper class to extract/summarize data from a pandas DataFrame.  

This class is responsible for extracting, graphing, and summarizing data from a pandas DataFrame.

#### Methods: 
\_\_init__(self, data_frame) -&gt; None  
    Initializes the DataExtracter class with a pandas DataFrame.  
    :param data_frame: The DataFrame containing Weather Data.

summary(self) -&gt; pandas.DataFrame  
    Generates a summary for data. Uses Pandas describe() method to provide information about the data.  
    :return: A DataFrame containing summary statistics.

iter_rows(self)  
    Create a generator to iterate over rows of our DataFrame.  
    :yield: A row of the DataFrame.

daily_rain(self, location) -> matplotlib.figure.Figure  
    Create a line graph of how much rain there is per day in a certain location.  
    :param location: The location you want to graph.  
    :return: A matplotlib figure object

weekly_rain(self, location) -> matplotlib.figure.Figure  
    Create a line graph of how much rain there is per week in a certain location.  
    Use reduce to get an average rain value for the week.  
    :param location: The location you want to graph.  
    :return: A matplotlib figure object

daily_humidity(self, location) -> matplotlib.figure.Figure  
    Create a line graph of humidity % per day.  
    Use map to combine 9am and 3pm values into one average value.  
    :param location: The location you want to graph.  
    :return: A matplotlib figure object

daily_temperature(self, location) -> matplotlib.figure.Figure  
    Create a line graph of temperature per day.  
    Use map to combine 9am and 3pm values into one average value.  
    :param location: The location you want to graph.  
    :return: A matplotlib figure object

windy_days(self, location) -> matplotlib.figure.Figure  
    Create a bar chart of days that are windier than 25 km/h and less windy.  
    Use filter to count how many days are and aren't windier than 25 km/h.  
    :param location: The location you want to graph.  
    :return: A matplotlib figure object

# Machine Learning Models
## Modules
- sklearn.ensemble (RandomForestRegressor)
- pandas
- sqlite3 
- sqlalchemy
- logging
- os
- numpy
- joblib
- json

## Features
- Trained multivariate forecasting models for each location
- Random Forest Regression for predicting weather variables
- Support for forecasting multiple days into the future
- Metadata storage for model configuration

# Database
## Modules
- os
- pandas
- sqlalchemy (create_engine, Column, Integer, Float, String, Boolean, MetaData, Table)
- sqlalchemy.ext.declarative (declarative_base)
- sqlalchemy.orm (sessionmaker)

## Functions
### create_weather_database()
Creates a SQLite database from the Weather Training Data CSV file.

This function:
- Sets up a connection to a SQLite database
- Defines a Weather table model with all the required columns
- Creates the table in the database
- Loads data from the CSV file
- Handles potential missing values in the data
- Inserts all records into the database
- Provides progress feedback through console output

## Structure
- SQLite database (weather.db)
- Main table: weather
- Fields include:
  - id: Primary key
  - row_id: Original row ID from CSV
  - location: City/location name
  - min_temp, max_temp: Temperature extremes
  - rainfall: Daily precipitation amount
  - evaporation, sunshine: Additional measurements
  - wind_gust_dir, wind_gust_speed: Wind gust information
  - wind_dir_9am, wind_dir_3pm: Wind direction measurements
  - windspeed9am, windspeed3pm: Wind speed measurements
  - humidity9am, humidity3pm: Humidity measurements
  - pressure9am, pressure3pm: Atmospheric pressure
  - cloud9am, cloud3pm: Cloud cover measurements
  - temp9am, temp3pm: Temperature measurements
  - rain_today: Indicator if it rained today
  - rain_tomorrow: Predicted rainfall for tomorrow

# MultivariateForecaster
## Modules
- joblib
- json
- pandas
- numpy
- sqlalchemy
- datetime

## Class
### MultivariateForecaster
MultivariateForecaster(metadata_path='./models/multivariate_model_metadata.json', db_path='weather.db')

A class for generating multivariate weather forecasts using pre-trained models.

This class loads pre-trained models and metadata to generate forecasts for all
weather variables simultaneously for a specified number of days.

#### Attributes:
metadata (dict): Dictionary containing model metadata for each location  
db_path (str): Path to the SQLite database  
engine: SQLAlchemy engine for database connection

#### Methods:
\_\_init__(self, metadata_path='./models/multivariate_model_metadata.json', db_path='weather.db')  
    Initializer for the MultivariateForecaster class.  
    Loads model metadata from a JSON file and sets up the database connection.  
    :param metadata_path: Path to the metadata JSON file  
    :param db_path: Path to the SQLite database  

get_available_locations(self)  
    Returns a list of locations available for forecasting.  
    :return: A list of location names as strings  

get_available_columns(self, location)  
    Returns a list of columns available for the specified location.  
    :param location: The location to get columns for  
    :return: A list of column names as strings  
    :raises ValueError: If the location is not found in metadata  

get_latest_data(self, location, n_lags=14)  
    Gets the latest data for all columns for a specific location.  
    Retrieves the most recent data points from the database for the specified location,  
    which will be used as input for the forecasting model.  
    :param location: The location to fetch data for  
    :param n_lags: Number of days of historical data to fetch  
    :return: Dictionary with column names as keys and lists of values as values  
    :raises ValueError: If the location is not found in metadata  

forecast(self, location, days=7)  
    Generate a forecast for all weather variables for the specified location.  
    This method:  
    1. Retrieves the latest data for the location  
    2. Loads the appropriate pre-trained model  
    3. Makes predictions for the specified number of days  
    4. Formats the results with appropriate units and dates  
    :param location: Location to forecast for  
    :param days: Number of days to forecast (default: 7)  
    :return: Dictionary containing forecast results with dates and values for each column  
    :raises ValueError: If the location is not found or if there's not enough data  

_get_column_units(self, column)  
    Returns appropriate units for a weather variable based on its name.  
    :param column: The name of the weather variable column  
    :return: String representing the units for the given column
