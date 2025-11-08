from collections import defaultdict
import os.path
import random
import argparse
import shutil
import smtplib
import json
from email.message import EmailMessage
from configparser import ConfigParser

parser = argparse.ArgumentParser(description="Randomly assign Secret Santas.")
parser.add_argument('-v', '--verbose', action='store_true', help='log additional info')
parser.add_argument('-c', '--clear', action='store_true', help='delete outputs directory at start')
parser.add_argument('-n', '--noemail', action='store_true', help='do not send emails')
args = parser.parse_args()

FILE_NAME = 'names.json'
OUTPUTS_DIR = './outputs'
CONFIG_FILE_NAME='config.cfg'

if args.clear:
    shutil.rmtree(OUTPUTS_DIR, ignore_errors=True)

if not os.path.isfile(FILE_NAME):
    print("names.json file not found. Please create one.")
    exit(1)

constraints = defaultdict(set)
all_names = []
emails_dict = {}

with open(FILE_NAME) as file:
    people_data = json.load(file)

for person in people_data:
    name = person['name']
    email = person['email']
    exclusions = person.get('exclusions', [])

    all_names.append(name)
    emails_dict[name] = email
    constraints[name] = set(exclusions)

def validate(arr):
    """Check if arrangement is valid: no one in exclusion list and no self-assignment."""
    for name in arr:
        if arr[name] in constraints[name] or arr[name] == name:
            return False
    return True

# Generate arrangements by random shuffling until we find a valid one
other = list(all_names)
random.shuffle(other)
arrangement = dict(zip(all_names, other))
iters = 1
while not validate(arrangement):
    other = list(all_names)
    random.shuffle(other)
    arrangement = dict(zip(all_names, other))
    iters += 1
    if iters > 100000:  # Safety check
        print("Could not find valid arrangement after 100000 attempts. Check your constraints.")
        exit(1)

if args.verbose:
    print(arrangement)
    print(f"Computed in {iters} iterations.")
if not os.path.isdir(OUTPUTS_DIR):
    os.mkdir(OUTPUTS_DIR)
for name, val in arrangement.items():
    with open(f"{OUTPUTS_DIR}/{name}'s recipient.txt", "w") as f:
        f.write(val)

if not args.noemail:
    config = ConfigParser()
    config.read(CONFIG_FILE_NAME)
    my_email = config['credentials']['email']
    my_password = config['credentials']['password']

    with smtplib.SMTP_SSL('smtp.gmail.com',465) as smtp:
        smtp.login(my_email, my_password)

        for name, address in emails_dict.items():
            msg = EmailMessage()
            msg['Subject'] = 'Your Secret Santa Recipient Is:'
            msg['From'] = my_email
            msg['To'] = address
            msg.set_content(f'Your Secret Santa Recipient Is: {arrangement[name]}')
            smtp.send_message(msg)        
