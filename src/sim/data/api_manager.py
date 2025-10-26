import requests
from typing import Dict
import os
import pandas as pd

class APIManager:
    BASE_URL = "https://servicebus.ren.pt/datahubapi"

    def __init__(self, lang = "en-US"):
        self.lang = lang
        self.session = requests.Session()

        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.datafiles_dir = os.path.join(self.base_dir, "datafiles")
        
        # Add filenames
        self.price_data_filename = "market_prices.csv"
        self.solar_data_filename = "solar_production.csv"
        self.wind_data_filename = "wind_production.csv"

    def _make_request(self, endpoint: str, params: Dict) -> Dict:
        params["culture"] = self.lang
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao consultar API: {e}")
        return None    
    
    def get_daily_price(self, date: str):
        data = self._make_request(
            "electricity/ElectricityMarketPricesDaily",
            {"date": date}
        )
        return data
    
    def get_daily_production_breakdown(self, date: str):
        data = self._make_request(
            "electricity/ElectricityProductionBreakdownDaily",
            {"date": date}
        )
        return data
    
    def generate_data(self, date: str):
        price_data = self.get_daily_price(date)
        production_data = self.get_daily_production_breakdown(date)
        
        folder_path = os.path.join(self.datafiles_dir, date)
        os.makedirs(folder_path, exist_ok=True)

        self.gen_market_data(price_data, folder_path)
        self.gen_production_data(production_data, folder_path)


    def gen_production_data(self, data: Dict, folder_path: str):
        time_unit = data.get("xAxis", {}).get("title", {}).get("text")
        time_series = data.get("xAxis", {}).get("categories")
        
        production_unit = data.get("yAxis", {}).get("title", {}).get("text")
        production_series_list = data.get("series", [])
        solar_series = []
        wind_series = []

        skip_flag = False
        for series in production_series_list:
            source = series.get("name")

            if source == "Solar":
                solar_series = series.get("data", [])
                if skip_flag:
                    break
                skip_flag = True

            if source == "Wind":
                wind_series = series.get("data", [])
                if skip_flag:
                    break
                skip_flag = True
        
        # Create DataFrames
        df_solar = pd.DataFrame({
            f"Time ({time_unit})": time_series,
            f"Production ({production_unit})": solar_series
        })

        df_wind = pd.DataFrame({
            f"Time ({time_unit})": time_series,
            f"Production ({production_unit})": wind_series
        })

        # Save to CSV
        solar_csv_path = os.path.join(folder_path, self.solar_data_filename)
        wind_csv_path = os.path.join(folder_path, self.wind_data_filename)

        production_col = f"Production ({production_unit})"
        df_solar[[f"Time ({time_unit})", production_col]].to_csv(solar_csv_path, index=False)
        df_wind[[f"Time ({time_unit})", production_col]].to_csv(wind_csv_path, index=False)
        
        print(f"Solar production saved to {solar_csv_path}")
        print(f"Wind production saved to {wind_csv_path}")

        return df_solar, df_wind


    def gen_market_data(self, data: Dict, folder_path: str):
        time_unit = data.get("xAxis", {}).get("title", {}).get("text")
        time_series = data.get("xAxis", {}).get("categories")
        
        production_unit = data.get("yAxis", {}).get("title", {}).get("text")
        price_series_list = data.get("series", [])
        price_series = []

        for series in price_series_list:
            source = series.get("name")
            if source == "PT":
                price_series = series.get("data", [])
                break

        formatted_times = []
        filtered_prices = []
        
        # Find hour 24 value - convert string to int
        hour_24_value = None
        for i, time_val in enumerate(time_series):
            try:
                hour = int(time_val)
                if hour == 24:
                    hour_24_value = price_series[i]
                    break
            except (ValueError, TypeError):
                continue
        
        # Add hour 0 with value from hour 24
        if hour_24_value is not None:
            formatted_times.append("00:00")
            filtered_prices.append(hour_24_value)
        
        # Process all other hours
        for i, time_val in enumerate(time_series):
            try:
                hour = int(time_val)  # Convert string to int
                if hour == 24:  # Skip hour 24
                    continue
                if hour == 0:  # Skip hour 0 if it exists
                    continue
                formatted_times.append(f"{hour:02d}:00")
                filtered_prices.append(price_series[i])
            except (ValueError, TypeError):
                # If it's not a number, keep it as is
                formatted_times.append(str(time_val))
                filtered_prices.append(price_series[i])

        df = pd.DataFrame({
            'Time (Hour)': formatted_times,
            'Price (€/MWh)': filtered_prices
        })
        
        csv_path = os.path.join(folder_path, self.price_data_filename)
        df.to_csv(csv_path, index=False)
        print(f"Market data saved to {csv_path}")
        
        return df

        
api_manager = APIManager()

if __name__ == "__main__":
    date = "2025-01-25"

    print("===========TEST API CALLS============")
    print("Daily Prices:")
    print(api_manager.get_daily_price(date))
    print("\nDaily Production Breakdown:")
    print(api_manager.get_daily_production_breakdown(date))

    print("===========GENERATE DATA============")
    api_manager.generate_data(date)