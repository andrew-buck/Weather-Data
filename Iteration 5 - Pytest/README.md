# Description
Tested the dataloader by checking that the data frame in our WeatherData object is not empty. Also checked that giving a junk file name gives an empty dataframe. I then checked the summary methods of extracter/weather data class. I checked that when you have an empty dataframe summary just returns an empty dataframe. I then checked that the extracter summary doesn't return an empty dataframe in normal conditions. I also checked that The WeatherData class prints out the summary when summary is called. Checked that the same thing is printed when you print a weatherdata object. Finally I checked that the iter_rows method returns rows at a time and that each row contains the "location" column. 

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