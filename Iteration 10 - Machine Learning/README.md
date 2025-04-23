# Instructions
1. pip install -r requirements.txt
2. python3 database.py
3. python3 model.py (to train the forecasting models)
4. python3 app.py

# Description
I used scikit for machine learning on my data. To train the data I get the data from the database. I trained my multivariate model using the RandomForestRegressor algorithm. There is a seperate model for each location. I decided to create a class that allows you to access the forecasts to make the program portable. I then created a page on my web app to access the forecasts. The web app uses an instance of the class to access the forecasts. When you create a forecast it uses the most recent data from the location, so you can update the data from the web page and get different forecasts. 

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

# Weather_Data
## Modules
- pandas
- logging
- matplotlib.pyplot
- functools (reduce)
- asyncio
- aiofiles
- os
- sqlite3
- sqlalchemy

## Classes
### WeatherData
WeatherData(file: str = None) -&gt; None

A class to manage and process weather data.

This class loads weather data from a CSV file or database, stores it in a pandas DataFrame,
and provides functionality to extract, graph, and summarize the data.

#### Attributes:
__data_frame: A pandas DataFrame containing weather data.  
__extracter: An instance of the DataExtracter class used for data visualization and summarization.

#### Methods:
\_\_init__(self, file: str = None) -&gt; None  
    Initializer for the WeatherData class. Loads weather data from a file and setting up helper classes to process data.  
    :param file: The name of a file to be read into a dataframe.  

create_async(cls, file: str = None) -> WeatherData  
    Asynchronously create a WeatherData instance.  
    :param file: The name of a file to be read into a dataframe.  
    :return: A WeatherData instance with the data loaded.

create_multiple_async(cls, file_list) -> list of WeatherData  
    Asynchronously create multiple WeatherData instances from a list of files.  
    :param file_list: List of filenames to load  
    :return: List of WeatherData instances

update_from_database(self, db_path='weather.db') -> int
    Updates the internal pandas DataFrame with any new data from SQLite database.  
    :param db_path: Path to the SQLite database file  
    :return: Number of new records added  

\_\_str__(self)  
    Provides a string representation of the weather data summary.  
    The summary is the same as the output to the summary method.   
    :return: A string that comes from the Pandas describe dataframe.

summary(self) -> None  
    Print out a summary of weather data. 
    The summary is generated using the private helper class DataExtracter, which
    uses a pandas DataFrame describe() method to provide information about the data.

iter_rows(self)  
    Use data extracters generator to iterate over rows of our Pandas DataFrame.  
    :yield: A row of the Pandas DataFrame. 

daily_rain(self, location) -> matplotlib.figure.Figure  
    Use the data extracter to graph daily rain.  
    :param location: The location you want to graph.  
    :return: A matplotlib figure object

weekly_rain(self, location) -> matplotlib.figure.Figure  
    Use data extracter to graph weekly rain.  
    :param location: The location you want to graph.  
    :return: A matplotlib figure object

daily_humidity(self, location) -> matplotlib.figure.Figure  
    Use data extracter to graph daily humidity.  
    :param location: The location you want to graph.  
    :return: A matplotlib figure object

daily_temperature(self, location) -> matplotlib.figure.Figure  
    Use data extracter to graph daily temperature.  
    :param location: The location you want to graph.  
    :return: A matplotlib figure object

windy_days(self, location) -> matplotlib.figure.Figure  
    Use dataextracter to chart windy days.  
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

read_csv_async(file_name : str = None) -> pandas.DataFrame  
    Asynchronously read data from a CSV file into a dataframe.  
    There is a default file, leave file_name as None to access it.  
    :param file_name: The name of the file to read  
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
- sklearn.ensemble
- pandas
- sqlite3 
- sqlalchemy
- logging
- os
- numpy
- joblib
- json
- datetime

## Features
- Trained multivariate forecasting models for each location
- Random Forest Regression for predicting weather variables
- Support for forecasting multiple days into the future
- Metadata storage for model configuration

# MultivariateForecaster
## Modules
- joblib
- json
- pandas
- numpy
- sqlalchemy
- os
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
