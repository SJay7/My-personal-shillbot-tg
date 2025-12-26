"""Test script to check lounge access"""
import asyncio
from telethon import TelegramClient

API_ID = 35483512
API_HASH = "cc591ecf72dde80d403391b191c5a9c4"

lounges = ["TheSolitaireRoom", "Charleslounge", "FOMOLounge"]

async def main():
    client = TelegramClient('shill_session', API_ID, API_HASH)
    await client.connect()
    
    if not await client.is_user_authorized():
        print("Not logged in! Run login.py first")
        return
    
    me = await client.get_me()
    print(f"Logged in as: {me.first_name}\n")
    
    # List all dialogs (chats you're in)
    print("Your groups/channels:")
    print("-" * 40)
    async for dialog in client.iter_dialogs():
        if dialog.is_group or dialog.is_channel:
            print(f"  {dialog.name} | ID: {dialog.id}")
    
    print("\n" + "-" * 40)
    print("Testing lounges from lounges.txt:")
    print("-" * 40)
    
    for lounge in lounges:
        print(f"\nTrying: {lounge}")
        try:
            entity = await asyncio.wait_for(client.get_entity(lounge), timeout=5)
            print(f"  SUCCESS! Found: {entity.title} (ID: {entity.id})")
        except asyncio.TimeoutError:
            print(f"  TIMEOUT - took too long")
        except Exception as e:
            print(f"  FAILED: {e}")
    
    await client.disconnect()

asyncio.run(main())




