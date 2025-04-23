"""
Defines a wrapper class for a Pandas Dataframe.
"""
import logging
import pandas
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from functools import reduce
import asyncio
import aiofiles
import os
import sqlite3
from sqlalchemy import create_engine

def setup_logging():
    os.makedirs('./logging', exist_ok=True)
    logging.basicConfig(filename='./logging/logging.log', level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    return logging.getLogger("my_logger")

logger = None

class WeatherData:
    """
    A class to manage and process weather data.

    This class loads weather data from a CSV file, stores it in a pandas DataFrame,
    and provides functionality to extract, graph, and summarize the data.

    Attributes:
        __data_frame: A pandas DataFrame containing weather data.  
        __extracter: An instance of the DataExtracter class used for data visualization and summarization.
    """
    def __init__(self, file : str = None) -> None:
        """
        Initializer for the WeatherData class. Loads weather data from a file and
        setting up helper classes to process data.
        :param file: The name of a file to be read into a dataframe.
        """
        global logger
        if logger is None:
            logger = setup_logging()
        loader = self.__DataLoader(file)
        self.__data_frame = loader.data_frame.set_index('Location')
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
        return await asyncio.gather(*tasks)

    def update_from_database(self, db_path='weather.db'):
        """
        Updates the internal pandas DataFrame with any new data from SQLite database.
        
        This method: Connects to the SQLite database, retrieves all records,
        updates the internal pandas DataFrame, and reinitializes the data extracter with the updated DataFrame
        
        :param db_path: Path to the SQLite database file
        :return: Number of new records added
        """
        try:
            # Connect to SQLite database
            engine = create_engine(f'sqlite:///{db_path}')
            
            # Read database into pandas DataFrame
            db_df = pandas.read_sql('SELECT * FROM weather', engine)
            
            # If database has no data, return
            if db_df.empty:
                logger.warning("Database contains no records")
                return 0
                
            # Convert column names if needed (database might use different naming)
            column_mapping = {
                'location': 'Location',
                'rainfall': 'Rainfall',
                'humidity9am': 'Humidity9am',
                'humidity3pm': 'Humidity3pm',
                'temp9am': 'Temp9am',
                'temp3pm': 'Temp3pm',
                'windspeed9am': 'WindSpeed9am', 
                'windspeed3pm': 'WindSpeed3pm'
            }
            db_df = db_df.rename(columns={v: k for k, v in column_mapping.items() 
                                        if v in db_df.columns})
            
            # Update the internal DataFrame 
            self.__data_frame = db_df.set_index('Location')
            
            # Reinitialize the data extracter with the updated DataFrame
            self.__extracter = DataExtracter(self.__data_frame)
            
            logger.info(f"Successfully updated DataFrame with {len(db_df)} records from database")
            return len(db_df)
        except Exception as e:
            logger.error(f"Error updating from database: {e}")
            return 0

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
        return self.__extracter.daily_rain(location)

    def weekly_rain(self, location):
        """
        Use data extracter to graph weekly rain.

        :param location: The location you want to graph.
        """
        return self.__extracter.weekly_rain(location)

    def daily_humidity(self, location):
        """
        Use data extracter to graph daily humidity

        :param location: The location you want to graph.
        """
        return self.__extracter.daily_humidity(location)

    def daily_temperature(self, location):
        """
        Use data extracter to graph daily temperature

        :param location: The location you want to graph.
        """
        return self.__extracter.daily_temperature(location)

    def windy_days(self, location):
        """
        Use dataextracter to chart windy days.

        :param location: The location you want to graph.
        """
        return self.__extracter.windy_days(location)

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
            if file is None:
                self.data_frame = self.read_database()
            else:
                self.data_frame = self.read_csv(file)

        @staticmethod
        def read_database(db_path='weather.db'):
            """
            Read data directly from a SQLite database into a pandas DataFrame.
            
            :param db_path: Path to the SQLite database file
            :return: A pandas DataFrame containing the data from the database
            """
            weather_data = pandas.DataFrame()
            try:
                # Use SQLAlchemy to connect to the database
                engine = create_engine(f'sqlite:///{db_path}')
                
                # Read database into pandas DataFrame
                weather_data = pandas.read_sql('SELECT * FROM weather', engine)
                
                # Column name mapping from database to expected format
                column_mapping = {
                    'location': 'Location',
                    'rainfall': 'Rainfall',
                    'humidity9am': 'Humidity9am',
                    'humidity3pm': 'Humidity3pm',
                    'temp9am': 'Temp9am',
                    'temp3pm': 'Temp3pm',
                    'windspeed9am': 'WindSpeed9am', 
                    'windspeed3pm': 'WindSpeed3pm'
                }
                
                # Rename columns as needed
                weather_data = weather_data.rename(columns={k: v for k, v in column_mapping.items() 
                                                if k in weather_data.columns})
                logger.info(f"Successfully loaded {len(weather_data)} records from database")
            except sqlite3.Error as e:
                logger.error(f"SQLite error: {e}")
            except Exception as e:
                logger.error(f"Error reading from database: {e}")
            return weather_data

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
                file_name = "./Data/Weather Training Data.csv"
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
                file_name = "./Data/Weather Training Data.csv"
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
    Helper class to extract/summarize data from a pandas DataFrame.

    This class is responsible for extracting, graphing, and summarizing data from a pandas DataFrame.
    """
    def __init__(self, data_frame) -> None:
        """
        Initializes the DataExtracter class with a pandas DataFrame.

        :param data_frame: The DataFrame containing weather data. 
        """
        self.__data_frame = data_frame

    def summary(self) -> pandas.DataFrame:
        """
        Generates a summary for data.

        Uses Pandas describe() method to provide information about the data.
        :return: A DataFrame containing summary statistics. 
        """
        if len(self.__data_frame) == 0:
            logger.warning("Data frame is empty, no summary available.")
            return self.__data_frame
        return self.__data_frame.describe()

    def iter_rows(self):
        """
        Create a generator to iterate over rows of our DataFrame.

        :yeild: A row of the DataFrame. 
        """
        for row in self.__data_frame.iterrows():
            yield row

    def daily_rain(self, location):
        """
        Create a line graph of how much rain there is per day in a certain location.

        :param location: The location you want to graph.
        """
        tempDF = self.__data_frame.loc[location, ['Rainfall']].reset_index()
        fig = plt.figure(figsize=(10, 5))
        plt.plot(tempDF.index, tempDF['Rainfall'], marker='', linestyle='-', color='blue')
        plt.xlabel('Days')
        plt.ylabel('Rainfall (mm)')
        plt.title(f'Rainfall in {location} Over Time')
        plt.grid()
        return fig

    def weekly_rain(self, location):
        '''
        Create a line graph of how much rain there is per week in a certain location. 
        Use reduce to get an average rain value for the week.

        :param location: The location you want to graph.
        '''
        tempDF = self.__data_frame.loc[location, ['Rainfall']].reset_index(drop=True)
        rainfall = tempDF['Rainfall'].tolist()
        def weekly_average(data):
            result = []
            window = 7
            # Process data in weekly chunks
            for i in range(0, len(data), window):
                week_values = data[i:i+window]
                avg = reduce(lambda a,b: a + b, week_values) / len(week_values)
                result.extend([avg] * len(week_values)) # keep the column the same length
            return result
        tempDF['Rainfall_Smoothed'] = weekly_average(rainfall)
        tempDF['Rainfall_Smoothed'].interpolate(inplace=True)  # Smooth out missing values

        fig = plt.figure(figsize=(10, 5))
        plt.plot(tempDF.index, tempDF['Rainfall_Smoothed'], marker='', linestyle='-', label='7-day Avg', color='blue')
        plt.xlabel('Days')
        plt.ylabel('Rainfall (mm)')
        plt.title(f'Smoothed Rainfall in {location} (Weekly)')
        plt.grid()
        plt.legend()
        return fig

    
    def daily_humidity(self, location):
        '''
        Create a line graph of humidity % per day. 
        Use map to combine 9am and 3pm values into one average value.

        :param location: The location you want to graph.
        '''
        # Combine the 9am and 3pm values into an average value
        tempDF = self.__data_frame.loc[location, ['Humidity9am', 'Humidity3pm']].reset_index(drop=True)
        tempDF['AvgHumidity'] = list(map(lambda x: (x[0] + x[1]) / 2, zip(tempDF['Humidity9am'], tempDF['Humidity3pm'])))
        fig = plt.figure(figsize=(10, 5))
        plt.plot(tempDF.index, tempDF['AvgHumidity'], marker='', linestyle='-', color='blue')
        plt.xlabel('Days')
        plt.ylabel('Humidity (percent)')
        plt.title(f'Humidity in {location} (Daily)')
        plt.grid()
        plt.legend() 
        return fig

    def daily_temperature(self, location):
        '''
        Create a line graph of temperature per day. 
        Use map to combine 9am and 3pm values into one average value.

        :param location: The location you want to graph.
        '''
        # Combine the 9am and 3pm values into an average value
        tempDF = self.__data_frame.loc[location, ['Temp9am', 'Temp3pm']].reset_index(drop=True)
        tempDF['AvgTemp'] = list(map(lambda x: (x[0] + x[1]) / 2, zip(tempDF['Temp9am'], tempDF['Temp3pm'])))
        fig = plt.figure(figsize=(10, 5))
        plt.plot(tempDF.index, tempDF['AvgTemp'], marker='', linestyle='-', color='blue')
        plt.xlabel('Days')
        plt.ylabel('Temperature (Celsius)')
        plt.title(f'Temperature in {location} (Daily)')
        plt.grid()
        plt.legend()
        return fig

    def windy_days(self, location):
        """
        Create a bar chart of days that are windier than 25 km/h and less windy.
        Use filter to count how many days are and aren't windier than 25 km/h.

        :param location: The location you want to graph.
        """
        tempDF = self.__data_frame.loc[location, ['WindSpeed9am', 'WindSpeed3pm']].reset_index(drop=True)
        tempDF['AvgWindSpeed'] = list(map(lambda x: (x[0] + x[1]) / 2, zip(tempDF['WindSpeed9am'], tempDF['WindSpeed3pm'])))
        windy_days = tempDF.iloc[list(filter(lambda i: tempDF['AvgWindSpeed'].iloc[i] >= 25, range(len(tempDF))))]
        non_windy_days = tempDF.iloc[list(filter(lambda i: tempDF['AvgWindSpeed'].iloc[i] < 25, range(len(tempDF))))]
        windy_count = len(windy_days)
        non_windy_count = len(non_windy_days)
        categories = ['Windy Days (≥25 km/h)', 'Non-Windy Days (<25 km/h)']
        # Create Bar Chart
        fig = plt.figure(figsize=(10,5))
        plt.bar(categories, [windy_count, non_windy_count], color=['blue', 'gray'])
        plt.xlabel('Wind Condition')
        plt.title('Comparison of Windy and Non-Windy Days')
        return fig