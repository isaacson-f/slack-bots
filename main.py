from fastapi import FastAPI
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

#MongoClient.get_database()

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
    channel_name="goodwords"

    channel_name = "needle"
    conversation_id = None
    try:
       # Call the conversations.list method using the WebClient
        result = client.conversations_history(channel="C0441R6SKBN")
        conversation_history = result["messages"]
        for message in conversation_history:
            word = message['text']
            temp_list = list(filter(lambda a: len(a) > 0, word.split(" ")))
            if len(temp_list) > 1:
               print(f"invalid submission: {temp_list}")
            else:
               print(temp_list[0].lower())
    except SlackApiError as e:
        print(f"Error: {e}")


@app.post("/slack/events")
async def root(resp: SlackChallenge):
    return resp.challenge




