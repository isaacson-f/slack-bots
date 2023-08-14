import os
from pymongo import MongoClient
from dotenv import load_dotenv


load_dotenv()
# Provide the mongodb atlas url to connect python to mongodb using pymongo
CONNECTION_STRING = os.environ.get("DATABASE_URL")
client = MongoClient(CONNECTION_STRING)

def get_good_words_collection():

    goodWords = client['test']

    collection = goodWords['good-words']
 
    return collection

def get_blind_75():
    computer_science = client['comp-sci']
    collection = computer_science['blind-75']
    return collection

def get_current_day_leetcode():
    computer_science = client['comp-sci']
    collection = computer_science['current_day']

    return collection

# This is added so that many files can reuse the function get_database()