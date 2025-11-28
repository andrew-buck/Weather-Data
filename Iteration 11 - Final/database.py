import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, Float, String, Boolean, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

def create_weather_database():
    """
    Creates a SQLite database from the Weather Training Data CSV file.
    """
    # Set up database connection
    db_path = os.path.join(os.path.dirname(__file__), 'weather.db')
    engine = create_engine(f'sqlite:///{db_path}')
    Base = declarative_base()
    
    # Define Weather table model with all columns
    class Weather(Base):
        __tablename__ = 'weather'
        
        id = Column(Integer, primary_key=True)
        row_id = Column(String)
        location = Column(String, index=True)
        min_temp = Column(Float)
        max_temp = Column(Float)
        rainfall = Column(Float)
        evaporation = Column(Float)
        sunshine = Column(Float)
        wind_gust_dir = Column(String)
        wind_gust_speed = Column(Float)
        wind_dir_9am = Column(String)
        wind_dir_3pm = Column(String)
        windspeed9am = Column(Float)
        windspeed3pm = Column(Float)
        humidity9am = Column(Float)
        humidity3pm = Column(Float)
        pressure9am = Column(Float)
        pressure3pm = Column(Float)
        cloud9am = Column(Float)
        cloud3pm = Column(Float)
        temp9am = Column(Float)
        temp3pm = Column(Float)
        rain_today = Column(String)
        rain_tomorrow = Column(Float)

    # Create tables
    Base.metadata.create_all(engine)
    
    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Load CSV data
    data_path = "./Data/Weather Training Data.csv"
    try:
        weather_df = pd.read_csv(data_path)
        print(f"Loaded {len(weather_df)} records from CSV.")
        
        # Convert DataFrame to list of dictionaries
        weather_records = []
        for _, row in weather_df.iterrows():
            # Handle potential missing values
            record = Weather(
                row_id=row.get('row ID', None),
                location=row.get('Location', None),
                min_temp=row.get('MinTemp', None),
                max_temp=row.get('MaxTemp', None),
                rainfall=row.get('Rainfall', None),
                evaporation=row.get('Evaporation', None),
                sunshine=row.get('Sunshine', None),
                wind_gust_dir=row.get('WindGustDir', None),
                wind_gust_speed=row.get('WindGustSpeed', None),
                wind_dir_9am=row.get('WindDir9am', None),
                wind_dir_3pm=row.get('WindDir3pm', None),
                windspeed9am=row.get('WindSpeed9am', None),
                windspeed3pm=row.get('WindSpeed3pm', None),
                humidity9am=row.get('Humidity9am', None),
                humidity3pm=row.get('Humidity3pm', None),
                pressure9am=row.get('Pressure9am', None),
                pressure3pm=row.get('Pressure3pm', None),
                cloud9am=row.get('Cloud9am', None),
                cloud3pm=row.get('Cloud3pm', None),
                temp9am=row.get('Temp9am', None),
                temp3pm=row.get('Temp3pm', None),
                rain_today=row.get('RainToday', None),
                rain_tomorrow=row.get('RainTomorrow', None)
            )
            weather_records.append(record)
        
        # Insert records into the database
        session.add_all(weather_records)
        session.commit()
        print(f"Successfully inserted {len(weather_records)} records into database.")
        
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == '__main__':
    create_weather_database()