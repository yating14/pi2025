import pandas as pd
import joblib
import datetime
import numpy as np
import adafruit_amg88xx
import busio
import board
from sklearn.ensemble import RandomForestClassifier
import time

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
    data = pd.DataFrame(columns=['timestamp', 'temperature', 'time_of_day', 'day_of_week', 'fan_status', 'usage_duration'])

def get_time_of_day(hour):
    """ 根據小時數判斷時間區間 """
    if 6 <= hour < 12:
        return "morning"
    elif 12 <= hour < 18:
        return "afternoon"
    elif 18 <= hour < 24:
        return "evening"
    else:
        return "night"

def get_current_data(fan_status, duration):
    now = datetime.datetime.now()
    current_temp = get_current_temperature()
    time_of_day = get_time_of_day(now.hour)
    return [now, current_temp, time_of_day, now.strftime('%A'), fan_status, duration]

def log_user_action(fan_status):
    global data
    duration = 0
    
    if len(data) > 0 and data.iloc[-1]['fan_status'] == "ON":
        last_time = datetime.datetime.strptime(data.iloc[-1]['timestamp'], "%Y-%m-%d %H:%M:%S")
        duration = (datetime.datetime.now() - last_time).seconds
    
    new_entry = get_current_data("ON" if fan_status == 1 else "OFF", duration)
    data.loc[len(data)] = new_entry
    data.to_csv("fan_usage_data.csv", index=False)

def calculate_fan_usage():
    total_duration = data[data['fan_status'] == "ON"]['usage_duration'].sum()
    print(f"總共開啟風扇時間：{total_duration} 秒")

def train_ai():
    global data
    if len(data) < 10:
        return
    
    X = data[['temperature', 'time_of_day', 'day_of_week']]
    y = data['fan_status'].apply(lambda x: 1 if x == "ON" else 0)
    
    model = RandomForestClassifier()
    model.fit(X, y)
    
    joblib.dump(model, "fan_ai_model.pkl")
    print("AI 已更新學習!")

def predict_fan_action():
    try:
        model = joblib.load("fan_ai_model.pkl")
    except FileNotFoundError:
        print("模型尚未訓練，請先收集資料")
        return
    
    current_temp, time_of_day, day_of_week = get_current_data(None, 0)[1:4]
    prediction = model.predict([[current_temp, time_of_day, day_of_week]])
    
    if prediction[0] == 1:
        print("AI 建議開風扇")
    else:
        print("AI 建議關閉風扇")

log_user_action(1)  # 記錄使用者開啟風扇
time.sleep(5)       # 模擬風扇運行 5 秒
log_user_action(0)  # 記錄使用者關閉風扇

train_ai()
calculate_fan_usage()
predict_fan_action()
