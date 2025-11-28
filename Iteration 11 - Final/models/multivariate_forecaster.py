import joblib
import json
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from datetime import datetime, timedelta

class MultivariateForecaster:
    """
    A class for generating multivariate weather forecasts using pre-trained models.
    
    This class loads pre-trained models and metadata to generate forecasts for all
    weather variables simultaneously for a specified number of days.
    
    Attributes:
        metadata (dict): Dictionary containing model metadata for each location
        db_path (str): Path to the SQLite database
        engine: SQLAlchemy engine for database connection
    """
    
    def __init__(self, metadata_path='./models/multivariate_model_metadata.json', db_path='weather.db'):
        """
        Initializer for the MultivariateForecaster class.
        
        Loads model metadata from a JSON file and sets up the database connection.
        
        :param metadata_path: Path to the metadata JSON file
        :param db_path: Path to the SQLite database
        """
        # Load metadata
        with open(metadata_path, 'r') as f:
            self.metadata = json.load(f)
        
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')
    
    def get_available_locations(self):
        """
        Returns a list of locations available for forecasting.
        
        :return: A list of location names as strings
        """
        return list(self.metadata.keys())
    
    def get_available_columns(self, location):
        """
        Returns a list of columns available for the specified location.
        
        :param location: The location to get columns for
        :return: A list of column names as strings
        :raises ValueError: If the location is not found in metadata
        """
        if location not in self.metadata:
            raise ValueError(f"Location '{location}' not found in metadata")
        return self.metadata[location]['available_columns']
    
    def get_latest_data(self, location, n_lags=14):
        """
        Gets the latest data for all columns for a specific location.
        
        Retrieves the most recent data points from the database for the specified location,
        which will be used as input for the forecasting model.
        
        :param location: The location to fetch data for
        :param n_lags: Number of days of historical data to fetch
        :return: Dictionary with column names as keys and lists of values as values
        :raises ValueError: If the location is not found in metadata
        """
        if location not in self.metadata:
            raise ValueError(f"Location '{location}' not found in metadata")
        
        # Get available columns and their DB mappings
        columns = self.metadata[location]['available_columns']
        db_mappings = self.metadata[location]['db_column_mapping']
        
        # Prepare SQL query with all needed columns
        db_cols = [db_mappings[col] for col in columns if db_mappings[col] is not None]
        column_str = ', '.join(db_cols)
        
        query = f"""
        SELECT {column_str}
        FROM weather
        WHERE location = '{location}'
        ORDER BY id DESC
        LIMIT {n_lags}
        """
        
        # Execute query
        results = pd.read_sql(query, self.engine)
        
        # Reorganize data by column
        latest_data = {}
        for col in columns:
            db_col = db_mappings[col]
            if db_col in results.columns:
                # Get values and reverse them (oldest first)
                values = results[db_col].tolist()
                values.reverse()
                latest_data[col] = values
        
        return latest_data
    
    def forecast(self, location, days=7):
        """
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
        """
        if location not in self.metadata:
            raise ValueError(f"Location '{location}' not found")
        
        # Get model info
        model_info = self.metadata[location]
        n_lags = model_info['n_lags']
        columns = model_info['available_columns']
        
        # Get the latest data for all columns
        latest_data = self.get_latest_data(location, n_lags)
        
        # Check if we have enough data
        for col, values in latest_data.items():
            if len(values) < n_lags:
                raise ValueError(f"Not enough data for {col}. Need {n_lags} days but only have {len(values)}.")
        
        # Load the model
        model = joblib.load(model_info['model_path'])
        
        # Prepare input for the model - flatten the window of all variables
        input_window = []
        for i in range(n_lags):
            day_values = [latest_data[col][i] for col in columns]
            input_window.append(day_values)
        
        # Initialize forecast results
        forecasts = {col: [] for col in columns}
        
        # Generate forecasts for the specified number of days
        for _ in range(days):
            # Flatten the input window for the model
            model_input = np.array(input_window).flatten().reshape(1, -1)
            
            # Make prediction for all variables for the next day
            prediction = model.predict(model_input)[0]
            
            # Store predictions by column
            for i, col in enumerate(columns):
                forecasts[col].append(prediction[i])
            
            # Update input window: remove oldest day, add new prediction as a list
            input_window.pop(0)
            input_window.append(prediction)
        
        # Generate dates for the forecast period
        today = datetime.now().date()
        dates = [(today + timedelta(days=i+1)).strftime('%Y-%m-%d') for i in range(days)]
        
        # Format results
        results = {
            'dates': dates,
            'location': location,
            'forecasts': {}
        }
        
        # Add each column's forecast with its proper units
        for col in columns:
            results['forecasts'][col] = {
                'values': forecasts[col],
                'units': self._get_column_units(col),
                'stats': model_info['train_stats'][col]
            }
        
        return results
    
    def _get_column_units(self, column):
        """
        Returns appropriate units for a weather variable based on its name.
        
        :param column: The name of the weather variable column
        :return: String representing the units for the given column
        """
        if 'temp' in column.lower():
            return '°C'
        elif 'rain' in column.lower():
            return 'mm'
        elif 'wind' in column.lower() and 'speed' in column.lower():
            return 'km/h'
        elif 'humidity' in column.lower():
            return '%'
        elif 'pressure' in column.lower():
            return 'hPa'
        else:
            return ''


# Example usage if run directly
if __name__ == "__main__":
    forecaster = MultivariateForecaster()
    
    print("Available locations:")
    locations = forecaster.get_available_locations()
    print(locations)
    
    # Example for Sydney if available
    if 'Sydney' in locations:
        print("\nColumns available for Sydney:")
        columns = forecaster.get_available_columns('Sydney')
        print(columns)
        
        print("\nGenerating 7-day forecast for Sydney...")
        forecast = forecaster.forecast('Sydney')
        
        print(f"\nForecast for {forecast['location']} from {forecast['dates'][0]} to {forecast['dates'][-1]}:")
        
        # Display the first few columns as examples
        example_cols = ['MaxTemp', 'MinTemp', 'Rainfall'] 
        example_cols = [col for col in example_cols if col in forecast['forecasts']]
        
        for col in example_cols:
            print(f"\n{col} ({forecast['forecasts'][col]['units']}):")
            for i, date in enumerate(forecast['dates']):
                value = forecast['forecasts'][col]['values'][i]
                print(f"  {date}: {value:.1f}{forecast['forecasts'][col]['units']}")