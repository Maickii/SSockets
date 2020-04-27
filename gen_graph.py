import pandas as pd
from pandas import Series, DataFrame
import matplotlib.pyplot as plt

fd = open("results.txt", "r")
results = fd.readlines()
data = [results[0][0], results[0][2], results[0][4], results[0][6], results[0][8]]
plt.bar(['norm_config', 'save_keys', 'load_key', 'load_key w bad path', 'save_key w no path'], data)
plt.ylabel("# of times tested")
plt.xlabel("messages")
plt.title("SSockets Results")
plt.show()
