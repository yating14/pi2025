import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import busio
import board
import adafruit_amg88xx
from scipy.interpolate import griddata

# 初始化 I2C 和感測器
i2c_bus = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_amg88xx.AMG88XX(i2c_bus)

# 設定熱像圖參數
grid_x, grid_y = np.mgrid[0:7:32j, 0:7:32j]
fig, ax = plt.subplots()
cbar = None

def update(frame):
    global cbar
    pixels = np.array(sensor.pixels)  # 讀取感測器數據
    points = [(i // 8, i % 8) for i in range(64)]
    values = pixels.flatten()
    grid_z = griddata(points, values, (grid_x, grid_y), method='cubic')
    
    ax.clear()
    cax = ax.imshow(grid_z, cmap='inferno', interpolation='bilinear', vmin=20, vmax=40)
    
    if cbar is None:
        cbar = fig.colorbar(cax)
    
    # 印出數據到終端機
    print("Sensor Data:")
    for row in pixels:
        print([round(temp, 2) for temp in row])
    print("-" * 40)

ani = animation.FuncAnimation(fig, update, interval=500)
plt.show()
