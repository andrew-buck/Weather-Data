# Description
I used map to combine morning and evening data into one daily average data for multiple graphs. I used filter to look at days with higher and lower than 25km/h winds to put on a bar chart. I also used reduce to create weekly averages for rainfall. Overall I graphed daily rain, temperature, and humidity. I then graphed weekly rain and created a bar chart for windy and non windy days. You can get graphs for each location that is in the austrialian weather dataset. I chose these graphs because they seemed like useful information to have on weather in an area. It can show trends that happen yearly/monthly.

# Main
## Modules

weather_data
## Functions

### main()
The main driver of the program.
# Weather_Data
## Modules
pandas
importlib.resources
## Classes
### WeatherData
WeatherData(file: str = None) -&gt; None

A class to manage and process weather data.

This class loads weather data from a CSV file, stores it in a Pandas DataFrame,
and provides functionality to extract and summarize the data.

#### Attributes:
__data_frame (pandas.DataFrame): A DataFrame containing weather data.  
__extracter (WeatherData.__DataExtracter): An instance of the private helper class DataExtracter
                                               used for data summarization.
#### Methods:
\_\_init__(self, file: str = None) -&gt; None  
    Initializer for the WeatherData class. Loads weather data from a file and setting up helper classes to process data.  
:param file: The name of a file to be read into a dataframe.  

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
:yeild: A row of the Pandas DataFrame. 

daily_rain(self, location) -&gt; None  
Use the data extracter to graph daily rain.  
:param location: The location you want to graph.

weekly_rain(self, location) -&gt; None  
Use data extracter to graph weekly rain.  
:param location: The location you want to graph.

daily_humidity(self, location) -&gt; None  
Use data extracter to graph daily humidity.  
:param location: The location you want to graph.

daily_temperature(self, location) -&gt; None  
Use data extracter to graph daily temperature.  
:param location: The location you want to graph.

windy_days(self, location) -&gt; None  
Use dataextracter to chart windy days.  
:param location: The location you want to graph.

### __DataLoader
__DataLoader(file : str = None) -&gt; None  

Private helper class to load weather data from a CSV file.

This class is responsible for reading the weather data into a Pandas DataFrame.

#### Attributes:
data_frame (pandas.DataFrame): A DataFrame containing weather data.

#### Methods:
\_\_init__(self, file : str = None) -&gt; None  
Initializes the DataLoader class with a Pandas DataFrame by reading the csv file.  
:param file: The name of a csv file to load into a DataFrame. Leave as None if you want the default.


read_csv(self, file: str = None) -&gt; None  
Use Pandas to read data from a CSV file into a DataFrame. There is a default file.  
:param file_name: The name of the file to read, leave file_name as None to acces it.  
:return: A pandas dataframe containing the data from the CSV file

### __DataExtracter
__DataExtractor(data_frame : pandas.DataFrame) -&gt; None

Private helper class to extract/summarize data from a pandas DataFrame.

This class provides functionality to generate a summary of data using pandas
build in methods.

#### Attributes:
__data_frame (pandas.DataFrame): A DataFrame containing weather data.

#### Methods: 
\_\_init__(self, data_frame : pandas.DataFrame) -&gt; None  
Initializes the DataExtracter class with a Pandas DataFrame.  
:param data_frame: The DataFrame containing Weather Data.

summary(self) -&gt; pandas.DataFrame  
Generates a summary for data. Uses Pandas describe() method to provide information about the data.  
:return: A DataFrame cotnaining summary statistics.

iter_rows(self)  
Create a generator to iterate over rows of our Pandas DataFrame.  
:yeild: A row of the Pandas DataFrame.

daily_rain(self, location) -&gt; None  
Create a line graph of how much rain there is per day in a certain location.  
:param location: The location you want to graph.

weekly_rain(self, location) -&gt; None  
Create a line graph of how much rain there is per week in a certain location.  
Use reduce to get an average rain value for the week.  
:param location: The location you want to graph.

daily_humidity(self, location) -&gt; None  
Create a line graph of humidity % per day.  
Use map to combine 9am and 3pm values into one average value.  
:param location: The location you want to graph.

daily_temperature(self, location) -&gt; None  
Create a line graph of temperature per day.  
Use map to combine 9am and 3pm values into one average value.  
:param location: The location you want to graph.

windy_days(self, location) -&gt; None  
Create a bar chart of days that are windier than 25 km/h and less windy.  
Use filter to count how many days are and aren't windier than 25 km/h.  
:param location: The location you want to graph.
