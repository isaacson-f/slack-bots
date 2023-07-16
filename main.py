from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}



@app.post("/challenge")
async def root(challenge: str):
    return challenge




