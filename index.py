from flask import Flask
import threading
import dingtalk_stream
from dingtalk_stream import AckMessage
import requests

app = Flask(__name__)

# 钉钉应用的App Key和App Secret
APP_KEY = "xxxx"
APP_SECRET = "xxxx"


# 定义事件处理器
class MyEventHandler(dingtalk_stream.EventHandler):
    async def process(self, event: dingtalk_stream.EventMessage):
        print(
            event.headers.event_type,
            event.headers.event_id,
            event.headers.event_born_time,
            event.data,
        )
        # 处理接收到的事件，并发送到WordPress
        send_data_to_wordpress_thread = threading.Thread(
            target=send_data_to_wordpress, args=(event.data,)
        )
        send_data_to_wordpress_thread.start()
        return AckMessage.STATUS_OK, "OK"


class MyCallbackHandler(dingtalk_stream.CallbackHandler):
    async def process(self, message: dingtalk_stream.CallbackMessage):
        print(message.headers.topic, message.data)
        # 处理接收到的回调消息，并发送到WordPress
        send_data_to_wordpress_thread = threading.Thread(
            target=send_data_to_wordpress, args=(message.data,)
        )
        send_data_to_wordpress_thread.start()
        return AckMessage.STATUS_OK, "OK"


# 启动钉钉Stream客户端
def start_dingtalk_client():
    credential = dingtalk_stream.Credential(APP_KEY, APP_SECRET)
    client = dingtalk_stream.DingTalkStreamClient(credential)
    client.register_all_event_handler(MyEventHandler())
    client.register_callback_handler(
        dingtalk_stream.ChatbotMessage.TOPIC, MyCallbackHandler()
    )
    client.start_forever()


# 发送数据到wordpress
def send_data_to_wordpress(data, allowed_origin=None):
    url = "http://00.00.00.00/wp-json/your-endpoint/data"
    headers = {"Content-Type": "application/json"}

    # 添加允许跨域的请求头
    if allowed_origin:
        headers["Access-Control-Allow-Origin"] = allowed_origin

    requests.post(url, json=data, headers=headers)


# 启动钉钉Stream客户端线程
thread = threading.Thread(target=start_dingtalk_client, daemon=True)
thread.start()


# Flask路由，用于健康检查或其他用途
@app.route("/")
def index():
    return "DingTalk Stream client is running."


if __name__ == "__main__":
    app.run(port=5000)
