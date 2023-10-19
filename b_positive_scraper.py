from datetime import datetime
import os
from bs4 import BeautifulSoup
import requests
from slack_sdk import WebClient

from mongo_client import get_beta_members, get_b_positive_collection

brothers_collection = get_beta_members()

b_positive_collection = get_b_positive_collection()

client = WebClient(token=os.environ.get("SLACK_TOKEN"))

def insert_all_brothers_in_db():
    html_page = requests.get(os.environ.get("B_POSITIVE_URL"))
    soup = BeautifulSoup(html_page.text, 'html.parser')
    donation_list = soup.findAll('ul')
    people_in_org = donation_list[2]
    for element in people_in_org:
            filter_object = element.text.replace('\n', '')
            if filter_object:
                name = element["data-name"]
                name_list = list(filter(lambda a: len(a) > 0, name.split(' ')))
                doc = brothers_collection.find_one({"lastName": name_list[1]})
                if len(name_list) > 2:
                     doc = brothers_collection.find_one({"firstName": name_list[0]})
                if not doc is None:
                    b_positive_profile = {}
                    b_positive_profile["brother_email"] = doc["email"]
                    b_positive_profile["total_money_raised"] = float(element["data-donation-amount"])
                    b_positive_profile["periodical_money_raised"] = {"fall_2023": 0}
                    b_positive_profile["last_donation"] = datetime(2023,1,1)
                    b_positive_collection.insert_one(b_positive_profile)
                
                elif doc is None:
                    print(f'NAME: {name_list}')
                    print(f'AMOUNT: {element["data-donation-amount"]}')


def update_donations():
    html_page = requests.get(os.environ.get("B_POSITIVE_URL"))
    soup = BeautifulSoup(html_page.text, 'html.parser')
    donation_list = soup.findAll('ul')
    people_in_org = donation_list[2]
    for element in people_in_org:
            filter_object = element.text.replace('\n', '')
            if filter_object:
                name = element["data-name"]
                name_list = list(filter(lambda a: len(a) > 0, name.split(' ')))
                doc = brothers_collection.find_one({"lastName": name_list[1]})
                if len(name_list) > 2:
                     doc = brothers_collection.find_one({"firstName": name_list[0]})
                if not doc is None:
                    b_positive_profile = b_positive_collection.find_one({"brother_email":doc["email"]})
                    raised_diff = element["data-donation-amount"] - b_positive_profile["total_money_raised"]
                    if raised_diff > 0:
                        cur_amount = b_positive_profile["periodical_money_raised"][0]["fall_2023"]
                        b_positive_profile["periodical_money_raised"][0]["fall_2023"] = cur_amount + raised_diff
                    b_positive_profile["last_donation"] = datetime.today()
                    print(f"{doc['firstName']} {doc['lastName']} RAISED {cur_amount} THE WEEK OF {datetime.today()}")
                    b_positive_collection.update_one({"brother_email": doc["email"]}, b_positive_profile)
                elif doc is None:
                    print(f'NAME: {name_list}')
                    print(f'AMOUNT: {element["data-donation-amount"]}')

def find_current_donations():
    profiles = b_positive_collection.find()
    b_positive_profiles = []
    for profile in profiles:
        doc = brothers_collection.find_one({"email": profile["brother_email"]})
        cur_dict = {
              "first_name": doc["firstName"],
              "last_name": doc["lastName"],
              "total_money_raised": profile["total_money_raised"],
              "cur_sem_raised": profile["periodical_money_raised"][0]['fall_2023'],
              "last_donation": profile["last_donation"]
         }
        b_positive_profiles.append(cur_dict)
    b_positive_profiles.sort(key=lambda a: float(a["total_money_raised"]), reverse=True)
    print(b_positive_profiles)

# Nick -> Nicholas
# Gabriel -> gabe


