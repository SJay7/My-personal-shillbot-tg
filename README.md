# Shill Bot - Telegram Lounge Scheduler

Automated posting to Telegram shill lounges with message rotation.

## Setup

### 1. Get Telegram API Credentials

1. Go to https://my.telegram.org/apps
2. Log in with your phone number
3. Create a new application (any name)
4. Copy the `api_id` and `api_hash`

### 2. Install Dependencies

```bash
cd shill-bot
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Set these environment variables:

```bash
# Windows PowerShell
$env:API_ID="your_api_id"
$env:API_HASH="your_api_hash"
$env:PHONE="+234xxxxxxxxxx"

# Linux/Mac
export API_ID="your_api_id"
export API_HASH="your_api_hash"
export PHONE="+234xxxxxxxxxx"
```

Optional settings (have defaults):
- `INTERVAL_MIN` - Minimum minutes between rounds (default: 30)
- `INTERVAL_MAX` - Maximum minutes between rounds (default: 60)
- `DELAY_MIN` - Minimum seconds between each lounge post (default: 5)
- `DELAY_MAX` - Maximum seconds between each lounge post (default: 15)

### 4. Add Your Lounges

Edit `lounges.txt` - one lounge per line:

```
cryptoshills
monadpromo
-1001234567890
```

Can use:
- Username (without @)
- Group/Channel ID (negative number)

### 5. Add Your Messages

Edit files in `messages/` folder:

- `msg1.txt` - First message text
- `msg1.jpg` - First message image (optional)
- `msg2.txt` - Second message text
- `msg2.png` - Second message image (optional)
- ... up to as many as you want

Messages rotate automatically.

### 6. Run

```bash
python bot.py
```

First run will ask for a verification code sent to your Telegram.

## How It Works

1. Bot logs into YOUR account (userbot)
2. Loads lounges and messages
3. Every 30-60 minutes:
   - Picks next message in rotation
   - Posts to all lounges
   - Random delay between each post (prevents flood ban)
4. Repeats until you stop it

## Railway Deployment (Run 24/7)

### 1. Generate StringSession (run locally once)

```bash
$env:API_ID="your_api_id"
$env:API_HASH="your_api_hash"
python generate_session.py
```

This will prompt for phone/code and output a long string. Copy it!

### 2. Deploy to Railway

1. Push code to GitHub
2. Go to https://railway.app and connect your repo
3. Add environment variables:
   - `API_ID` - Your Telegram API ID
   - `API_HASH` - Your Telegram API Hash
   - `SESSION_STRING` - The string from step 1
   - `INTERVAL_MIN` - Minutes between rounds (default: 15)
   - `INTERVAL_MAX` - Minutes between rounds (default: 15)
   - `DELAY_MIN` - Seconds between posts (default: 15)
   - `DELAY_MAX` - Seconds between posts (default: 20)

4. Deploy! Bot will run 24/7

### 3. Create Telegram Folder

Create a folder in Telegram called "Shill Groups" and add all your lounges there.
The bot reads from this folder - add/remove groups anytime!

## Notes

- First login requires phone verification (one-time)
- Session is saved locally - won't ask again
- If you get flood-waited, bot shows the wait time
- Failed posts are logged but don't stop the bot
- Use responsibly - only in actual shill lounges

