from itertools import islice
import weather_data as wd

def main():
    """
    The main driver of the program.
    """
    weather_data = wd.WeatherData()
    weather_data.summary()
    for row in islice(weather_data.iter_rows(), 5):
        print(row)

if __name__ == "__main__":
    main()
