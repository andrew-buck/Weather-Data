"""
Defines a wrapper class for a Pandas Dataframe.
"""
import logging
import pandas
import matplotlib.pyplot as plt
from functools import reduce
logging.basicConfig(filename='logging/logging.log', level=logging.INFO,
                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("my_logger")

class WeatherData:
    """
    A class to manage and process weather data.

    This class loads weather data from a CSV file, stores it in a Pandas DataFrame,
    and provides functionality to extract and summarize the data.

    Attributes:
        __data_frame (pandas.DataFrame): A DataFrame containing weather data.
        __extracter (WeatherData.__DataExtracter): An instance of the private helper class 
                                                   DataExtracter used for data summarization.
    """
    def __init__(self, file : str = None) -> None:
        """
        Initializer for the WeatherData class. Loads weather data from a file and
        setting up helper classes to process data.
        :param file: The name of a file to be read into a dataframe.
        """
        loader = self.__DataLoader(file) # Currently is only used to give us the Data Frame,
        # not needed as an attribute
        self.__data_frame = loader.data_frame.set_index('Location')
        self.__extracter = self.__DataExtracter(self.__data_frame)

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
        Use data extracters generator to iterate over rows of our Pandas DataFrame.

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

    class __DataExtracter:
        """
        Private helper class to extract/summarize data from a pandas DataFrame.

        This class provides functionality to generate a summary of data using pandas
        build in methods. 
        """
        def __init__(self, data_frame : pandas.DataFrame) -> None:
            """
            Initializes the DataExtracter class with a Pandas DataFrame.

            :param data_frame: The DataFrame containing weather data. 
            """
            self.__data_frame = data_frame

        def summary(self) -> pandas.DataFrame:
            """
            Generates a summary for data.

            Uses Pandas describe() method to provide information about the data.
            :return: A DataFrame containing summary statistics. 
            """
            if self.__data_frame.empty:
                logger.warning("Data frame is empty, no summary available.")
                return self.__data_frame
            return self.__data_frame.describe()

        def iter_rows(self):
            """
            Create a generator to iterate over rows of our Pandas DataFrame.

            :yeild: A row of the Pandas DataFrame. 
            """
            for row in self.__data_frame.iterrows():
                yield row

        def daily_rain(self, location):
            """
            Create a line graph of how much rain there is per day in a certain location.

            :param location: The location you want to graph.
            """
            tempDF = self.__data_frame.loc[location, ['Rainfall']].reset_index()
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
            # Combine the 9am and 3pm values into an average value
            tempDF = self.__data_frame.loc[location, ['Humidity9am', 'Humidity3pm']].reset_index(drop=True)
            tempDF['AvgHumidity'] = list(map(lambda x: (x[0] + x[1]) / 2, zip(tempDF['Humidity9am'], tempDF['Humidity3pm'])))
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
            # Combine the 9am and 3pm values into an average value
            tempDF = self.__data_frame.loc[location, ['Temp9am', 'Temp3pm']].reset_index(drop=True)
            tempDF['AvgTemp'] = list(map(lambda x: (x[0] + x[1]) / 2, zip(tempDF['Temp9am'], tempDF['Temp3pm'])))
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
            tempDF = self.__data_frame.loc[location, ['WindSpeed9am', 'WindSpeed3pm']].reset_index(drop=True)
            tempDF['AvgWindSpeed'] = list(map(lambda x: (x[0] + x[1]) / 2, zip(tempDF['WindSpeed9am'], tempDF['WindSpeed3pm'])))
            windy_days = tempDF.iloc[list(filter(lambda i: tempDF['AvgWindSpeed'].iloc[i] >= 25, range(len(tempDF))))]
            non_windy_days = tempDF.iloc[list(filter(lambda i: tempDF['AvgWindSpeed'].iloc[i] < 25, range(len(tempDF))))]
            windy_count = len(windy_days)
            non_windy_count = len(non_windy_days)
            categories = ['Windy Days (≥25 km/h)', 'Non-Windy Days (<25 km/h)']
            # Create Bar Chart
            plt.figure(figsize=(10,5))
            plt.bar(categories, [windy_count, non_windy_count], color=['blue', 'gray'])
            plt.xlabel('Wind Condition')
            plt.title('Comparison of Windy and Non-Windy Days')
            plt.show()
