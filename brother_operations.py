
import re
from mongo_client import get_beta_members
from datetime import datetime

brothers_collection = get_beta_members()
with open('active_brothers.csv', 'r') as brothers:
    brother_list = brothers.readlines()
    for i in range(1, len(brother_list)):
        brother_object = {}
        new_details = brother_list[i].split(',')
        for i in range(len(new_details)):
            new_details[i].strip()
            new_details[i] = new_details[i].lower()
            if i == 5:
                datetime_object = datetime.strptime(new_details[i], '%m/%d/%y')
                new_details[i] = datetime_object

        if len(new_details) == 17:
            brother_object["lastName"] = new_details[1]
            brother_object["firstName"] = new_details[2]
            brother_object["email"] = new_details[3]
            brother_object["birthday"] = new_details[5]
            brother_object["pledgeClass"] = new_details[6]
            brother_object["rollNumber"] = new_details[7]
            brother_object["venmo"] = new_details[8]
            brother_object["major"] = new_details[9]
            brother_object["plannedGraduation"] = new_details[10]
            brother_object["tShirtSize"] = new_details[11]
            brother_object["coopOrClass"] = new_details[12]
            brother_object["active"] = new_details[13]
            print(f'Inserting {brother_object}')
            output = brothers_collection.insert_one(brother_object)
            print(output)
        if new_details[2] == "Joshua" and new_details[1] == "Fernandez" or new_details[2] == "Gabriel" and new_details[1] == "Lynch":
            print(new_details)