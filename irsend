import subprocess

def send_ir_signal(command):
    """
    發送紅外線指令給電風扇
    :param command: LIRC 設定檔中的按鍵名稱 (例如 'KEY_POWER')
    """
    remote_name = "fan_remote"  # 你的遙控器名稱，確保與 lircd.conf 中的名稱匹配
    try:
        result = subprocess.run(["irsend", "SEND_ONCE", remote_name, command], 
                                capture_output=True, text=True, check=True)
        print("發送成功:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("發送失敗:", e.stderr)

# 測試發送開關電源訊號
send_ir_signal("KEY_POWER")
