# model.py
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from mesa import Agent, Model
from mesa.time import RandomActivation
import random
import pandas as pd
import numpy as np

wheat_yields = pd.read_csv("/Users/cliffbekar/Dropbox/Research Material/[1] Paper, inheritance dynamics/Analytics/wheat_yields.csv")
barley_yields = pd.read_csv("/Users/cliffbekar/Dropbox/Research Material/[1] Paper, inheritance dynamics/Analytics/barley_yields.csv")
oat_yields = pd.read_csv("/Users/cliffbekar/Dropbox/Research Material/[1] Paper, inheritance dynamics/Analytics/oat_yields.csv")

wheatyields_mean = wheat_yields.mean().interpolate()
barleyyields_mean = barley_yields.mean().interpolate()
oatyields_mean = oat_yields.mean().interpolate()

wheatyields_sd = wheat_yields.std().interpolate()
barleyyields_sd = barley_yields.std().interpolate()
oatyields_sd = oat_yields.std().interpolate()

class HarvestModel(Model):
    """A model with some number of agents."""
    def __init__(self, num_agents, width, height):
        self.running = True
        self.subsistence = 80
        self.land_holders = ['small_holder','med_holder','large_holder']
        self.wheat_seed_rate = 0.25
        self.wheat_acres_sown = 0.4
        self.barley_seedRate = 0.5
        self.barley_acres_sown = 0.5
        self.oat_acres_sown = 0.05
        self.oat_seedRate = 0.75
        self.tithe = 0.9
        self.year = 0
        self.date = 1211
        self.num_agents = num_agents
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)

        # Create agents
        for i in range(self.num_agents):
            agent = HarvestAgent(i , self)
            self.schedule.add(agent)
            for j in range (agent.parcels):
                self.grid.place_agent(agent , (j , i))

        self.datacollector = DataCollector(
        # a function to call
            model_reporters={"Gini": compute_gini,
                             "Number Fed": count_fed},
        # an agent attribute
            agent_reporters={"land":
                            "land"})

    def step(self):
        self.datacollector.collect(self)
        self.date += 1
        self.schedule.step()


class HarvestAgent(Agent):
    """ An agent with fixed initial land."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.stores = 0
        self.fed = 0
        self.charges = 0
        self.color_id = ["#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])]

        k = random.choice(model.land_holders)
        if k == 'large_holder':
            self.land = 30
            self.parcels = self.land * 4
            self.parcels_wheat = int(self.model.wheat_acres_sown * self.parcels)
            self.parcels_barley = int(self.model.barley_acres_sown * self.parcels)
            self.parcels_oat = int(self.model.oat_acres_sown * self.parcels)
            self.wheat_seed = self.parcels_wheat * self.model.wheat_seed_rate
            self.barley_seed = self.parcels_barley * self.model.barley_seedRate
            self.oat_seed = self.parcels_oat * self.model.oat_seedRate
        if k == 'med_holder':
            self.land = 15
            self.parcels = self.land * 4
            self.parcels_wheat = int(self.model.wheat_acres_sown * self.parcels)
            self.parcels_barley = int(self.model.barley_acres_sown * self.parcels)
            self.parcels_oat = int(self.model.oat_acres_sown * self.parcels)
            self.wheat_seed = self.parcels_wheat * self.model.wheat_seed_rate
            self.barley_seed = self.parcels_barley * self.model.barley_seedRate
            self.oat_seed = self.parcels_oat * self.model.oat_seedRate
        if k == 'small_holder':
            self.land = 10
            self.parcels = self.land * 4
            self.parcels_wheat = int(self.model.wheat_acres_sown * self.parcels)
            self.parcels_barley = int(self.model.barley_acres_sown * self.parcels)
            self.parcels_oat = int(self.model.oat_acres_sown * self.parcels)
            self.wheat_seed = self.parcels_wheat * self.model.wheat_seed_rate
            self.barley_seed = self.parcels_barley * self.model.barley_seedRate
            self.oat_seed = self.parcels_oat * self.model.oat_seedRate

    def harvest(self):
        self.meanw = wheatyields_mean[self.model.year]
        self.sdw = (wheatyields_sd[self.model.year])
        self.meanb = barleyyields_mean[self.model.year]
        self.sdb = (barleyyields_sd[self.model.year])
        self.meano = oatyields_mean[self.model.year]
        self.sdo = (oatyields_sd[self.model.year])

    # yield per seed, convert from quarters to wheat_harvest
        self.yldw = max((self.sdw * np.random.randn(1) + self.meanw),0)
        self.yldb = max((self.sdb * np.random.randn(1) + self.meanb),0)
        self.yldo = max((self.sdo * np.random.randn(1) + self.meano),0)
        
    # yield per acre, net of tithe
        self.wheat_harvest = (((self.wheat_seed / self.parcels_wheat) * self.yldw) * self.parcels_wheat) * self.model.tithe
        self.barley_harvest = (((self.barley_seed / self.parcels_barley) * self.yldb) * self.parcels_barley) * self.model.tithe
        self.oat_harvest = (((self.oat_seed / self.parcels_oat) * self.yldo) * self.parcels_oat) * self.model.tithe
        
        self.harvestAll = self.wheat_harvest + self.barley_harvest + self.oat_harvest
        

    def retainSeed(self):
        if self.wheat_harvest > (self.model.wheat_seed_rate * self.parcels_wheat):
            self.wheat_seed = self.model.wheat_seed_rate * self.parcels_wheat
        else:
            self.wheat_seed = self.wheat_harvest
        self.wheat_harvest = self.wheat_harvest - self.wheat_seed
        self.wheat_harvest = max(self.wheat_harvest , 0)
        
        if self.barley_harvest > (self.model.barley_seedRate * self.parcels_barley):
            self.barley_seed = self.model.barley_seedRate * self.parcels_barley
        else:
            self.barley_seed = self.barley_harvest
        self.barley_harvest = self.barley_harvest - self.barley_seed
        self.barley_harvest = max(self.barley_harvest, 0)

        if self.oat_harvest > (self.model.oat_seedRate * self.parcels_oat):
            self.oat_seed = self.model.oat_seedRate * self.parcels_oat
        else:
            self.oat_seed = self.oat_harvest
        self.oat_harvest = self.oat_harvest - self.oat_seed
        self.oat_harvest = max(self.oat_harvest, 0)

        print(self.wheat_seed, self.barley_seed, self.oat_seed, self.harvestAll)

    def eat(self):
        self.harvestAll = self.harvestAll - self.model.subsistence
        if self.harvestAll > 0:
            self.fed = 1
        else:
            self.fed = 0
        self.harvestAll = max (self.harvestAll,0)

    def returnColor(self):
        return (self.color_id)

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        new_position = random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def give_money(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        if len(cellmates) > 1:
            other = random.choice(cellmates)
            other.land += 1
            self.land -= 1

    def step(self):
        self.harvest()
        self.retainSeed()
        self.eat()

# collectors / returners

def compute_gini(model):
    agent_lands = [agent.land for agent in model.schedule.agents]
    x = sorted(agent_lands)
    N = model.num_agents
    B = sum(xi * (N - i) for i, xi in enumerate(x)) / (N * sum(x))
    return (1 + (1 / N) - 2 * B)

def count_fed(model):
    number_fed = sum([agent.fed for agent in model.schedule.agents])
    return number_fed