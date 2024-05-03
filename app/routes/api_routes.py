from flask import jsonify, request
from . import api_bp
from flask_cors import cross_origin
from uuid import uuid4
import os
import re
from tika import parser
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from dotenv import load_dotenv
load_dotenv()
pinecone_api_key = os.getenv('PINECONE_API_KEY')

pc = Pinecone(api_key=pinecone_api_key)
filesDir = "./files/"

@api_bp.route('/prepareDocuments', methods=['POST'])
@cross_origin()
def prepare_documents():
    if request.method == 'POST':
        print("hello")
        file = request.files['file']
        if file:
            id = uuid4()
            file.save(os.path.join(filesDir, file.filename))
            raw = parser.from_file(filesDir+file.filename) 
            response = remove_extra_spaces_1(raw['content'])
            embeddedMap = createEmbedding(response)
            insertVector(embeddedMap, file.filename, id)
            return jsonify({"id": id})


def remove_extra_spaces_1(text):
  """Removes extra spaces from a string using split and join.

  Args:
      text: The string to remove extra spaces from.

  Returns:
      The string with extra spaces removed.
  """
  return ' '.join(text.split())

def createEmbedding(text):
    model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
    chunks = break_chunks(text)
    
    embeddedMap = []
    for chunk in chunks:
       encodedChunks = []
       encodedChunks.append(chunk)
       encodedChunks.append(model.encode(chunk))
       embeddedMap.append(encodedChunks)     
    return embeddedMap

def break_chunks(text, max_length=500):
  """Breaks a string into chunks at full stop or max length.

  Args:
    text: The string to break into chunks.
    max_length: The maximum length of each chunk.

  Returns:
    A list of chunks.
  """

  chunks = []
  i = 0
  while i < len(text):
    j = i + max_length
    while j < len(text) and text[j] != '.':
      j += 1
    chunk = text[i:j + 1]
    # Remove multiple whitespaces
    chunk = re.sub(r'\s+', ' ', chunk)
    chunks.append(chunk)
    i = j + 1
  return chunks


def insertVector(embeddedMap, filename, documentId):
    input = []
    print(len(embeddedMap))
    for i in range(len(embeddedMap)):
        input.append((filename + "-" + str(i), embeddedMap[i][1], {"text": embeddedMap[i][0], "documentId": str(documentId)}))
    index_name = "documents"
    try:
       index = pc.Index(index_name)
       index.upsert(
             vectors=input,
             namespace="ns1"
             )
    except ValueError as e:
          print("Error:", e)

