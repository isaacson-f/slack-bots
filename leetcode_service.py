from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
import mongo_client
import pandas as pd
from datetime import date


client = WebClient(token=os.environ.get("SLACK_TOKEN"))

blind_75_collection = mongo_client.get_blind_75()

def post_daily_leetcode():
    question = find_next_question()
    client.chat_postMessage(channel="GKCJN0CLU", text=f"Daily Leetcode question from Blind 75: \n Type: {question['Type']} \n Difficulty: {question['Difficulty']} \n Question: <{question['URL']}|{question['Name']}>")

def find_next_question():
    question = 1
    looking = True
    while looking and question < 76:
        print(question)
        record = blind_75_collection.find_one({'Index': question})
        if record['Used_Times'] == 0:
            looking = False
            blind_75_collection.update_one({'Index': question}, { "$set": { 'Used_Times': 1 } })
            return record
        question += 1
        

def insert_questions():
    leet_code = pd.read_csv('Blind_75.csv')
    types = leet_code['Type']
    difficulty = leet_code['Difficulty']
    name = leet_code['Name']
    url = leet_code['URL']

    for i in range(1,len(types)):
        blind_75_collection.insert_one({'Index': i, 'Type': types[i], 'Difficulty': difficulty[i], 'Name': name[i], 'URL': url[i], 'Used_Times': 0})
