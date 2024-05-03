from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
@cross_origin()
def index():
    print("hello")
    return "Hi there"

@socketio.on('message')
@cross_origin()
def handle_message(message):
    print("secondhello")
    socketio.emit('message', "Hi there")

if __name__ == '__main__':
    socketio.run(app)