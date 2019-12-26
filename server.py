from mesa.visualization.modules import ChartModule
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from model import UnitModel

chart_OC = ChartModule([{"Label": "Occupied",
                        "Color": "Green"}, {"Label": "Notice Available",
                        "Color": "Yellow"}, {"Label": "Notice Leased",
                        "Color": "Blue"}],
                       data_collector_name='data_collector')

chart_VA = ChartModule([{"Label": "Vacant Available",
                        "Color": "Black"}],
                       data_collector_name='data_collector')

chart_VL = ChartModule([{"Label": "Vacant Leased",
                        "Color": "Black"}],
                       data_collector_name='data_collector')

chart_NA = ChartModule([{"Label": "Notice Available",
                        "Color": "Black"}],
                       data_collector_name='data_collector')

chart_NL = ChartModule([{"Label": "Notice Leased",
                        "Color": "Black"}],
                       data_collector_name='data_collector')

chart_MTM = ChartModule([{"Label": "Month to Month",
                        "Color": "Black"}],
                        data_collector_name='data_collector')

def agent_portrayal(agent):
    
    OccupancyStatus_Color_Mapping = {
        "OC": "green",
        "NA": "yellow",
        "NL": "blue",
        "VL": "orange",
        "VA": "red"
    }
    
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "Layer": 0,
                 "r": 0.5}
    
    if agent.sm.params['OccupancyStatus'] in OccupancyStatus_Color_Mapping.keys():
            portrayal["Color"] = OccupancyStatus_Color_Mapping[agent.sm.params['OccupancyStatus']]

    return portrayal

grid = CanvasGrid(agent_portrayal, 20, 20, 500, 500)

simulation_controls = {
    "LeasesPerWeek": UserSettableParameter('slider', 'Leases Per Week', 3, 0, 10, 1),
    "ApplicationToMoveInLeadDays": UserSettableParameter('slider', 'Application to MoveIn Lead Days', 14, 1, 30, 1),
    "RenewalProbability": UserSettableParameter('slider', 'Renewal Probability', 0.5, 0, 1, 0.01),
    "AverageNoticeLeadDays": UserSettableParameter('slider', 'Average Notice Lead Days', 30, 1, 180, 1),
    "MakeReadyDays": UserSettableParameter('slider', 'Make Ready Days', 5, 5, 15, 1),
    "MarketRentGrowth": UserSettableParameter('slider', 'Market Rent Growth/Yr', 0.03, 0, 1, 0.01),
}

n_slider = UserSettableParameter('slider', 'Number of agents', 100, 2, 200, 1)

def run_server(simulation_date, configs):

    server = ModularServer(UnitModel,
                           [grid, chart_OC, chart_VA, chart_VL, chart_NA, chart_NL, chart_MTM],
                           "Unit Model",
                           {"N": n_slider, "configs": configs,
                            **simulation_controls, "SimulationDate": simulation_date})

    server.launch()
