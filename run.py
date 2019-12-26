import json
import argparse
from model import run_simulation
from server import run_server

parser = argparse.ArgumentParser()
parser.add_argument('mode', choices=["headless", "UI"], type=str, help='Simulation mode')
parser.add_argument('-n', help='Number of days to simulate', type=int)

args = parser.parse_args()

parser = argparse.ArgumentParser()


with open('property_details.json', 'r') as fh:
    items = json.loads(fh.read())

configs = items['_items']

simulation_params = {
    "RenewalProbability": 0.5,
    "AverageNoticeLeadDays": 30,
    "MakeReadyDays": 5,
    "SimulationDate": configs[0]['ReportDate'], #"Thu, 01 Jan 1970 00:00:00 GMT",
    "LeasesPerWeek": 10,
    "ApplicationToMoveInLeadDays": 14,
    "MarketRentGrowth": 0.03,
}

NUM_UNITS = 100

if args.mode == "headless":
    if args.n is None:
        parser.error("headless mode requires -n <num_simulation_days>")
    else:
        run_simulation(days=args.n, num_units=NUM_UNITS,
                       configs=configs, simulation_params=simulation_params)
else:
    run_server(simulation_date=simulation_params['SimulationDate'], configs=configs)
