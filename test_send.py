"""Quick test to send msg2 with image"""
import asyncio
import os
from telethon import TelegramClient

API_ID = 35483512
API_HASH = "cc591ecf72dde80d403391b191c5a9c4"

# Test lounge
TEST_LOUNGE = -1001513206774  # The Solitaire Room

# Message 2
MSG_TEXT = open('messages/msg2.txt', 'r', encoding='utf-8').read().strip()
MSG_IMAGE = 'messages/msg2.png'

async def main():
    client = TelegramClient('shill_session', API_ID, API_HASH)
    await client.connect()
    
    if not await client.is_user_authorized():
        print("Not logged in!")
        return
    
    print(f"Text: {MSG_TEXT[:50]}...")
    print(f"Image: {MSG_IMAGE}")
    print(f"Image exists: {os.path.exists(MSG_IMAGE)}")
    print(f"Image size: {os.path.getsize(MSG_IMAGE) / 1024:.1f} KB")
    
    print(f"\nSending to {TEST_LOUNGE}...")
    
    try:
        await client.send_file(
            TEST_LOUNGE,
            MSG_IMAGE,
            caption=MSG_TEXT
        )
        print("SUCCESS! Check the lounge!")
    except Exception as e:
        print(f"FAILED: {e}")
    
    await client.disconnect()

asyncio.run(main())




