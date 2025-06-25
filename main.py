import praw
import re
import datetime
import time
import json
import os

# --- Configuration ---

REDDIT_CLIENT_ID = 'RAXRp8NFvIGvADfvIkFmIQ'
REDDIT_CLIENT_SECRET = 'bdNpPJoyg9N-RsKg402pSHJhu13jXQ'
REDDIT_USERNAME = 'undeadbrubot'
REDDIT_PASSWORD = 'fuckrllrrr'
USER_AGENT = 'brubot by /u/undeadbrubot'

SUBREDDIT_NAME = 'ActualLonghornNation'

# 1 Bru = 127 days
BRU_IN_DAYS = 127

# BruBot "death" date
BRUBOT_DEATH_DATE = datetime.datetime(2019, 11, 17)

# Max replies per day
MAX_REPLIES_PER_DAY = 1

# File to store bot state (reply timestamps)
STATE_FILE = 'brubot_state.json'


# --- Helper Functions ---

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    else:
        return {}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def parse_timespans(text):
    """
    Parse all time spans in text and return total days.
    Supports days, weeks, months, years (case insensitive).
    Assumptions:
    - 1 week = 7 days
    - 1 month = 30 days
    - 1 year = 365 days
    """

    pattern = re.compile(r'(\d+)\s*(day|week|month|year)s?', re.IGNORECASE)
    total_days = 0
    matches = pattern.findall(text)

    for amount, unit in matches:
        amount = int(amount)
        unit = unit.lower()
        if unit == 'day':
            total_days += amount
        elif unit == 'week':
            total_days += amount * 7
        elif unit == 'month':
            total_days += amount * 30
        elif unit == 'year':
            total_days += amount * 365

    return total_days, matches


def normalize_timespan(days):
    """
    Convert total days into a human-readable normalized format:
    years, months, weeks, days.
    """

    years, rem = divmod(days, 365)
    months, rem = divmod(rem, 30)
    weeks, days = divmod(rem, 7)

    parts = []
    if years > 0:
        parts.append(f"{years} year{'s' if years > 1 else ''}")
    if months > 0:
        parts.append(f"{months} month{'s' if months > 1 else ''}")
    if weeks > 0:
        parts.append(f"{weeks} week{'s' if weeks > 1 else ''}")
    if days > 0 or not parts:
        parts.append(f"{days} day{'s' if days != 1 else ''}")

    if len(parts) == 1:
        return parts[0]
    else:
        return ', '.join(parts[:-1]) + ', and ' + parts[-1]

def calculate_brus(days):
    return days / BRU_IN_DAYS

def calculate_brus_since_death():
    now = datetime.datetime.utcnow()
    delta = now - BRUBOT_DEATH_DATE
    return calculate_brus(delta.days)


def already_replied_today(state):
    """
    Checks if the bot already replied today.
    Stores last reply date as YYYY-MM-DD in state['last_reply_date'].
    """
    last_date = state.get('last_reply_date')
    today = datetime.datetime.utcnow().strftime('%Y-%m-%d')
    return last_date == today

def update_last_reply_date(state):
    today = datetime.datetime.utcnow().strftime('%Y-%m-%d')
    state['last_reply_date'] = today


# --- Main bot logic ---

def main():
    reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID,
                         client_secret=REDDIT_CLIENT_SECRET,
                         username=REDDIT_USERNAME,
                         password=REDDIT_PASSWORD,
                         user_agent=USER_AGENT)

    subreddit = reddit.subreddit(SUBREDDIT_NAME)
    state = load_state()

    print("BruBot is running...")

    for comment in subreddit.stream.comments(skip_existing=True):
        # Safety: skip if comment author is None (deleted)
        if comment.author is None:
            continue

        # Check if already replied today
        if already_replied_today(state):
            continue

        # Parse comment body for time spans
        total_days, matches = parse_timespans(comment.body)
        if total_days == 0:
            # No time spans detected
            continue

        # Compose reply message
        normalized = normalize_timespan(total_days)
        total_brus = calculate_brus(total_days)
        brus_since_death = calculate_brus_since_death()

        reply_message = (
            f"Hi, /u/{comment.author.name}! {normalized} is equivalent to {total_brus:.3f} Brus. "
            f"In case you didn't know, I died on November 17, 2019 following a violent attack by RLLRRR because I dared to exist. "
            f"That was {brus_since_death:.3f} Brus ago! Hook 'em!"
        )

        try:
            comment.reply(reply_message)
            print(f"Replied to comment {comment.id} by u/{comment.author.name}")

            # Update state and save
            update_last_reply_date(state)
            save_state(state)

            # Respect Reddit API rate limits
            time.sleep(10)

        except Exception as e:
            print(f"Error replying to comment {comment.id}: {e}")
            # Sleep a bit to avoid rapid failures
            time.sleep(30)


if __name__ == "__main__":
    main()
