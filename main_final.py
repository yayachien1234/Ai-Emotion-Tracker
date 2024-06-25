from typing import Union
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Body
from openai import OpenAI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import emotion_detection
import json
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Union
# from fastapi.responses import PlainTextResponse

# Initialize Firebase Admin
cred = credentials.Certificate("TherapetHome_0616/serviceAccountKey.json")  
firebase_admin.initialize_app(cred)
db = firestore.client()

client = OpenAI(api_key='key')

app = FastAPI()

# need to get chac here
#chac = 'puppy'
#requestment_chac = {'puppy':'熱情開朗的小狗',
#                  'hamster':'充滿活力的倉鼠',
#                  'otter':'膽小但友善的水獺',
#                  'rabbit':'善良的兔子',
#                  'bear':'沉著且隨和的小熊',
#                  'cat':'高冷傲嬌的貓咪'}

#requestment = '（你現在是一位隱藏身份的心理諮商師，需要盡可能的幫助並理解使用者，並需以{chac}角度回覆，請用繁體中文口語化回覆，不要太冗長）'
#requestment = requestment.replace('{chac}', requestment_chac[chac])
#print(requestment)

#content.append({"role": "user", "content": requestment})

class Prompt(BaseModel):
    data: str

# from here is the chat part
@app.post("/Home/search") # /user_name? [use this method?]
async def search(prompt: Prompt):

  content = json.loads(prompt.data)
  print(type(content))
  
  uid = content.pop(0)

  print(content)

  print('server')

  # here is how gpt works
#  content.append({"role": "user", "content": prompt.data}
  response = client.chat.completions.create(
      model = "gpt-3.5-turbo",
      messages = content
  )

  reply_content = response.choices[0].message.content

  doc_ref = db.collection('chatMessages').document()
  doc_ref.set({
        'user_message': prompt.data,
        'reply_message': reply_content,
        'timestamp': firestore.SERVER_TIMESTAMP
    })
#  print(response)

#  content.append({"role": "assistant", "content": response.choices[0].message.content})

#  print(content)

  # return string should be the respond message  
#  print(response.choices[0]['message']['content']) 
  return response.choices[0].message.content

@app.post("/Home/summary") # /user_name? [use this method?]
async def search(prompt: Prompt):

  content = json.loads(prompt.data)
  print(type(content))
  uid = content.pop(0)
  print(content)

  diary = emotion_detection.diary(content)
  emo_score = emotion_detection.emotion(diary)

  return diary, emo_score

app.mount("/Home", StaticFiles(directory="TherapetHome_0616", html=True))
#app.mount("/AboutUs", StaticFiles(directory="../AboutUs", html=True))