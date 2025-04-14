import os
import paho.mqtt.client as mqtt
import threading

# --- 定義 callback ---
def on_log(client, userdata, level, buf):
    print("MQTT LOG:", buf)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT 連線成功！")
        client.subscribe("esp32/control")
    else:
        print(f"MQTT 連線失敗，錯誤碼：{rc}")

def on_message(client, userdata, msg):
    print(f"收到來自 {msg.topic} 的訊息: {msg.payload.decode()}")

# --- 動態取得憑證路徑 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CA_CERT_PATH = os.path.join(BASE_DIR, "mqtt-certs", "certs", "ca.crt")
print("使用的 ca.crt 路徑：", CA_CERT_PATH)

# --- 建立 MQTT client 並設定 TLS ---
mqtt_client = mqtt.Client()
mqtt_client.on_log = on_log
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# 如果是自簽憑證，測試時可考慮略過驗證主機名：
mqtt_client.tls_set(ca_certs=CA_CERT_PATH)
mqtt_client.tls_insecure_set(True)

def start_mqtt():
    try:
        mqtt_client.connect("192.168.11.6", 8883, 60)
        thread = threading.Thread(target=mqtt_client.loop_forever, daemon=True)
        thread.start()
        print("MQTT 客戶端正在運行...")
    except Exception as e:
        print(f"無法連接到 MQTT 伺服器: {e}")

# 發送訊息給 ESP32
def publish_message(message):
    try:
        mqtt_client.publish(esp32/control, message)
        print(f" 已發送 MQTT 訊息: {message}")
    except Exception as e:
        print(f" 發送 MQTT 訊息失敗: {e}")

if __name__ == "__main__":
    start_mqtt()

