import os
from pymongo import MongoClient
from dotenv import load_dotenv


def get_good_words_collection():
    load_dotenv()
   # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = os.environ.get("DATABASE_URL")

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient(CONNECTION_STRING)

    goodWords = client['test']

    collection = goodWords['good-words']
 
    return collection
  
# This is added so that many files can reuse the function get_database()