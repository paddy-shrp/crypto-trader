import numpy as np
from trading_simulator.data_center import DataCenter
import datetime as dt
import matplotlib.pyplot as plt

data_center = DataCenter(["ETH/USD"], file_name="eth_usd_2022")

data = data_center.get_history_by_frequency(dt.datetime.now(), dt.timedelta(weeks=100), "15min", "ETH/USD").values[:, 0]

def calculate_theta_for_pol(x, y, pol_length):
    A = np.column_stack([x**i for i in range(pol_length)])
    theta = np.linalg.solve(A.T @ A, A.T @ y)
    return theta

old_size = len(data)
y = data[:int(old_size*0.7)]
length = len(y)
y_norm = (y - y.min()) / (y.max() - y.min())
x_norm = np.arange(length) / length

thetas = 100 * [0]

for i in range(len(thetas)):
    thetas[i] = calculate_theta_for_pol(x_norm, y_norm, i+1)

# Validation Set
y_val = data[int(old_size*0.7):]
val_length = len(y_val)
y_val_norm = ((y_val - y_val.min()) / (y_val.max() - y_val.min()))
x_val = np.arange(val_length) / val_length

yls = 100 * [0]
err = 100 * [0]
for i in range(len(yls)):
    yls_temp = 0
    for j in range(i):
        yls_temp += (thetas[i][j] * x_val**j)
    yls[i] = yls_temp
    err[i] = np.linalg.norm(yls[i] - y_val_norm) / np.linalg.norm(y_val_norm)
 
lowest = np.argmin(err)

plt.title(str(err[lowest]))
plt.plot(np.arange(1, 101), err)
plt.show()