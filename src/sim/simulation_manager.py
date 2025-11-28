from sim.data.json_result_manager import json_result_manager
from ast import Dict
from sim.model.model import HEMSModel

class SimulationManager:
    def __init__(self):
        self.model_smart = HEMSModel(agent_type="smart")
        self.model_basic = HEMSModel(agent_type="basic")

    def start_smulation(self, config, df_solar_production=None, df_wind_production=None, df_consumption=None, df_price=None) -> Dict:
        self.pass_configs_to_model(config, df_solar_production, df_wind_production, df_consumption, df_price)
        
        for i in range(self.model_smart.steps):
            self.model_smart.step()

        results = self.model_smart.datacollector.get_model_vars_dataframe()
        json_result_manager.save_to_json_file(results, agent_type="smart")

        for i in range(self.model_basic.steps):
            self.model_basic.step()

        results = self.model_basic.datacollector.get_model_vars_dataframe()
        json_result_manager.save_to_json_file(results, agent_type="basic")

        json_result_manager.calculate_final_results()

        return json_result_manager.final_json_data

    def pass_configs_to_model(self, config, df_solar_production=None, df_wind_production=None, df_consumption=None, df_price=None):
        self.simulation_configs = SimulationConfigs(config, df_solar_production, df_wind_production, df_consumption, df_price)
        self.model_smart.setup_configs(self.simulation_configs)
        self.model_basic.setup_configs(self.simulation_configs)


simulation_manager = SimulationManager()

class SimulationConfigs:
    def __init__(self, config, df_solar_production=None, df_wind_production=None, df_consumption=None, df_price=None):
        self.config = config

        self.selected_date = config.get("selected_date", None)
        self.interval = config.get("interval", None)
        self.battery_max_capacity = config.get("max_capacity", None)

        self.tariff = config.get("tariff", None)
        self.complex_mode = config.get("complex_mode", False)

        self.df_solar_production = df_solar_production
        self.df_wind_production = df_wind_production
        self.df_consumption = df_consumption
        self.df_price = df_price