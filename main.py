from datetime import datetime, timezone
from fastapi import FastAPI, status, Response, Request
from goodwords_service import add_historical_goodwords, process_event
from leetcode_service import post_daily_leetcode
from b_positive_scraper import update_donations, find_current_donations
from pydantic import BaseModel
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import logging
import os
from dotenv import load_dotenv
import mongo_client
from typing import Optional, List, Union, Dict
import json

from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

load_dotenv()

app = FastAPI()

logger = logging.getLogger(__name__)

class HistoricalChannel(BaseModel):
    channel_id: str

@app.get('/')
async def root():
    return ""


@app.post('/history', status_code=201)
async def root(req: HistoricalChannel, response: Response):
    if req.channel_id == 'C0441R6SKBN':
        add_historical_goodwords()
    else:
        response.status_code = 404

@app.get('/leetcode/blind-75')
async def root():
    post_daily_leetcode()
    

@app.post('/slack/events')
async def root(req: Dict[str, object], resp: Response):
    if req.get('challenge', False):
        return req['challenge']
    elif req.get('event', False):
        print(f"Event Received: {req.get('event')}")
        process_event(req.get('event'))
    else:
        resp.status_code = 400
        print(f'Event missing attribute: {req}')


@app.get('/b-positive/weekly-update')
async def root():
    find_current_donations()


@app.get('/b-positive/update-donations')
async def root():
    update_donations(single_update=False)

@app.get('/b-positive/refresh-consistent')
async def root():
    update_donations(single_update=True)


@app.post('/discord/interactions')
async def root(req: Request, req_body: Dict[str, object] ,resp: Response):
    # Your public key can be found on your application in the Developer Portal
    PUBLIC_KEY = os.environ['DISCORD_PUBLIC_KEY']
    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))

    signature = req.headers['X-Signature-Ed25519']
    print(f'params: {req.query_params}')
    timestamp = req.headers['X-Signature-Timestamp']
    body = await req.body()
    new_body = body.decode("utf-8")
    
    print('Verifying')
    print(f'{timestamp}{req_body}')
    try:
        verify_key.verify(f'{timestamp}{new_body}'.encode(), bytes.fromhex(signature))
        if req_body['type'] == 1:
           print('Health check discord')
           resp.status_code = 200
           resp.body = str({'type':1}).encode()
           return resp
    except BadSignatureError:
        resp.status_code = 401
        return resp
        



