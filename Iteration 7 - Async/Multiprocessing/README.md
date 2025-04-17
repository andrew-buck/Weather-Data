# Description
For my asynchronous programming I decided to create an async version of my read_csv method. This was because I figured that reading CSV files into a pandas dataframe was
the most I/O intensive process I have in my program. The Async version of read_csv is only faster sometimes because there is a lot of computation done after you have read the file 
to put it into the Pandas Dataframe.  

For multiprocessing I decided to create multiple processes if you want to create graphs for multiple locations or if you want to run all/multiple of the graphing functions at once. 
The Bulk_process_graphs method should be used if you want to run multiple of the graphing methods. This is because it efficiently creates one processing pool instead of spinning one up for each method.
If you only want to graph multiple locations for one graph, then pass in multiple locations to the original method. 

# Main
## Modules
weather_data  
itertools islice  
asyncio  
time
## Functions

### main()
The main driver of the program.
# Weather_Data
## Modules
pandas  
logging  
matplotlib.pyplot  
functools reduce  
multiprocessing cpu_count  
asyncio  
aiofiles  
concurrent.futures ProcessPoolExecuter
## Functions
process_helper(args)  
A helper function to return the result of a method call on the location.  
:param args: A tuple containing the extracter, method_name, and location.
## Classes
### WeatherData
WeatherData(file: str = None) -&gt; None

A class to manage and process weather data.

This class loads weather data from a CSV file, stores it in a Pandas DataFrame,
and provides functionality to extract, graph, and summarize the data.

#### Attributes:
__data_frame (pandas.DataFrame): A DataFrame containing weather data.  
__extracter (WeatherData.__DataExtracter): An instance of the private helper class DataExtracter
                                               used for data summarization.
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

bulk_process_graphs(self, locations, methods=None)  
Process graphs for multiple locations/methods in parallel using a single process pool.  
:param locations: List of locations to analyze  
:param methods: List of methods to run. If None, all methods are run.  
:return: Dictionary with results

process_multiple_locations(self, executor, method_name, locations)  
Process multiple locations in parallel using an existing process pool.  
:param executor: The ProcessPoolExecutor to use  
:param method_name: The name of the method to call  
:param locations: A list of locations to process  
:return: A list of results  

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
