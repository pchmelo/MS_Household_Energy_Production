import os
from dotenv import load_dotenv

from mesa import Model
from mesa.datacollection import DataCollector

from sim.agent.agent_base import HEMSAgent

load_dotenv()
interval_str = os.getenv("INTERVAL", "1,0")
hour_interval, minute_interval = map(int, interval_str.split(","))
max_capacity = int(os.getenv("MAX_CAPACITY"))

def get_steps():
    return 24 * 60 // (hour_interval * 60 + minute_interval)

def update_time(current_time):
    hour, minute = current_time

    minute += minute_interval
    hour += hour_interval

    if minute >= 60:
        minute -= 60
        hour += 1
    if hour >= 24:
        hour -= 24

    return (hour, minute)

def format_actions(actions):
    """Format actions list into a string: 'key: value, key: value, ...'"""
    if not actions:
        return "No actions"
    
    action_strings = []
    for action_dict in actions:
        for key, value in action_dict.items():
            action_strings.append(f"{key}: {value:.4f}")
    
    return ", ".join(action_strings)

class HEMSModel(Model):
    def __init__(self, agent_type="smart"):
        super().__init__()

        # Initialize model parameters
        self.steps = get_steps()
        self.battery_capacity = max_capacity
        self.cur_capacity = 0.0
        self.actions = []
        self.price = 0.0
        self.solar_production = 0.0
        self.wind_production = 0.0
        self.consumption = 0.0
        self.old_capacity = 0.0
        self.cur_hour = (0, 0)

        # Initialize goal
        self.balance = 0.0

        # Create agent
        agent = HEMSAgent(self, agent_type)
        self.agents.add(agent)

        # Data collector setup
        self.datacollector = DataCollector(
            model_reporters={
                "Current_Hour": lambda m: f"{m.cur_hour[0]:02}:{m.cur_hour[1]:02}",
                "Solar_Production": lambda m: m.solar_production,
                "Wind_Production": lambda m: m.wind_production,
                "Consumption": lambda m: m.consumption,
                "Current_Capacity": lambda m: m.old_capacity,
                "Price": lambda m: m.price,
                "Actions": lambda m: format_actions(m.actions),
                "Balance": lambda m: m.balance,
                "New_Capacity": lambda m: m.cur_capacity
            }
        )

    def step(self):
        self.cur_hour = update_time(self.cur_hour)
        self.agents.do("step")
        self.datacollector.collect(self)
