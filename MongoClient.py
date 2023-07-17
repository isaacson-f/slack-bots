import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def get_database():
 
   # Provide the mongodb atlas url to connect python to mongodb using pymongo
   CONNECTION_STRING = os.environ.get("DATABASE_CONNECTION")
 
   # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
   client = MongoClient(CONNECTION_STRING)
 
   # Create the database for our example (we will use the same database throughout the tutorial
   return client['user_shopping_list']
  
# This is added so that many files can reuse the function get_database()
