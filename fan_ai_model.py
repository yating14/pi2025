import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import numpy as np

# 讀取 CSV 檔案
data = pd.read_csv("fan_usage_data.csv")

# 準備數據
X = data[['temperature']]  # 特徵：溫度
y = data['fan_status']  # 標籤：風扇狀態 (0: 關閉, 1: 開啟)

# 切分訓練集與測試集 (80% 訓練, 20% 測試)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 訓練模型（使用邏輯回歸）
model = LogisticRegression()
model.fit(X_train, y_train)

# 測試準確度
accuracy = model.score(X_test, y_test)
print(f"模型準確度: {accuracy * 100:.2f}%")

# 測試不同溫度的預測結果
test_temps = [[25], [26], [27], [28], [29], [30]]
predictions = model.predict(test_temps)

for temp, pred in zip(test_temps, predictions):
    status = "開啟" if pred == 1 else "關閉"
    print(f"溫度 {temp[0]}°C -> 風扇應該 {status}")

# 讓 Raspberry Pi 讀取即時溫度並決定風扇開關
current_temp = float(input("請輸入當前溫度: "))
fan_status = model.predict([[current_temp]])[0]

if fan_status == 1:
    print("開啟風扇")
else:
    print("關閉風扇")
