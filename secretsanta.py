from collections import defaultdict
import os.path
import random
import argparse
import shutil
import smtplib
from email.message import EmailMessage
from configparser import ConfigParser

parser = argparse.ArgumentParser(description="Randomly assign Secret Santas.")
parser.add_argument('-v', '--verbose', action='store_true', help='log additional info')
parser.add_argument('-c', '--clear', action='store_true', help='delete outputs directory at start')
args = parser.parse_args()

FILE_NAME = 'names.txt'
OUTPUTS_DIR = './outputs'
CONFIG_FILE_NAME='config.cfg'

if args.clear:
    shutil.rmtree(OUTPUTS_DIR, ignore_errors=True)

if not os.path.isfile(FILE_NAME):
    print("names.txt file not found. Please create one.")
    exit(1)

config = ConfigParser()
config.read(CONFIG_FILE_NAME)
my_email = config['credentials']['email']
my_password = config['credentials']['password']

constraints = defaultdict(set)
all_names = []
emails_dict = {}
with open(FILE_NAME) as file:
    for line in file:
        people = line.strip().split(",")
        people = [p.split(":") for p in people]
        names = [p[0] for p in people]
        addresses = [p[1] for p in people]
        for i in range(len(names)):
            constraints[names[i]] = set(names)
            all_names.append(names[i])

            emails_dict[names[i]] = addresses[i]

def validate(arr):
    for name in arr:
        if arr[name] in constraints[name]:
            return False
    return True

other = list(all_names)
random.shuffle(other)
arrangement = dict(zip(all_names, other))
iters = 1
while not validate(arrangement):
    other = list(all_names)
    random.shuffle(other)
    arrangement = dict(zip(all_names, other))
    iters += 1

if args.verbose:
    print(arrangement)
    print(f"Computed in {iters} iterations.")
if not os.path.isdir(OUTPUTS_DIR):
    os.mkdir(OUTPUTS_DIR)
for name, val in arrangement.items():
    with open(f"{OUTPUTS_DIR}/{name}'s recipient.txt", "w") as f:
        f.write(val)

with smtplib.SMTP_SSL('smtp.gmail.com',465) as smtp:
    smtp.login(my_email, my_password)

    for name, address in emails_dict.items():
        msg = EmailMessage()
        msg['Subject'] = 'Your Secret Santa Recipient Is:'
        msg['From'] = my_email
        msg['To'] = address
        msg.set_content(arrangement[name])
        smtp.send_message(msg)        
