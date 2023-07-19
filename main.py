from datetime import datetime, timezone
from fastapi import FastAPI, status, Response
from goodwords_service import add_historical_goodwords, process_event
from pydantic import BaseModel
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import logging
import os
from dotenv import load_dotenv
import mongo_client
from typing import Optional, List, Union


load_dotenv()

app = FastAPI()

logger = logging.getLogger(__name__)

class HistoricalChannel(BaseModel):
    channel_id: str

@app.get("/")
async def root():
    return ''


@app.post("/history", status_code=201)
async def root(req: HistoricalChannel, response: Response):
    if req.channel_id == "C0441R6SKBN":
        add_historical_goodwords()
    else:
        response.status_code = 404
    

@app.post("/slack/events")
async def root(req: dict[str, object], resp: Response):
    if req.get('challenge', False):
        return req['challenge']
    elif req.get('event', False):
        process_event(req.get('event'))
    else:
        resp.status_code = 400
        print(f"Event missing attribute: {req}")



