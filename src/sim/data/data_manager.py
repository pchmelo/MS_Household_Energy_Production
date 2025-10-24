import os
import pandas as pd

try:
    from .api_manager import api_manager
except ImportError:
    from api_manager import api_manager


class DataManager:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.datafiles_dir = os.path.join(self.base_dir, "datafiles")

        self.price_data_filename = "market_prices.csv"
        self.solar_data_filename = "solar_production.csv"
        self.wind_data_filename = "wind_production.csv"

        
    def start_data_collection(self, date: str):
        self.date = date
        
        date_folder = os.path.join(self.datafiles_dir, date)

        if not os.path.exists(date_folder) or not os.path.isdir(date_folder):
            print(f"Folder for date {date} does not exist")
            api_manager.generate_data(self.date)
            return False
        
        self.get_data_for_date()
        print(f"Solar production: \n{self.df_solar_production.head()}")
        print(f"Wind production: \n{self.df_wind_production.head()}")
        print(f"Market prices: \n{self.df_price_data.head()}")
        return True

    def get_model_data_entry(self, date: str = None, time_stamp: str = ""):
        if time_stamp == "":
            raise ValueError("Time stamp must be provided")
        
        if date is not None:
            self.start_data_collection(date)

        hour, minute = self.parse_timestamp(time_stamp)
        
        price = None
        solar_production = None
        wind_production = None

        return price, solar_production, wind_production

    def get_data_for_date(self):
        self.df_solar_production = pd.read_csv(os.path.join(
            self.datafiles_dir, self.date, self.solar_data_filename))
        self.df_wind_production = pd.read_csv(os.path.join(
            self.datafiles_dir, self.date, self.wind_data_filename))    
        self.df_price_data = pd.read_csv(os.path.join(
            self.datafiles_dir, self.date, self.price_data_filename))
        
    def parse_timestamp(self, timestamp: str):
        hour, minute = map(int, timestamp.split(":"))
        return hour, minute
        

data_manager = DataManager()


if __name__ == "__main__":
    data_manager.start_data_collection("2025-08-25")