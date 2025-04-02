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

# 溫度計時器與狀態變數
over_threshold_time = None
under_threshold_time = None
fan_on = False  # 記錄風扇狀態

REMOTE_NAME = "fan_remote"  # LIRC 設定檔中的遙控器名稱


def send_ir_signal(command):
    """
    發送紅外線指令給電風扇
    :param command: LIRC 設定檔中的按鍵名稱 (例如 'KEY_POWER')
    """
    try:
        result = subprocess.run(["irsend", "SEND_ONCE", REMOTE_NAME, command],
                                capture_output=True, text=True, check=True)
        print("發送成功:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("發送失敗:", e.stderr)


def update(frame):
    global cbar, over_threshold_time, under_threshold_time, fan_on
    
    pixels = np.array(sensor.pixels)  # 讀取感測器數據
    avg_temp = np.mean(pixels)  # 計算平均溫度
    
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
    print(f"平均溫度: {avg_temp:.2f}°C")
    print("-" * 40)
    
    # 判斷溫度條件
    current_time = time.time()
    if avg_temp > 30:
        if over_threshold_time is None:
            over_threshold_time = current_time
        elif current_time - over_threshold_time >= 5 and not fan_on:
            print("溫度超過30度5秒，開啟風扇")
            send_ir_signal("KEY_POWER")
            fan_on = True
            under_threshold_time = None  # 重置低溫計時
    else:
        over_threshold_time = None  # 重置高溫計時
    
    if avg_temp < 25:
        if under_threshold_time is None:
            under_threshold_time = current_time
        elif current_time - under_threshold_time >= 60 and fan_on:
            print("溫度低於25度1分鐘，關閉風扇")
            send_ir_signal("KEY_POWER")
            fan_on = False
            over_threshold_time = None  # 重置高溫計時
    else:
        under_threshold_time = None  # 重置低溫計時

# 啟動動畫與顯示
ani = animation.FuncAnimation(fig, update, interval=500)
plt.show()
