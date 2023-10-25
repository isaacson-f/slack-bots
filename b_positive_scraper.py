from datetime import datetime
import os
from bs4 import BeautifulSoup
import requests
from slack_sdk import WebClient

from mongo_client import get_beta_members, get_b_positive_collection, get_beta_slack

brothers_collection = get_beta_members()

b_positive_collection = get_b_positive_collection()

slack_collection = get_beta_slack()

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
                # first look for matching first and last names
                doc = brothers_collection.find_one({"lastName": name_list[1].lower().strip(), "firstName": name_list[0].lower().strip()})
                # if there is nothing found (due to nicknames etc.) check for just last name
                if not doc:
                     doc = brothers_collection.find_one({"lastName": name_list[1].lower().strip()})
                if len(name_list) > 2:
                     doc = brothers_collection.find_one({"firstName": name_list[0].lower().strip()})
                if not doc is None:
                    exists = b_positive_collection.find_one({"brother_email": doc["email"]})
                    if exists is None:
                        b_positive_profile = {}
                        b_positive_profile["brother_email"] = doc["email"]
                        b_positive_profile["total_money_raised"] = float(element["data-donation-amount"])
                        b_positive_profile["periodical_money_raised"] = {"fall_2023": 0}
                        b_positive_profile["last_donation"] = datetime(2023,10,1)
                        print(f"INSERTING: {b_positive_profile}")
                        b_positive_collection.insert_one(b_positive_profile)
                    else:
                         print(f'BROTHER WITH EMAIL: {exists["brother_email"]} EXISTS')
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
            doc = brothers_collection.find_one({"lastName": name_list[1].lower().strip(), "firstName": name_list[0].lower().strip()})
                # if there is nothing found (due to nicknames etc.) check for just last name
            if not doc:
                doc = brothers_collection.find_one({"lastName": name_list[1].lower().strip()})
            if len(name_list) > 2:
                doc = brothers_collection.find_one({"firstName": name_list[0].lower().strip()})
            elif doc is None:
                print(f'LOOKING FOR: {name_list[1].lower()} ON SLACK')
                doc = slack_collection.find_one({"lastName": name_list[1].lower()})
            if not doc is None:
                print(f"LOOKING FOR {doc['email']}")
                b_positive_profile = b_positive_collection.find_one({"brother_email": doc["email"]})
                if b_positive_profile is None:
                    print(f"COULD NOT FIND {doc['email']}, INSERTING INTO B+ DB")
                    b_positive_profile = {}
                    b_positive_profile["brother_email"] = doc["email"]
                    b_positive_profile["total_money_raised"] = float(element["data-donation-amount"])
                    b_positive_profile["periodical_money_raised"] = {"fall_2023": float(element["data-donation-amount"])}
                    b_positive_profile["last_donation"] = datetime.today()
                    print(f"INSERTING: {b_positive_profile}")
                    b_positive_collection.insert_one(b_positive_profile)
                raised_diff = float(element["data-donation-amount"]) - b_positive_profile["total_money_raised"]
                b_positive_profile["total_money_raised"] = float(element["data-donation-amount"])
                if raised_diff > 0:
                    cur_amount = b_positive_profile["periodical_money_raised"]["fall_2023"]
                    b_positive_profile["periodical_money_raised"]["fall_2023"] = cur_amount + raised_diff
                    b_positive_profile["last_donation"] = datetime.today()
                    b_positive_collection.replace_one({"brother_email": doc["email"]}, b_positive_profile)
                    print(f"{doc['firstName']} {doc['lastName']} RAISED {cur_amount} THE WEEK OF {datetime.today()}")
                else:
                    print(f"{doc['firstName']} {doc['lastName']} DID NOT RAISE ANY MONEY THE WEEK OF {datetime.today()}")
            elif doc is None:
                print(f'NAME: {name_list[1].lower()}')
                print(f'AMOUNT: {element["data-donation-amount"]}')


def find_current_donations():
    profiles = b_positive_collection.find()
    b_positive_profiles = []
    for profile in profiles:
        doc = brothers_collection.find_one({"email": profile["brother_email"]})
        if not doc:
            doc = slack_collection.find_one({"email": profile["brother_email"]})
        cur_dict = {
              "first_name": doc["firstName"],
              "last_name": doc["lastName"],
              "total_money_raised": profile["total_money_raised"],
              "cur_sem_raised": profile["periodical_money_raised"]['fall_2023'],
              "last_donation": profile["last_donation"]
         }
        b_positive_profiles.append(cur_dict)
    leaderboard = {}
    leaderboard["shame_list"] = []
    for profile in b_positive_profiles:
         if profile["total_money_raised"] == 0:
              leaderboard["shame_list"].append(profile)
    b_positive_profiles.sort(key=lambda a: float(a["total_money_raised"]), reverse=True)
    leaderboard["first_all_time"], leaderboard["second_all_time"], leaderboard["third_all_time"] = b_positive_profiles[0], b_positive_profiles[1], b_positive_profiles[2]
    end_index = len(b_positive_profiles)-1
    leaderboard["last_all_time"], leaderboard["second_last_all_time"], leaderboard["third_last_all_time"] = b_positive_profiles[end_index], b_positive_profiles[end_index-1], b_positive_profiles[end_index-2]
    b_positive_profiles.sort(key=lambda a: float(a["cur_sem_raised"]), reverse=True)
    print(b_positive_profiles[:3])
    leaderboard["first_cur_sem"], leaderboard["second_cur_sem"], leaderboard["third_cur_sem"], leaderboard["fourth_cur_sem"], leaderboard["fifth_cur_sem"]= b_positive_profiles[0], b_positive_profiles[1], b_positive_profiles[2], b_positive_profiles[3], b_positive_profiles[4]
    leaderboard["last_cur_sem"], leaderboard["second_last_cur_sem"], leaderboard["third_last_cur_sem"] = b_positive_profiles[end_index], b_positive_profiles[end_index-1], b_positive_profiles[end_index-2]
    send_donation_update(leaderboard)

def send_donation_update(leaderboard):
    all_time_leaders = (leaderboard['first_all_time'], leaderboard['second_all_time'], leaderboard['third_all_time'])
    current_sem_leaders = (leaderboard['first_cur_sem'], leaderboard['second_cur_sem'], leaderboard['third_cur_sem'], leaderboard['fourth_cur_sem'], leaderboard['fifth_cur_sem'])
    shame_message = ":( \bBrothers with zero dollars donated -"
    for profile in leaderboard["shame_list"]:
         shame_message += f" {profile['first_name'].title()} {profile['last_name'].title()},"
    shame_message = shame_message[:-1]

    message = f"B+ Fundraising Update! \n All Time Leaders: \n 1st - {all_time_leaders[0]['first_name'].title()} {all_time_leaders[0]['last_name'].title()[0]} with ${all_time_leaders[0]['total_money_raised']} raised \n 2nd - {all_time_leaders[1]['first_name'].title()} {all_time_leaders[1]['last_name'].title()[0]} with ${all_time_leaders[1]['total_money_raised']} raised \n 3rd - {all_time_leaders[2]['first_name'].title()} {all_time_leaders[2]['last_name'].title()[0]} with ${all_time_leaders[2]['total_money_raised']} raised \n"
    least_raised = f"Current Sem Leaders \n 1st - {current_sem_leaders[0]['first_name'].title()} {current_sem_leaders[0]['last_name'].title()[0]} with ${current_sem_leaders[0]['cur_sem_raised']} raised \n 2nd - {current_sem_leaders[1]['first_name'].title()} {current_sem_leaders[1]['last_name'].title()[0]} with ${current_sem_leaders[1]['cur_sem_raised']} raised \n 3rd - {current_sem_leaders[2]['first_name'].title()} {current_sem_leaders[2]['last_name'].title()[0]} with ${current_sem_leaders[2]['cur_sem_raised']} raised \n 4th - {current_sem_leaders[3]['first_name'].title()} {current_sem_leaders[3]['last_name'].title()[0]} with ${current_sem_leaders[3]['cur_sem_raised']} raised\n 5th - {current_sem_leaders[4]['first_name'].title()} {current_sem_leaders[4]['last_name'].title()[0]} with ${current_sem_leaders[4]['cur_sem_raised']} raised \nLFG :fire:"
    message += least_raised
    #message += shame_message

    client.chat_postMessage(channel="C0431QCLX18", text=message)


# Nick -> Nicholas
# Gabriel -> gabe