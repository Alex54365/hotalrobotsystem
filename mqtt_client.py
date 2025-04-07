import paho.mqtt.client as mqtt
import threading
import os

# MQTT 設定
MQTT_BROKER = os.getenv('MQTT_BROKER', '172.20.10.10')  
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_TOPIC = os.getenv('MQTT_TOPIC', 'esp32/control')
MQTT_KEEPALIVE = int(os.getenv('MQTT_KEEPALIVE', 60))

# 初始化 MQTT 客戶端
mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(" MQTT 連線成功！")
        client.subscribe(MQTT_TOPIC)  # 訂閱主題
    else:
        print(f" MQTT 連線失敗，錯誤碼：{rc}")

def on_message(client, userdata, msg):
    print(f" 收到來自 {msg.topic} 的訊息: {msg.payload.decode()}")

# 設定回呼函式
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# 啟動 MQTT
def start_mqtt():
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
        thread = threading.Thread(target=mqtt_client.loop_forever, daemon=True)
        thread.start()
        print(" MQTT 客戶端正在運行...")
    except Exception as e:
        print(f" 無法連接到 MQTT 伺服器: {e}")

# 讓 Flask 能夠發送 MQTT 訊息到 ESP32
def publish_message(message):
    try:
        mqtt_client.publish(MQTT_TOPIC, message)
        print(f" 已發送 MQTT 訊息: {message}")
    except Exception as e:
        print(f" 發送 MQTT 訊息失敗: {e}")

# 讓其他程式可以匯入 `mqtt_client` 使用
if __name__ == "__main__":
    start_mqtt()
