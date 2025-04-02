import numpy as np
import busio
import board
import adafruit_amg88xx
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# 初始化 I2C 介面
i2c_bus = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_amg88xx.AMG88XX(i2c_bus)

# 設定圖像顯示
fig, ax = plt.subplots()
cbar = None
def update(frame):
    global cbar
    pixels = np.array(sensor.pixels)  # 讀取感測器數據
    ax.clear()
    cax = ax.imshow(pixels, cmap='inferno', interpolation='bilinear', vmin=20, vmax=40)
    
    # 加入 color bar
    if cbar is None:
        cbar = fig.colorbar(cax)
    
    # 印出數據到終端機
    print("Sensor Data:")
    for row in pixels:
        print([round(temp, 2) for temp in row])
    print("-" * 40)

# 設定動畫
ani = animation.FuncAnimation(fig, update, interval=500)
plt.show()
import numpy as np
import busio
import board
import adafruit_amg88xx
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# 初始化 I2C 介面
i2c_bus = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_amg88xx.AMG88XX(i2c_bus)

# 設定圖像顯示
fig, ax = plt.subplots()
cbar = None
def update(frame):
    global cbar
    pixels = np.array(sensor.pixels)  # 讀取感測器數據
    ax.clear()
    cax = ax.imshow(pixels, cmap='inferno', interpolation='bilinear', vmin=20, vmax=40)
    
    # 加入 color bar
    if cbar is None:
        cbar = fig.colorbar(cax)
    
    # 印出數據到終端機
    print("Sensor Data:")
    for row in pixels:
        print([round(temp, 2) for temp in row])
    print("-" * 40)

# 設定動畫
ani = animation.FuncAnimation(fig, update, interval=500)
plt.show()
