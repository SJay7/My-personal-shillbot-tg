import os

# Get these from https://my.telegram.org/apps
API_ID = os.getenv('API_ID', '')
API_HASH = os.getenv('API_HASH', '')

# Your phone number with country code (e.g., +234...)
PHONE = os.getenv('PHONE', '')

# Interval between posting rounds (minutes)
INTERVAL_MIN = int(os.getenv('INTERVAL_MIN', 15))
INTERVAL_MAX = int(os.getenv('INTERVAL_MAX', 15))

# Delay between each lounge post (seconds) - prevents flood ban
DELAY_MIN = int(os.getenv('DELAY_MIN', 15))
DELAY_MAX = int(os.getenv('DELAY_MAX', 20))

# Session - use StringSession for Railway, file for local
SESSION_STRING = os.getenv('SESSION_STRING', '')  # For Railway
SESSION_NAME = 'shill_session'  # For local file


