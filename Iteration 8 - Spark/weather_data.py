"""
Defines a wrapper class for a Pandas Dataframe.
"""
import logging
import pandas
import matplotlib.pyplot as plt
from functools import reduce
import asyncio
import aiofiles
import os
os.environ['PYARROW_IGNORE_TIMEZONE'] = '1'
from pyspark.sql import SparkSession
from pyspark.sql.window import Window
from pyspark.sql.functions import avg, col, row_number, count, when
import pyspark.sql.functions as F
logging.basicConfig(filename='logging/logging.log', level=logging.INFO,
                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("my_logger")

class WeatherData:
    """
    A class to manage and process weather data.

    This class loads weather data from a CSV file, stores it in a PySpark DataFrame,
    and provides functionality to extract, graph, and summarize the data.

    Attributes:
        __data_frame: A PySpark DataFrame containing weather data.  
        spark: A SparkSession instance for distributed computing.  
        __extracter: An instance of the DataExtracter class used for data visualization and summarization.
    """
    def __init__(self, file : str = None) -> None:
        """
        Initializer for the WeatherData class. Loads weather data from a file and
        setting up helper classes to process data.
        :param file: The name of a file to be read into a dataframe.
        """
        loader = self.__DataLoader(file) 
        self.__data_frame = loader.data_frame.set_index('Location')
        self.spark = (SparkSession.builder
                 .appName("WeatherData")
                 .config("spark.driver.host", "localhost")
                 .config("spark.driver.bindAddress", "127.0.0.1")
                 .getOrCreate()) # Start the spark session
        self.__data_frame = self.spark.createDataFrame(self.__data_frame.reset_index()) # Convert to a Spark DataFrame
        self.__extracter = DataExtracter(self.__data_frame)

    @classmethod
    async def create_async(cls, file: str = None):
        """
        Asynchronously create a WeatherData instance.
        
        :param file: The name of a file to be read into a dataframe.
        :return: A WeatherData instance with the data loaded.
        """
        # Create a new instance without calling __init__
        instance = cls.__new__(cls)
        # Load data asynchronously
        data_frame = await cls.__DataLoader.read_csv_async(file)
        # Set up the instance attributes manually
        instance.__data_frame = data_frame.set_index('Location')
        instance.__extracter = DataExtracter(instance.__data_frame)
        return instance
        
    @classmethod
    async def create_multiple_async(cls, file_list):
        """
        Asynchronously create multiple WeatherData instances from a list of files.
        
        :param file_list: List of filenames to load
        :return: List of WeatherData instances
        """
        tasks = [asyncio.create_task(cls.create_async(file)) for file in file_list]
        # tasks = [cls.create_async(file) for file in file_list]
        return await asyncio.gather(*tasks)

    def summary(self) -> None:
        """
        Print out a summary of weather data.

        The summary is generated using the private helper class DataExtracter, which
        uses a pandas DataFrame describe() method to provide information about the data.
        """
        sum = self.__extracter.summary()
        print(sum)

    def iter_rows(self):
        """
        Use data extracters generator to iterate over rows of a Pandas DataFrame.

        :yeild: A row of the Pandas DataFrame. 
        """
        for row in self.__extracter.iter_rows():
            yield row

    def __str__(self):
        """
        Provides a string representation of the weather data summary. 

        The summary is the same as the output to the summary method. 
        :return: A string that comes from the Pandas describe dataframe.
        """
        return self.__extracter.summary().__str__()

    def daily_rain(self, location):
        """
        Use the data extracter to graph daily rain.

        :param location: The location you want to graph.
        """
        self.__extracter.daily_rain(location)

    def weekly_rain(self, location):
        """
        Use data extracter to graph weekly rain.

        :param location: The location you want to graph.
        """
        self.__extracter.weekly_rain(location)

    def daily_humidity(self, location):
        """
        Use data extracter to graph daily humidity

        :param location: The location you want to graph.
        """
        self.__extracter.daily_humidity(location)

    def daily_temperature(self, location):
        """
        Use data extracter to graph daily temperature

        :param location: The location you want to graph.
        """
        self.__extracter.daily_temperature(location)

    def windy_days(self, location):
        """
        Use dataextracter to chart windy days.

        :param location: The location you want to graph.
        """
        self.__extracter.windy_days(location)

    class __DataLoader:
        """
        Private helper class to load weather data from a CSV file.
        
        This class is responsible for reading the weather data into a pandas DataFrame.
        """
        def __init__(self, file : str = None) -> None:
            '''
            Initializes the DataLoader class with a Pandas DataFrame by reading the csv file.

            :param file: The name of a csv file to load into a DataFrame. 
            Leave as None if you want the default.
            '''
            self.data_frame = self.read_csv(file)

        @staticmethod
        def read_csv(file_name : str =None) -> pandas.DataFrame:
            """
            Use pandas to read data from a CSV file into a dataframe.
            There is a default file, leave file_name as None to access it.

            :param file_name: The name of the file to read
            :return: A pandas dataframe containing the data from the CSV file
            """
            weather_data = pandas.DataFrame()
            if file_name is None:
                file_name = "Data/Weather Training Data.csv"
            try:
                with open(file_name, 'r', encoding='utf-8') as file:
                    weather_data = pandas.read_csv(file)
            except FileNotFoundError:
                logger.error("File not found: %s", file_name)
            except pandas.errors.EmptyDataError:
                logger.error("CSV file is empty")
            except Exception as e:
                logger.error("An error occurred while reading the file: %s", e)
            return weather_data

        @staticmethod
        async def read_csv_async(file_name: str = None) -> pandas.DataFrame:
            """
            Asynchronously read data from a CSV file into a dataframe.
            There is a default file, leave file_name as None to access it.

            :param file_name: The name of the file to read
            :return: A pandas dataframe containing the data from the CSV file
            """
            weather_data = pandas.DataFrame()
            if file_name is None:
                file_name = "Data/Weather Training Data.csv"
            try:
                async with aiofiles.open(file_name, 'r', encoding='utf-8') as file:
                    # Read the file content asynchronously
                    content = await file.read()
                    # Run pandas in a thread pool
                    loop = asyncio.get_event_loop()
                    weather_data = await loop.run_in_executor(None, lambda: pandas.read_csv(file_name))

            except FileNotFoundError:
                logger.error("File not found: %s", file_name)
            except pandas.errors.EmptyDataError:
                logger.error("CSV file is empty")
            except Exception as e:
                logger.error("An error occurred while reading the file: %s", e)
            return weather_data

class DataExtracter:
    """
    Private helper class to extract/summarize data from a PySpark DataFrame.

    This class is responsible for extracting, graphing, and summarizing data from a Spark DataFrame.
    """
    def __init__(self, data_frame) -> None:
        """
        Initializes the DataExtracter class with a PySpark DataFrame.

        :param data_frame: The DataFrame containing weather data. 
        """
        self.__data_frame = data_frame

    def summary(self) -> pandas.DataFrame:
        """
        Generates a summary for data.

        Uses Pandas describe() method to provide information about the data.
        :return: A DataFrame containing summary statistics. 
        """
        if self.__data_frame.count() == 0:
            logger.warning("Data frame is empty, no summary available.")
            return self.__data_frame
        return self.__data_frame.toPandas().describe()

    def iter_rows(self):
        """
        Create a generator to iterate over rows of our DataFrame.

        :yeild: A row of the DataFrame. 
        """
        pandas_df = self.__data_frame.toPandas().set_index('Location')
        for row in pandas_df.iterrows():
            yield row

    def daily_rain(self, location):
        """
        Create a line graph of how much rain there is per day in a certain location.

        :param location: The location you want to graph.
        """
        location_data = self.__data_frame.filter(f"Location = '{location}'")
        tempDF = location_data.select('Rainfall').toPandas()
        plt.figure(figsize=(10, 5))
        plt.plot(tempDF.index, tempDF['Rainfall'], marker='', linestyle='-', color='blue')
        plt.xlabel('Days')
        plt.ylabel('Rainfall (mm)')
        plt.title(f'Rainfall in {location} Over Time')
        plt.grid()
        plt.show()

    def weekly_rain(self, location):
        '''
        Create a line graph of how much rain there is per week in a certain location.
        Use reduce to get an average rain value for the week.

        :param location: The location you want to graph.
        '''
        # Filter by location
        location_data = self.__data_frame.filter(f"Location = '{location}'")
        # Add row number for ordering
        location_data = location_data.withColumn("row_id", 
                                                F.monotonically_increasing_id())
        # Define 7-day window specification
        window_spec = Window.orderBy("row_id").rowsBetween(-3, 3)
        # Calculate average rainfall over the window
        smoothed_data = location_data.withColumn("Rainfall_Smoothed", 
                                                F.avg("Rainfall").over(window_spec))
        # Now convert to pandas for plotting
        tempDF = smoothed_data.select("Rainfall", "Rainfall_Smoothed").toPandas()
        if 'Rainfall_Smoothed' in tempDF.columns and not tempDF.empty:
            tempDF['Rainfall_Smoothed'] = tempDF['Rainfall_Smoothed'].interpolate()
        # Create the plot
        plt.figure(figsize=(10, 5))
        plt.plot(tempDF.index, tempDF['Rainfall_Smoothed'], marker='', linestyle='-', label='7-day Avg', color='blue')
        plt.xlabel('Days')
        plt.ylabel('Rainfall (mm)')
        plt.title(f'Smoothed Rainfall in {location} (Weekly)')
        plt.grid()
        plt.legend()
        plt.show()

    
    def daily_humidity(self, location):
        '''
        Create a line graph of humidity % per day. 
        Use map to combine 9am and 3pm values into one average value.

        :param location: The location you want to graph.
        '''
        # Filter by location
        location_data = self.__data_frame.filter(f"Location = '{location}'")
        # Calculate average humidity directly in Spark
        humidity_data = location_data.withColumn(
            "AvgHumidity", 
            (col("Humidity9am") + col("Humidity3pm")) / 2
        )
        # Select just the computed column for plotting
        tempDF = humidity_data.select("AvgHumidity").toPandas()
        plt.figure(figsize=(10, 5))
        plt.plot(tempDF.index, tempDF['AvgHumidity'], marker='', linestyle='-', color='blue')
        plt.xlabel('Days')
        plt.ylabel('Humidity (percent)')
        plt.title(f'Humidity in {location} (Daily)')
        plt.grid()
        plt.legend() 
        plt.show()

    def daily_temperature(self, location):
        '''
        Create a line graph of temperature per day. 
        Use map to combine 9am and 3pm values into one average value.

        :param location: The location you want to graph.
        '''
        # Filter by location
        location_data = self.__data_frame.filter(f"Location = '{location}'")
        # Calculate average humidity directly in Spark
        humidity_data = location_data.withColumn(
            "AvgTemp", 
            (col("Temp9am") + col("Temp3pm")) / 2
        )
        # Select just the computed column for plotting
        tempDF = humidity_data.select("AvgTemp").toPandas()
        plt.figure(figsize=(10, 5))
        plt.plot(tempDF.index, tempDF['AvgTemp'], marker='', linestyle='-', color='blue')
        plt.xlabel('Days')
        plt.ylabel('Temperature (Celsius)')
        plt.title(f'Temperature in {location} (Daily)')
        plt.grid()
        plt.legend()
        plt.show()

    def windy_days(self, location):
        """
        Create a bar chart of days that are windier than 25 km/h and less windy.
        Use filter to count how many days are and aren't windier than 25 km/h.

        :param location: The location you want to graph.
        """
        location_data = self.__data_frame.filter(f"Location = '{location}'")
        # Calculate average wind speed directly in Spark
        wind_data = location_data.withColumn(
            "AvgWindSpeed", 
            (col("WindSpeed9am") + col("WindSpeed3pm")) / 2
        )
        
        # Count windy and non-windy days directly in Spark
        wind_counts = wind_data.agg(
            count(when(col("AvgWindSpeed") >= 25, True)).alias("windy_count"),
            count(when(col("AvgWindSpeed") < 25, True)).alias("non_windy_count")
        ).collect()[0]
        
        # Extract counts from Spark result
        windy_count = wind_counts["windy_count"]
        non_windy_count = wind_counts["non_windy_count"]
        categories = ['Windy Days (≥25 km/h)', 'Non-Windy Days (<25 km/h)']
        # Create Bar Chart
        plt.figure(figsize=(10,5))
        plt.bar(categories, [windy_count, non_windy_count], color=['blue', 'gray'])
        plt.xlabel('Wind Condition')
        plt.title('Comparison of Windy and Non-Windy Days')
        plt.show()
