# Description
For this portion of the project I migrated my pandas dataframe to pyspark. I now do all of my calculations for graphing within the pyspark framework before converting to a pandas dataframe for the graphing portion. This is the framework I use for iter_rows and summary as well. I switch to pandas before doing what I did before. An interesting switch with my graphs is that instead of it being a weekly average one week at a time, it is now a rolling weekly average that goes value by value. 

# Main
## Modules
weather_data  
itertools islice  
asyncio  
## Functions

### main()
The main driver of the program.

# Weather_Data
## Modules
pandas  
logging  
matplotlib.pyplot  
functools reduce  
asyncio  
aiofiles  
os  
pyspark.sql SparkSession  
pyspark.sql.window Window  
pyspark.sql.functions  
## Classes
### WeatherData
WeatherData(file: str = None) -&gt; None

A class to manage and process weather data.

This class loads weather data from a CSV file, stores it in a PySpark DataFrame,
and provides functionality to extract, graph, and summarize the data.

#### Attributes:
__data_frame: A PySpark DataFrame containing weather data.  
spark: A SparkSession instance for distributed computing.  
__extracter: An instance of the DataExtracter class used for data visualization and summarization.
#### Methods:
\_\_init__(self, file: str = None) -&gt; None  
    Initializer for the WeatherData class. Loads weather data from a file and setting up helper classes to process data.  
:param file: The name of a file to be read into a dataframe.  

create_async(cls, str) -> WeatherData  
Asynchronously create a WeatherData instance.  
:param file: The name of a file to be read into a dataframe.  
:return: A WeatherData instance with the data loaded.

create_multiple_async(cls, file_list) -> list of WeatherData  
Asynchronously create multiple WeatherData instances from a list of files.  
:param file_list: List of filenames to load  
:return: List of WeatherData instances

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
Use multiprocessing to generate daily rain graphs for multiple locations.
Or use regular method if only one location is provided  
:param locations: List of locations to process

weekly_rain(self, location) -&gt; None  
Use multiprocessing to generate weekly rain graphs for multiple locations.  
Or use regular method if only one location is provided  
:param locations: List of locations to process

daily_humidity(self, location) -&gt; None  
Use multiprocessing to generate daily humidity graphs for multiple locations.  
Or use regular method if only one location is provided.  
:param locations: List of locations to process

daily_temperature(self, location) -&gt; None  
Use multiprocessing to generate daily temperature graphs for multiple locations.  
Or use regular method if only one location is provided.  
:param locations: List of locations to process

windy_days(self, location) -&gt; None  
Use multiprocessing to generate windy days charts for multiple locations.  
Or use regular method if only one location is provided.  
:param locations: List of locations to process

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

read_csv_async(file_name : str = None) -> pandas.DataFrame  
Asynchronously read data from a CSV file into a dataframe.  
There is a default file, leave file_name as None to access it.  
:param file_name: The name of the file to read  
:return: A pandas dataframe containing the data from the CSV file

### __DataExtracter
__DataExtractor(data_frame) -&gt; None

Private helper class to extract/summarize data from a PySpark DataFrame.

This class provides functionality to generate a summary of data using pandas
build in methods.

#### Attributes:
__data_frame: A PySpark DataFrame containing weather data.

#### Methods: 
\_\_init__(self, data_frame) -&gt; None  
Initializes the DataExtracter class with a PySpark DataFrame.  
:param data_frame: The DataFrame containing Weather Data.

summary(self) -&gt; pandas.DataFrame  
Generates a summary for data. Uses Pandas describe() method to provide information about the data.  
:return: A DataFrame cotnaining summary statistics.

iter_rows(self)  
Create a generator to iterate over rows of our DataFrame.  
:yeild: A row of the DataFrame.

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
