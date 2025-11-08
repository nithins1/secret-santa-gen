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
parser.add_argument('-s', '--send-only', action='store_true', help='send emails using existing output files (do not regenerate)')
args = parser.parse_args()

FILE_NAME = 'names.json'
OUTPUTS_DIR = './outputs'
CONFIG_FILE_NAME='config.cfg'

if not os.path.isfile(FILE_NAME):
    print("names.json file not found. Please create one.")
    exit(1)

# Load participant data
with open(FILE_NAME) as file:
    people_data = json.load(file)

all_names = []
emails_dict = {}
constraints = defaultdict(set)

for person in people_data:
    name = person['name']
    email = person['email']
    exclusions = person.get('exclusions', [])

    all_names.append(name)
    emails_dict[name] = email
    constraints[name] = set(exclusions)

# Check for --send-only mode
if args.send_only:
    # Read arrangement from existing output files
    if not os.path.isdir(OUTPUTS_DIR):
        print(f"Error: {OUTPUTS_DIR} directory not found. Run without --send-only first to generate assignments.")
        exit(1)

    arrangement = {}
    for name in all_names:
        output_file = f"{OUTPUTS_DIR}/{name}'s recipient.txt"
        if not os.path.isfile(output_file):
            print(f"Error: {output_file} not found. Run without --send-only first to generate assignments.")
            exit(1)
        with open(output_file) as f:
            arrangement[name] = f.read().strip()

    if args.verbose:
        print("Loaded arrangement from existing output files:")
        print(arrangement)
else:
    # Generate new arrangement
    if args.clear:
        shutil.rmtree(OUTPUTS_DIR, ignore_errors=True)

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

    # Write output files
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

    print(f"Sending emails from {my_email}...")
    with smtplib.SMTP_SSL('smtp.gmail.com',465) as smtp:
        smtp.login(my_email, my_password)

        for name, address in emails_dict.items():
            msg = EmailMessage()
            msg['Subject'] = 'Your Secret Santa Recipient Is:'
            msg['From'] = my_email
            msg['To'] = address
            msg.set_content(f'Your Secret Santa Recipient Is: {arrangement[name]}')
            smtp.send_message(msg)
            if args.verbose:
                print(f"  Sent to {name} ({address})")

    print(f"Successfully sent {len(emails_dict)} emails.")        
