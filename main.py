import praw
import datetime

# Set up the Reddit API credentials
reddit = praw.Reddit(client_id='RAXRp8NFvIGvADfvIkFmIQ',
                     client_secret='bdNpPJoyg9N-RsKg402pSHJhu13jXQ',
                     username='undeadbrubot',
                     password='fuckrllrrr',
                     user_agent='brubot by /u/undeadbrubot')

# Set the target username for the bot to respond to
target_username = 'gordogg24p'

# Set the base date to calculate the number of days from
base_date = datetime.datetime(2019, 11, 17)

# Set the message that the bot will respond with
response_message = 'Hey, {0}! It has been {1} Brus since {2} when you had me unceremoniously murdered for the crime of simply existing.'

# Set the maximum number of responses allowed per day
max_responses_per_day = 10

# Set the time window for counting the number of responses (in hours)
response_time_window = 24

# Initialize the response counter and the timestamp of the last response
response_count = 0
last_response_timestamp = datetime.datetime.now()

# Monitor the comments on a specific subreddit
subreddit = reddit.subreddit('ActualLonghornNation')
for comment in subreddit.stream.comments(skip_existing=True):
    if comment.author.name == target_username:
        # Check if enough time has passed since the last response
        time_since_last_response = datetime.datetime.now() - last_response_timestamp
        if time_since_last_response.total_seconds() / 3600 >= response_time_window:
            response_count = 0
        
        # Check if the response limit has been reached
        if response_count < max_responses_per_day:
            days_since_base = (datetime.datetime.now() - base_date).days / 126
            comment.reply(response_message.format(target_username, days_since_base, base_date.strftime('%B %d, %Y')))
            response_count += 1
            last_response_timestamp = datetime.datetime.now()