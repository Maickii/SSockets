#import matplotlib.pyplot as plt; plt.rcdefaults()
# import numpy as np
# import matplotlib.pyplot as plt
#
# objects = ('message1')
# y_pos = np.arange(1)
# performance = [3]
#
# plt.bar(y_pos, performance, align='center', alpha=0.5)
# plt.xticks(y_pos, objects)
# plt.ylabel('# of passes')
# plt.title('Messages Successfully Transfered Via SSockets')
# plt.show()
import pandas as pd
from pandas import Series, DataFrame
import matplotlib.pyplot as plt

data = [3, 0]
plt.bar(['message1', 'null'], data)
plt.ylabel("# of times tested")
plt.xlabel("messages")
plt.title("Messages Successfully Transfered Via SSockets")
plt.show()
