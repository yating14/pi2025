import pandas as pd
import joblib
import datetime
import numpy as np
from sklearn.ensemble import RandomForestClassifier
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
    data = pd.DataFrame(columns=['timestamp', 'temperature', 'hour', 'weekday', 'fan_status', 'usage_duration'])

# 計算風扇開啟時間
def calculate_fan_usage():
    global data
    if len(data) < 2:
        return

    last_on_time = None
    total_duration = 0

    for i in range(len(data)):
        if data.loc[i, 'fan_status'] == 1:
            if last_on_time is None:
                last_on_time = datetime.datetime.strptime(data.loc[i, 'timestamp'], "%Y-%m-%d %H:%M:%S")
        elif last_on_time is not None:
            end_time = datetime.datetime.strptime(data.loc[i, 'timestamp'], "%Y-%m-%d %H:%M:%S")
            duration = (end_time - last_on_time).total_seconds()
            data.at[i, 'usage_duration'] = duration
            total_duration += duration
            last_on_time = None
        else:
            data.at[i, 'usage_duration'] = 0  # 風扇沒開時，持續時間為 0

    data.to_csv("fan_usage_data.csv", index=False)
    print(f"總共開啟風扇時間：{total_duration} 秒")

# 取得當前環境數據
def get_current_data(fan_status):
    now = datetime.datetime.now()
    current_temp = get_current_temperature()
    usage_duration = 0

    # 確保 `data` 內有資料可以參考
    if len(data) > 0:
        usage_duration = data.iloc[-1]['usage_duration'] if 'usage_duration' in data.columns else 0

    return [now.strftime("%Y-%m-%d %H:%M:%S"), current_temp, now.hour, now.weekday(), fan_status, usage_duration]

# 當使用者開關風扇時，自動記錄
def log_user_action(fan_status):
    global data
    new_entry = get_current_data(fan_status)
    data.loc[len(data)] = new_entry
    data.to_csv("fan_usage_data.csv", index=False)

# 讓 AI 學習這些行為
def train_ai():
    global data
    if len(data) < 10:  # 先收集至少10筆資料才開始訓練
        return
    
    X = data[['temperature', 'hour', 'weekday', 'usage_duration']]
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

    current_data = get_current_data(None)
    current_temp, current_hour, current_weekday, _, current_usage = current_data[:5]
    
    prediction = model.predict([[current_temp, current_hour, current_weekday, current_usage]])

    if prediction[0] == 1:
        print("AI 建議開風扇")
    else:
        print("AI 建議關閉風扇")

# 假設使用者開關風扇：
log_user_action(1)  # 記錄使用者開啟風扇
log_user_action(0)  # 記錄使用者關閉風扇

# 計算總開啟時間
calculate_fan_usage()

# 訓練 AI
train_ai()

# AI 自動決定
predict_fan_action()
