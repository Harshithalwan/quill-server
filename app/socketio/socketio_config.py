from . import socketio
from flask import request
from flask_socketio import emit
import pathlib
from dotenv import load_dotenv
import textwrap
import google.generativeai as genai
import os
from IPython.display import display
from IPython.display import Markdown


load_dotenv()
gemini_api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel('gemini-pro')
chatSessions = {}
# Define Socket.IO event handlers
def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))
@socketio.on('connect')
def handle_connect():
    chatSessions[request.sid] = model.start_chat(history=[])
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    del chatSessions[request.sid]
    print('Client disconnected')

@socketio.on('message')
def handle_chat_message(message):
    print('Received message:', message)
    session_id = request.sid
    chat = chatSessions[session_id]
    response = chat.send_message(message, stream=True)
    # response = model.generate_content(message, stream=True)
    for chunk in response:
        # print(chunk.text)
        emit('message', chunk.text, to=session_id)   