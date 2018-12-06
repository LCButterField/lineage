# run.py
from server import server
import matplotlib.pyplot as plt


server.port = 8521 # The default
server.launch()

num_fed = model.datacollector.get_model_vars_dataframe()
num_fed.plot()

plt.show()