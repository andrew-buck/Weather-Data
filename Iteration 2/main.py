from weather_data import weather_data as wd

def main():
    """
    The main driver of the program
    """
    weather_data = wd.read_csv()
    print(weather_data.describe())

if __name__ == "__main__":
    main()
