
import re
from mongo_client import get_beta_slack
from datetime import datetime

brothers_collection = get_beta_slack()
with open('slack-members.csv', 'r') as brothers:
    brother_list = brothers.readlines()
    for i in range(1, len(brother_list)):
        brother_slack_object = {}
        new_details = brother_list[i].split(',')
        if new_details[2] != "Deactivated" and new_details[2] != "Bot":
            full_name = new_details[7].split(' ')
            print(full_name)
            brother_slack_object["username"] = new_details[0].lower()
            brother_slack_object["email"] = new_details[1].lower()
            if len(full_name) == 2:
                brother_slack_object["firstName"] = full_name[0].lower().strip('"')
                brother_slack_object["lastName"] = full_name[1].lower().strip('"')
            output = brothers_collection.insert_one(brother_slack_object)
            print(output)
'''            full_name = new_details[7].split(' ')
            brother_object["lastName"] = full_name[1]
            brother_object["firstName"] = full_name[0]
            brother_object["email"] = new_details[1]
            print(f'Inserting {brother_object}')
            output = brothers_collection.insert_one(brother_object)
            print(output)'''