import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import busio
import board
import adafruit_amg88xx
import subprocess
import time
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from scipy.interpolate import griddata

# 讀取 CSV 檔案並訓練 AI 模型
data = pd.read_csv("fan_usage_data.csv")
X = data[['temperature']]
y = data['fan_status']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LogisticRegression()
model.fit(X_train, y_train)

# 初始化 I2C 和感測器
i2c_bus = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_amg88xx.AMG88XX(i2c_bus)

# 設定熱像圖參數
grid_x, grid_y = np.mgrid[0:7:32j, 0:7:32j]
fig, ax = plt.subplots()
cbar = None

# 風扇狀態與計時變數
fan_on = False
cooldown_start_time = None  # 記錄降溫開始時間

REMOTE_NAME = "fan_remote"  # LIRC 設定檔中的遙控器名稱

def send_ir_signal(command):
    """ 發送紅外線指令給電風扇 """
    try:
        result = subprocess.run(["irsend", "SEND_ONCE", REMOTE_NAME, command],
                                capture_output=True, text=True, check=True)
        print("發送成功:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("發送失敗:", e.stderr)

def update(frame):
    global cbar, fan_on, cooldown_start_time
    
    pixels = np.array(sensor.pixels)
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
    
    # 使用 AI 判斷是否開關風扇
    fan_status = model.predict([[avg_temp]])[0]

    if fan_status == 1:
        if not fan_on:
            print("AI 判斷：開啟風扇")
            send_ir_signal("KEY_POWER")
            fan_on = True
        cooldown_start_time = None  # 風扇開啟時，重置關閉計時
    else:
        if fan_on:
            if cooldown_start_time is None:
                cooldown_start_time = time.time()  # 開始計時
            elif time.time() - cooldown_start_time >= 30:  # 持續 30 秒才關閉
                print("AI 判斷：關閉風扇 (30 秒後)")
                send_ir_signal("KEY_POWER")
                fan_on = False
                cooldown_start_time = None

# 啟動動畫與顯示
ani = animation.FuncAnimation(fig, update, interval=10000)  # 每 10 秒更新一次
plt.show()
