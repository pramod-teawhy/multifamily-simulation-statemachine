from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from agent import UnitAgent
from datetime import datetime
from dateutil.relativedelta import relativedelta
from collections import Counter
import random
import logging

def get_OC_count(model):
    status = [agent.sm.params["OccupancyStatus"] for agent in model.schedule.agents]
    return Counter(status)["OC"]


def get_VA_count(model):
    status = [agent.sm.params["OccupancyStatus"] for agent in model.schedule.agents]
    return Counter(status)["VA"]


def get_VL_count(model):
    status = [agent.sm.params["OccupancyStatus"] for agent in model.schedule.agents]
    return Counter(status)["VL"]


def get_NA_count(model):
    status = [agent.sm.params["OccupancyStatus"] for agent in model.schedule.agents]
    return Counter(status)["NA"]


def get_NL_count(model):
    status = [agent.sm.params["OccupancyStatus"] for agent in model.schedule.agents]
    return Counter(status)["NL"]


def get_MTM_count(model):
    matches = [agent for agent in model.schedule.agents
               if agent.sm.params["LeaseEndDateCurrentLease"] is not None and agent.sm.params["RenewalStatus"] == 'Undecided' and agent.sm.params["LeaseEndDateCurrentLease"]  < agent.sm.params["SimulationDate"]]
    return len(matches)


class UnitModel(Model):
    def __init__(self, N, configs, LeasesPerWeek, ApplicationToMoveInLeadDays,
                 RenewalProbability, AverageNoticeLeadDays, MakeReadyDays,
                 MarketRentGrowth, SimulationDate):
        simulation_params = {
            "LeasesPerWeek": LeasesPerWeek,
            "ApplicationToMoveInLeadDays": ApplicationToMoveInLeadDays,
            "RenewalProbability": RenewalProbability,
            "AverageNoticeLeadDays": AverageNoticeLeadDays,
            "MakeReadyDays": MakeReadyDays,
            "MarketRentGrowth": MarketRentGrowth,
            "SimulationDate": SimulationDate
        }

        width=20
        height=20

        self.running = True
        to_date = lambda s: datetime.strptime(s, '%a, %d %b %Y %H:%M:%S GMT')
        self.SimulationDate = to_date(simulation_params['SimulationDate'])
        self.DayInWeek = 0
        self.LeasesPerWeek = simulation_params["LeasesPerWeek"]
        self.AvailableLeasePerWeek = self.LeasesPerWeek

        self.num_agents = N
        self.schedule = RandomActivation(self)

        self.grid = MultiGrid(width, height, True)

        for i in range(self.num_agents):
            a = UnitAgent(i, self, configs[i], simulation_params)
            self.schedule.add(a)
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        self.data_collector = DataCollector(
            model_reporters={"Occupied": get_OC_count,
                             "Vacant Available": get_VA_count,
                             "Vacant Leased": get_VL_count,
                             "Notice Available": get_NA_count,
                             "Notice Leased": get_NL_count,
                             "Month to Month": get_MTM_count,
                             }
        )


    def step(self):
        self.data_collector.collect(self)
        self.SimulationDate += relativedelta(days=1)
        self.DayInWeek = self.DayInWeek + 1 if self.DayInWeek < 7 else 0
        if self.DayInWeek == 0:
            self.AvailableLeasePerWeek = self.LeasesPerWeek
        logging.info(f"Weekday: {self.DayInWeek} Avl Leases Per Week: {self.AvailableLeasePerWeek} ")

        self.schedule.step()


def run_simulation(days, num_units, configs, simulation_params):
    m = UnitModel(num_units, configs, **simulation_params)
    for i in range(days):
        m.step()
