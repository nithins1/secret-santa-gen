from collections import defaultdict
import os.path
import random
import argparse
import shutil

parser = argparse.ArgumentParser(description="Randomly assign Secret Santas.")
parser.add_argument('-v', '--verbose', action='store_true', help='log additional info')
parser.add_argument('-c', '--clear', action='store_true', help='delete outputs directory and exit')
args = parser.parse_args()

FILE_NAME = 'names.txt'
OUTPUTS_DIR = './outputs'

if args.clear:
    print("helo")
    shutil.rmtree(OUTPUTS_DIR, ignore_errors=True)
    exit(0)

if not os.path.isfile(FILE_NAME):
    print("names.txt file not found. Please create one.")
    exit(1)

constraints = defaultdict(list)
all_names = []
with open(FILE_NAME) as file:
    for line in file:
        names = line.strip().split(",")
        for i in range(len(names)):
            constraints[names[i]] = set(names)
            all_names.append(names[i])

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
