import asyncio
import random
import os
import glob
import time
from datetime import datetime
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.messages import GetDialogFiltersRequest
from telethon.errors import FloodWaitError, ChatWriteForbiddenError, UserBannedInChannelError
import config

# Client will be initialized in main() to avoid early file locks
client = None

# Track current message index for rotation
current_msg_index = 0

# Name of your Telegram folder containing shill groups
SHILL_FOLDER_NAME = "Shill Groups"


async def load_lounges_from_folder():
    """Load lounge list from Telegram 'Shill Groups' folder"""
    global client
    lounges = []
    
    try:
        # Get all dialog filters (folders)
        result = await client(GetDialogFiltersRequest())
        
        # Handle both old and new API response formats
        folders = result.filters if hasattr(result, 'filters') else result
        
        target_folder = None
        for folder in folders:
            if hasattr(folder, 'title'):
                title = folder.title
                if hasattr(title, 'text'):
                    title = title.text
                title = str(title)
                
                if title.lower() == SHILL_FOLDER_NAME.lower():
                    target_folder = folder
                    break
        
        if not target_folder:
            print(f"ERROR: Folder '{SHILL_FOLDER_NAME}' not found!")
            return lounges
        
        # Get all dialogs
        dialogs = await client.get_dialogs()
        
        # Build set of IDs in this folder
        if hasattr(target_folder, 'include_peers'):
            included_ids = set()
            for peer in target_folder.include_peers:
                if hasattr(peer, 'channel_id'):
                    included_ids.add(-1000000000000 - peer.channel_id)
                elif hasattr(peer, 'chat_id'):
                    included_ids.add(-peer.chat_id)
            
            # Find matching dialogs
            for dialog in dialogs:
                if dialog.id in included_ids or dialog.entity.id in included_ids:
                    lounges.append(dialog.id)
        
    except Exception as e:
        print(f"Error loading folder: {e}")
    
    return lounges


def load_messages():
    """Load all message templates from messages/ folder"""
    messages = []
    messages_dir = os.path.join(os.path.dirname(__file__), 'messages')
    msg_files = sorted(glob.glob(os.path.join(messages_dir, 'msg*.txt')))
    
    for msg_file in msg_files:
        msg_num = os.path.basename(msg_file).replace('msg', '').replace('.txt', '')
        
        # Read text
        with open(msg_file, 'r', encoding='utf-8') as f:
            text = f.read().strip()
        
        # Check for matching image (skip if > 5MB)
        image_path = None
        for ext in ['.jpg', '.jpeg', '.png', '.gif']:
            potential_image = os.path.join(messages_dir, f'msg{msg_num}{ext}')
            if os.path.exists(potential_image):
                size_mb = os.path.getsize(potential_image) / (1024 * 1024)
                if size_mb > 5:
                    print(f"Skipping large image ({size_mb:.1f}MB): {potential_image}")
                else:
                    image_path = potential_image
                    print(f"Found image ({size_mb:.1f}MB): {potential_image}")
                break
        
        messages.append({
            'text': text,
            'image': image_path
        })
    
    return messages


def get_next_message(messages):
    """Get next message in rotation"""
    global current_msg_index
    if not messages:
        return None
    msg = messages[current_msg_index]
    current_msg_index = (current_msg_index + 1) % len(messages)
    return msg


async def post_to_lounge(lounge, message):
    """Post a message to a single lounge. Returns (success, error, name)"""
    try:
        # First resolve the entity with timeout
        try:
            entity = await asyncio.wait_for(client.get_entity(lounge), timeout=10)
            name = getattr(entity, 'title', None) or getattr(entity, 'name', str(lounge))
        except asyncio.TimeoutError:
            return False, "Timeout finding group", None
        except Exception as e:
            return False, f"Can't find: {str(e)[:30]}", None
        
        # Send with timeout (longer for images)
        try:
            if message['image']:
                try:
                    await asyncio.wait_for(
                        client.send_file(entity, message['image'], caption=message['text']),
                        timeout=120  # 2 minutes for image upload
                    )
                except asyncio.TimeoutError:
                    # If image times out, try text-only as fallback
                    await asyncio.wait_for(
                        client.send_message(entity, message['text']),
                        timeout=30
                    )
                    return True, None, name  # Text sent successfully
                except Exception as img_err:
                    # If photo fails for other reasons, try text-only
                    if "PHOTO" in str(img_err).upper() or "MEDIA" in str(img_err).upper() or "TIMEOUT" in str(img_err).upper():
                        await asyncio.wait_for(
                            client.send_message(entity, message['text']),
                            timeout=30
                        )
                    else:
                        raise img_err
            else:
                await asyncio.wait_for(
                    client.send_message(entity, message['text']),
                    timeout=30
                )
        except asyncio.TimeoutError:
            return False, "Timeout sending", name
            
        return True, None, name
    except FloodWaitError as e:
        return False, f"Flood wait: {e.seconds}s", name
    except ChatWriteForbiddenError:
        return False, "Write forbidden", name
    except UserBannedInChannelError:
        return False, "Banned", name
    except Exception as e:
        return False, str(e)[:50], name if 'name' in dir() else None


async def shill_round(lounges, messages):
    """Post to all lounges"""
    message = get_next_message(messages)
    if not message:
        print("No messages loaded!")
        return
    
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"\n[{timestamp}] Starting shill round with message #{current_msg_index}")
    # Safe print for Windows console (strip emojis for preview)
    preview = message['text'][:50].encode('ascii', 'ignore').decode('ascii')
    print(f"Message preview: {preview}...")
    print(f"Image: {message['image'] or 'None'}")
    print("-" * 50)
    
    success_count = 0
    fail_count = 0
    
    for i, lounge in enumerate(lounges):
        success, error, name = await post_to_lounge(lounge, message)
        display_name = name[:30] if name else str(lounge)
        
        if success:
            print(f"  [{i+1}/{len(lounges)}] {display_name} - OK")
            success_count += 1
        else:
            print(f"  [{i+1}/{len(lounges)}] {display_name} - FAILED: {error}")
            fail_count += 1
        
        # Random delay between posts
        delay = random.uniform(config.DELAY_MIN, config.DELAY_MAX)
        await asyncio.sleep(delay)
    
    print("-" * 50)
    print(f"Round complete: {success_count} sent, {fail_count} failed")


async def main():
    global client
    
    print("=" * 50)
    print("SHILL BOT - Telegram Folder Edition")
    print("=" * 50)
    
    # Load messages first (doesn't need Telegram connection)
    messages = load_messages()
    print(f"Loaded {len(messages)} message templates")
    
    if not messages:
        print("ERROR: No messages found. Add msg1.txt to messages/")
        return
    
    # Wait a moment to ensure any previous session locks are released
    time.sleep(1)
    
    # Initialize client - use StringSession for Railway, file for local
    if config.SESSION_STRING:
        print("Using StringSession (Railway mode)")
        client = TelegramClient(StringSession(config.SESSION_STRING), config.API_ID, config.API_HASH)
    else:
        print("Using file session (local mode)")
        client = TelegramClient(config.SESSION_NAME, config.API_ID, config.API_HASH)
    
    # Connect
    print("\nConnecting to Telegram...")
    await client.connect()
    
    if not await client.is_user_authorized():
        print("ERROR: Not logged in. Run 'python login.py' first!")
        await client.disconnect()
        return
    
    me = await client.get_me()
    print(f"Logged in as: {me.first_name} (@{me.username})")
    
    # Load lounges from Telegram folder
    print(f"\nLoading groups from '{SHILL_FOLDER_NAME}' folder...")
    lounges = await load_lounges_from_folder()
    print(f"Found {len(lounges)} groups in folder")
    
    if not lounges:
        print(f"ERROR: No groups found in '{SHILL_FOLDER_NAME}' folder!")
        print("Make sure you have a folder with that exact name in Telegram.")
        await client.disconnect()
        return
    
    print(f"\nSchedule: Every {config.INTERVAL_MIN}-{config.INTERVAL_MAX} minutes")
    print("Press Ctrl+C to stop\n")
    
    # Main loop
    try:
        while True:
            try:
                # Refresh lounges from folder before each round (catches new groups!)
                lounges = await load_lounges_from_folder()
                print(f"[Refresh] {len(lounges)} groups in '{SHILL_FOLDER_NAME}' folder")
                
                await shill_round(lounges, messages)
                
                # Random interval until next round
                interval = random.uniform(config.INTERVAL_MIN * 60, config.INTERVAL_MAX * 60)
                next_run = datetime.now().timestamp() + interval
                next_time = datetime.fromtimestamp(next_run).strftime('%H:%M:%S')
                print(f"\nNext round at {next_time} (in {int(interval/60)} minutes)")
                
                await asyncio.sleep(interval)
                
            except KeyboardInterrupt:
                print("\n\nStopping bot...")
                break
    finally:
        # Always disconnect properly
        if client:
            await client.disconnect()
            print("Disconnected.")


if __name__ == '__main__':
    asyncio.run(main())


