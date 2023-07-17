from datetime import datetime, timezone
from fastapi import FastAPI, Request
from pydantic import BaseModel
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import logging
import os
from dotenv import load_dotenv
import MongoClient
from typing import Optional, List, Union


load_dotenv()

app = FastAPI()

client = WebClient(token=os.environ.get("SLACK_TOKEN"))

good_words_collection = MongoClient.get_good_words_collection()

logger = logging.getLogger(__name__)

class Reactions(BaseModel):
    name: str
    count: int
    users: List[str]

class SlackChallenge(BaseModel):
    token: Optional[str]
    challenge: Optional[str]
    type: str
    text: Optional[str]
    channel: Optional[str]
    user: Optional[str]
    ts: Optional[float]
    deleted_ts: Optional[float]
    event_ts: Optional[float]
    subtype: Optional[str]
    hidden: Optional[bool]
    is_starred: Optional[bool]
    pinned_to: Optional[List[str]]
    reactions: Optional[List[Reactions]]

@app.get("/")
async def root():
    return ''


@app.get("/history")
async def root():
    try:
       # Call the conversations.list method using the WebClient
        result = client.conversations_history(channel="C0441R6SKBN")
        conversation_history = result["messages"]
        for message in conversation_history:
            word = message['text']
            date_millis = float(message['ts'])
            user_id = message['user']
            temp_list = list(filter(lambda a: len(a) > 0, word.split(" ")))
            if len(temp_list) > 1:
               print(f"invalid submission: {temp_list}")
            else:
               if find_word(temp_list[0].lower()) is None:
                   insert_new_word(temp_list[0].lower(), date_millis, user_id)
    except SlackApiError as e:
        print(f"Error: {e}")


@app.post("/slack/events")
async def root(resp: dict[str, object]):
    if resp.get('challenge', False):
        return resp['challenge']
    elif resp.get('event', False):
        event = resp['event']
        if event.get('text', False) and event.get('ts', False) and event.get('user', False):
            message = event['text']
            millis_time = float(event['ts'])
            user = event['user']
            temp_list = list(filter(lambda a: len(a) > 0, message.split(" ")))
            if len(temp_list) > 1:
               print(f"invalid submission: {temp_list}")
            else: 
                prev_sent = find_word(temp_list[0])
                if prev_sent is not None:
                    print(f"Thread Time: {datetime.fromtimestamp(prev_sent['date_millis']).strftime('%m/%d/%Y')}, Prev Sent Word: {temp_list[0]}")
                    client.chat_postMessage(channel="C0441R6SKBN", text=f"{temp_list[0]} was previously sent on {datetime.fromtimestamp(prev_sent['date_millis']).strftime('%m/%d/%Y')}", thread_ts=millis_time)
                else:
                    insert_new_word(temp_list[0], millis_time, user)
                    client.chat_postMessage(channel="C0441R6SKBN", text="Great Word :biting_lip:", thread_ts=millis_time)
        else:
            print(f"Event missing attribute ts or text: {event}")
    else:
        print(f"Event missing attribute: {resp}")

def insert_new_word(word: str, date_millis: float, user: str):
    document = {
        "word": word,
        "date_millis": date_millis,
        "user_id": user
    }
    try:
        good_words_collection.insert_one(document)
        print(f"Successfully added word: \n {document['word']} \n millis: {document['date_millis']}")
    except Exception as e:
        print(f"Error adding word: {e}")

def find_word(word: str):
    return good_words_collection.find_one({"word": word})