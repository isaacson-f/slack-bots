from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class SlackChallenge(BaseModel):
    token: str
    challenge: str
    type: str

@app.get("/")
async def root():
    return {"message": "Hello World"}



@app.post("/slack/events")
async def root(resp: SlackChallenge):
    return resp.challenge




