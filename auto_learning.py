import pandas as pd
import joblib
import datetime
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import adafruit_amg88xx
import busio
import board

# 初始化 I2C 和感測器
i2c_bus = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_amg88xx.AMG88XX(i2c_bus)

def get_current_temperature():
    """ 讀取 AMG8833 感測器的溫度數據，回傳最高溫度 """
    pixels = np.array(sensor.pixels)  # 取得 8x8 的溫度矩陣
    max_temp = np.max(pixels)  # 取最高溫度
    return max_temp

# 嘗試讀取現有資料
try:
    data = pd.read_csv("fan_usage_data.csv")
except FileNotFoundError:
    data = pd.DataFrame(columns=['temperature', 'hour', 'weekday', 'fan_status', 'timestamp'])

# 取得當前環境數據
def get_current_data(fan_status):
    now = datetime.datetime.now()
    current_temp = get_current_temperature()
    return [current_temp, now.hour, now.weekday(), fan_status, now]

# 當使用者開關風扇時，自動記錄
def log_user_action(fan_status):
    global data
    new_entry = get_current_data(fan_status)
    data.loc[len(data)] = new_entry
    data.to_csv("fan_usage_data.csv", index=False)

# 計算風扇開啟時間
def calculate_fan_usage():
    global data
    total_duration = datetime.timedelta(0)

    for i in range(1, len(data)):
        if data.loc[i - 1, 'fan_status'] == 1 and data.loc[i, 'fan_status'] == 0:
            start_time = datetime.datetime.strptime(str(data.loc[i - 1, 'timestamp']), "%Y-%m-%d %H:%M:%S.%f")
            end_time = datetime.datetime.strptime(str(data.loc[i, 'timestamp']), "%Y-%m-%d %H:%M:%S.%f")
            duration = end_time - start_time
            total_duration += duration

    print(f"總共開啟風扇時間：{total_duration}")

# 讓 AI 學習這些行為
def train_ai():
    global data
    if len(data) < 10:  # 先收集至少10筆資料才開始訓練
        return
    
    X = data[['temperature', 'hour', 'weekday']]
    y = data['fan_status']

    model = RandomForestClassifier()
    model.fit(X, y)

    joblib.dump(model, "fan_ai_model.pkl")
    print("AI 已更新學習!")

# 讓 AI 自動判斷是否開風扇
def predict_fan_action():
    try:
        model = joblib.load("fan_ai_model.pkl")
    except FileNotFoundError:
        print("模型尚未訓練，請先收集資料")
        return

    current_temp, current_hour, current_weekday, _, _ = get_current_data(None)
    prediction = model.predict([[current_temp, current_hour, current_weekday]])

    if prediction[0] == 1:
        print("AI 建議開風扇")
    else:
        print("AI 建議關閉風扇")

# 假設使用者開關風扇：
log_user_action(1)  # 記錄使用者開啟風扇
log_user_action(0)  # 記錄使用者關閉風扇

# 訓練 AI
train_ai()

# 計算總開啟時間
calculate_fan_usage()

# AI 自動決定
predict_fan_action()
