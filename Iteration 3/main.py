import weather_data as wd

def main():
    """
    The main driver of the program.
    """
    weather_data = wd.WeatherData()
    weather_data.summary()

if __name__ == "__main__":
    main()
