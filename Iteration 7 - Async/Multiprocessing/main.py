from itertools import islice
import weather_data as wd
import asyncio
import time

async def main():
    """
    The main driver of the program.
    """
    file_list = ['./Data/Weather Training Data copy.csv', './Data/Weather Test Data.csv', './Data/Weather Training Data.csv', './Data/Weather Test Data.csv']
    #Async
    start_time = time.time()
    weather_data_instances = await wd.WeatherData.create_multiple_async(file_list)
    end_time = time.time()
    print(f"Async loading completed in {end_time - start_time:.2f} seconds")
    #Sync
    start_time = time.time()
    weather_data_instances = []
    for file in file_list:
        weather_data_instances.append(wd.WeatherData(file))
    end_time = time.time()
    print(f"Sync loading completed in {end_time - start_time:.2f} seconds")

    weather_data = wd.WeatherData()
    weather_data.summary()
    for row in islice(weather_data.iter_rows(), 5):
        print(row)
    # Multi Processing
    # Faster version because it only spawns one process pool
    weather_data.bulk_process_graphs(['Albury', 'Sydney', 'Cobar', 'Moree'])
    # Second parameter lets you specify which methods you want in the process pool
    # weather_data.bulk_process_weather_data(['Albury', 'Sydney', 'Cobar', 'Moree'], ['daily_rain', 'weekly_rain'])

    # Slower, creates multiple process pools. Only use these methods if you are using a single method
    # weather_data.daily_rain(['Albury', 'Sydney', 'Cobar', 'Moree'])
    # weather_data.weekly_rain(['Albury', 'Sydney', 'Cobar', 'Moree'])
    # weather_data.daily_humidity(['Albury', 'Sydney', 'Cobar', 'Moree'])
    # weather_data.daily_temperature(['Albury', 'Sydney', 'Cobar', 'Moree'])
    # weather_data.windy_days(['Albury', 'Sydney', 'Cobar', 'Moree'])

if __name__ == "__main__":
    asyncio.run(main())
