# server.py
from model import HarvestModel
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule


def agent_portrayal(agent):
    portrayal = {"Shape": "circle","Filled": "true","Layer": 0,"Color": agent.returnColor(),"r": 1}
    return portrayal

grid = CanvasGrid(agent_portrayal, 100, 100, 500, 500)
chartGini = ChartModule([{"Label": "Gini","Color": "Black"}], data_collector_name='datacollector')
chartFed = ChartModule([{"Label": "Number Fed","Color": "Black"}], data_collector_name='datacollector')


server = ModularServer(HarvestModel, [grid, chartGini, chartFed], "Harvest Model", {"num_agents": 100, "width": 120, "height": 100})

