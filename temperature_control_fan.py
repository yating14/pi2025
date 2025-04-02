import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import busio
import board
import adafruit_amg88xx
import subprocess
import time
from scipy.interpolate import griddata

# 初始化 I2C 和感測器
i2c_bus = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_amg88xx.AMG88XX(i2c_bus)

# 設定熱像圖參數
grid_x, grid_y = np.mgrid[0:7:32j, 0:7:32j]
fig, ax = plt.subplots()
cbar = None

temp_threshold = 30  # 設定溫度閾值
trigger_duration = 5  # 連續超過閾值的秒數
start_time = None  # 記錄開始超過閾值的時間

def send_ir_signal(command):
    """
    發送紅外線指令給電風扇
    :param command: LIRC 設定檔中的按鍵名稱 (例如 'KEY_POWER')
    """
    remote_name = "fan_remote"  # 你的遙控器名稱
    try:
        result = subprocess.run(["irsend", "SEND_ONCE", remote_name, command], 
                                capture_output=True, text=True, check=True)
        print("發送成功:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("發送失敗:", e.stderr)

def update(frame):
    global cbar, start_time
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
    
    # 檢查是否有超過溫度閾值的點
    if np.max(pixels) > temp_threshold:
        if start_time is None:
            start_time = time.time()  # 開始計時
        elif time.time() - start_time >= trigger_duration:
            print("溫度超過閾值，發送開啟風扇指令")
            send_ir_signal("KEY_POWER")
            start_time = None  # 重置計時器
    else:
        start_time = None  # 若低於閾值則重置計時器

ani = animation.FuncAnimation(fig, update, interval=500)
plt.show()
