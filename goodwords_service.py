from datetime import datetime, timezone
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import logging
import os
import mongo_client
from typing import Optional, List, Union
import random


client = WebClient(token=os.environ.get("SLACK_TOKEN"))

good_words_collection = mongo_client.get_good_words_collection()

EMOJIS = os.environ.get("VALID_EMOJIS").split(' ')

def add_historical_goodwords():
    # Call the conversations.list method using the WebClient
    result = client.conversations_history(channel="C0441R6SKBN")
    conversation_history = result["messages"]
    for message in conversation_history:
        word = message['text']
        date_millis = float(message['ts'])
        user_id = message['user']
        temp_list = list(filter(lambda a: len(a) > 0, word.split(" ")))
        if len(temp_list) == 1:
            handle_word_sent(temp_list[0], date_millis, user_id, True)

def process_event(event: object):
    if event.get('text', False) and event.get('ts', False) and event.get('user', False):
        if event.get('thread_ts', False):
            print(f"Replies to posts not accepted.")
            return
        message = event['text']
        millis_time = float(event['ts'])
        user = event['user']
        channel = event['channel']
        temp_list = list(filter(lambda a: len(a) > 0, message.split(" ")))
        if channel == "C06B6R5BC12":
            handle_note_added(message)
        elif channel == "C0441R6SKBN" and len(temp_list) == 1: 
            handle_word_sent(temp_list[0], millis_time, user)
        else:
            print(f"invalid submission: {message}")
    else:
        print(f"Event missing attribute ts or text: {event}")

def handle_note_added(note):
    print(note)

def handle_word_sent(word: str, millis_time: float, user_id: str, historical: bool=False):
    prev_sent = find_word(word)
    if prev_sent is not None:
        if not historical:
            client.chat_postMessage(channel="C0441R6SKBN", text=f"{word} was previously sent on {datetime.fromtimestamp(prev_sent['date_millis']).strftime('%m/%d/%Y')}", thread_ts=str(millis_time))
        print(f"Thread Time: {datetime.fromtimestamp(prev_sent['date_millis']).strftime('%m/%d/%Y')}, Prev Sent Word: {word}")
    elif not historical:
        insert_new_word(word, millis_time, user_id)
        client.reactions_add(channel="C0441R6SKBN", name=random.choice(EMOJIS), timestamp=str(millis_time))
    else:
        insert_new_word(word, millis_time, user_id)


def insert_new_word(word: str, date_millis: float, user: str):
    word_lowercase = word.lower()
    document = {
        "word": word_lowercase,
        "date_millis": date_millis,
        "user_id": user
    }
    good_words_collection.insert_one(document)
    print(f"Successfully added word: \n {document['word']} \n millis: {document['date_millis']}")


def find_word(word: str):
    result = good_words_collection.find_one({"word": word.lower()})
    print(f"Found: {result}")
    return result