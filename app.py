import time
import glob
import threading
import psutil
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'


async_mode = None
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = threading.Lock()



# 后台线程 产生数据，即刻推送至前端
def background_thread():
    count = 0
    while True:
        socketio.sleep(2)
        count += 1
        # 获取时间
        t = time.strftime('%H:%M:%S', time.localtime())
        # 获取cpu使用
        cpus = psutil.cpu_percent(interval=None, percpu=True)

        sent_data = {
            'time': t,
            'cpu': list(cpus)[:2],
            'count': count,
            'tempure': [random.randint(10, 220), random.randint(10, 220), random.randint(10, 220), random.randint(10, 220)]
        }
        socketio.emit('server_response', sent_data, namespace='/sentdata')


@socketio.on('connect', namespace='/sentdata')
def socket_connect():
    """与前端建立 socket 连接后，启动后台线程"""
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)



@app.route("/home")
def home():
    """主页"""
    return render_template('home.html')



if __name__ == '__main__':
    app.run(debug=True)
