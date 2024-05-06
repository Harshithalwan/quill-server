import requests
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
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec

load_dotenv()
gemini_api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel('gemini-1.5-pro-latest', 
                              system_instruction=["Respond from the give context of the chat, ask follow up questions if needed.", 
                                                  "If context seems unrelated to question, respond with 'No relevant context found'",
                                                  "Give concise response", 
                                                  "respond with plane text like you're chatting with a person, don't use markdown, you can use bullet points if needed"])

pinecone_api_key = os.getenv('PINECONE_API_KEY')
pc = Pinecone(api_key=pinecone_api_key)

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
    try:
        contextResponse = getSementicMatches(message['userMessage'], message['ids'])
        response = chat.send_message("Context: {context}, Question: {question}".format(context=' '.join(contextResponse), question=message['userMessage']), stream=True)
        # response = model.generate_content(message, stream=True)
        for chunk in response:
            emit('message', chunk.text, to=session_id)
    except Exception as e:
        print(e)
        emit('message', "Error occured!, please be patient and try again. If it still doesn't work reach out to @ Harshithalwan@gmail.com", to=session_id)   


HUGGING_FACE_API_KEY = os.getenv('HUGGING_FACE_API_KEY')
API_URL = "https://api-inference.huggingface.co/models/maidalun1020/bce-embedding-base_v1"
headers = {"Authorization": f"Bearer {HUGGING_FACE_API_KEY}"}
def getVector(payload):
    vectorResponse = requests.post(API_URL, headers=headers, json=payload)
    return vectorResponse.json()


def getSementicMatches(text, ids):
    # model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
    # questionVector = model.encode(text).tolist()
    try:
        questionVector = getVector({
                "inputs": text,
                })
        index = pc.Index("documents")
        contextResponse = index.query(
            vector=questionVector,
            filter={"documentId": {"$in": ids}},
            namespace="ns1", top_k=5,
            include_metadata=True)
        response = []
        for match in contextResponse['matches']:
            response.append(match['metadata']['text'])
        return response

    except Exception as e:
        print(e)
        raise Exception("Error: can't create embeddings")