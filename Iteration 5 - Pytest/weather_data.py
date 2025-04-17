"""
Defines a wrapper class for a Pandas Dataframe.
"""
import logging
import pandas
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
        self.__data_frame = loader.data_frame
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
