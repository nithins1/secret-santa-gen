# Secret Santa Generator

A Python script that randomly assigns Secret Santa pairs while respecting exclusion constraints (e.g., spouses, family members).

## Features

- **JSON-based configuration**: Easy-to-edit list of participants with names, emails, and exclusion lists
- **Fair randomization**: Uses uniform random sampling to ensure all valid arrangements are equally likely
- **Constraint handling**: Prevents matching people in each other's exclusion lists and self-assignments
- **Email notifications**: Automatically sends Secret Santa assignments via Gmail
- **Output files**: Creates individual text files with each person's recipient

## Setup

### Requirements

- Python 3.6+
- Standard library only (no external dependencies)

### Configuration Files

#### 1. `names.json`

Create a `names.json` file with your participants:

```json
[
  {
    "name": "Alice",
    "email": "alice@example.com",
    "exclusions": ["Bob"]
  },
  {
    "name": "Bob",
    "email": "bob@example.com",
    "exclusions": ["Alice"]
  },
  {
    "name": "Charlie",
    "email": "charlie@example.com",
    "exclusions": []
  }
]
```

**Fields:**
- `name`: Participant's name
- `email`: Email address for notifications
- `exclusions`: List of names this person cannot be matched with (e.g., spouse, family members)

**Note:** If Alice excludes Bob, you should also add Alice to Bob's exclusions list to ensure they can't be matched in either direction.

#### 2. `config.cfg`

Create a `config.cfg` file with your Gmail credentials:

```ini
[credentials]
email=your-email@gmail.com
password=your-app-password
```

**Important:** Use a Gmail [App Password](https://support.google.com/accounts/answer/185833), not your regular password.

**For testing:** Comment out the credentials with `##` to prevent accidental email sending:
```ini
[credentials]
##email=your-email@gmail.com
##password=your-app-password
```

### Clean Template Files

The repository includes `.clean` template files:
- `names.json.clean`: Example participant list
- `config.cfg.clean`: Example config file

Copy these to `names.json` and `config.cfg` and modify them with your actual data.

## Usage

### Basic Usage

```bash
python secretsanta.py
```

This will:
1. Generate random Secret Santa assignments
2. Create output files in `./outputs/` directory
3. Send emails to all participants

### Command Line Options

```bash
python secretsanta.py [OPTIONS]
```

**Options:**
- `-n, --noemail`: Generate assignments but don't send emails (useful for testing)
- `-v, --verbose`: Print the arrangement and iteration count
- `-c, --clear`: Delete the outputs directory before generating new assignments

**Examples:**

```bash
# Test without sending emails
python secretsanta.py --noemail

# See the assignments and statistics
python secretsanta.py --noemail --verbose

# Clear old outputs and generate fresh assignments
python secretsanta.py --clear --noemail
```

## Output

The script creates an `./outputs/` directory with individual files:
- `Alice's recipient.txt`
- `Bob's recipient.txt`
- etc.

Each file contains only the name of that person's Secret Santa recipient.

## How It Works

1. **Loads participants** from `names.json`
2. **Builds constraint set** from exclusion lists
3. **Generates random arrangements** by shuffling the participant list
4. **Validates arrangement** to ensure:
   - No one is matched with themselves
   - No one is matched with someone in their exclusions list
5. **Repeats** until a valid arrangement is found (typically 1-100 iterations)
6. **Outputs** results to files and/or emails

The algorithm uses uniform random sampling, meaning every valid arrangement has an equal probability of being selected.

## Safety Features

- **Iteration limit**: Stops after 100,000 attempts if no valid arrangement can be found
- **Config isolation**: Only reads email credentials when actually sending emails
- **Test mode**: `--noemail` flag prevents accidental email sending during testing

## Troubleshooting

**"names.json file not found"**
- Create a `names.json` file in the same directory as the script
- See the Configuration Files section above for the format

**"KeyError: 'email'" when running without `--noemail`**
- Your `config.cfg` file is missing or incorrectly formatted
- Make sure credentials aren't commented out with `#` or `##`

**"Could not find valid arrangement after 100000 attempts"**
- Your exclusion constraints may be too restrictive
- Check that a valid arrangement is mathematically possible
- For N people, you need enough flexibility for everyone to be matched

## Tips

- Always test with `--noemail` flag first
- Use the `--verbose` flag to see how many iterations were needed
- Keep exclusion lists minimal to ensure valid arrangements exist
- For couples/families, make sure exclusions are bidirectional
