import paho.mqtt.client as mqtt
import threading
import ssl
import os

# MQTT 設定
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = 8883
MQTT_TOPIC = "esp32/control"
MQTT_KEEPALIVE = 60

if MQTT_BROKER is None:
    raise ValueError("The MQTT_BROKER environment variable is not set!")
else:
    print(f"Connecting to MQTT broker at: {MQTT_BROKER}")
# 初始化 MQTT 客戶端
mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    """當連接成功時呼叫的回調函式"""
    if rc == 0:
        print("MQTT 連線成功！")
        client.subscribe(MQTT_TOPIC)  # 訂閱主題
    else:
        print(f"MQTT 連線失敗，錯誤碼：{rc}")

def on_message(client, userdata, msg):
    """當接收到消息時呼叫的回調函式"""
    print(f"收到來自 {msg.topic} 的訊息: {msg.payload.decode()}")

def on_log(client, userdata, level, buf):
    """用於打印 log 的回調函式"""
    print("MQTT LOG:", buf)

mqtt_client = mqtt.Client(protocol=mqtt.MQTTv311)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_log = on_log

# 自定義 SSL 上下文，禁用證書驗證
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

mqtt_client.tls_set_context(context)
# 啟動 MQTT
def start_mqtt():
    """啟動 MQTT 連線並運行客戶端"""
    try:
        print("正在嘗試連接到 MQTT 伺服器...")
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
        thread = threading.Thread(target=mqtt_client.loop_forever, daemon=True)
        thread.start()
        print("MQTT 客戶端正在運行...")
    except Exception as e:
        print(f"無法連接到 MQTT 伺服器: {e}")

# 讓 Flask 能夠發送 MQTT 訊息到 ESP32
def publish_message(message):
    """發送消息到指定的 MQTT 主題"""
    try:
        mqtt_client.publish(MQTT_TOPIC, message)
        print(f"已發送 MQTT 訊息: {message}")
    except Exception as e:
        print(f"發送 MQTT 訊息失敗: {e}")

# 讓其他程式可以匯入 `mqtt_client` 使用
if __name__ == "__main__":
    start_mqtt()
