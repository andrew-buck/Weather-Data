# Instructions
1. pip install -r requirements.txt
2. python3 database.py
3. python3 app.py

# Description
I was struggling to not deadlock with spark clusters. I ended up removing them for now, will consider later. I created a database that contains all of my weather training data. You can add, delete, and view rows of the database from my website. When rows are updated, so is the pandas dataframe contained by my weather data class. You can also create graphs of wind, rain, temperature, and humidity in each location from my database. This is done by the weather data class. 

# App
## Modules
- flask
- flask_sqlalchemy
- sqlalchemy
- weather_data
- io
- base64
- matplotlib.pyplot

## Features
- Visualize weather data with various charts
- View and manage weather data records
- Insert new weather records
- Delete existing weather records

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
