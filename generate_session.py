"""
Generate a StringSession for Railway deployment.
Run this locally ONCE, then save the output as SESSION_STRING env var.
"""
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
import config

async def main():
    print("=" * 50)
    print("STRING SESSION GENERATOR")
    print("=" * 50)
    
    # Create client with empty StringSession
    client = TelegramClient(StringSession(), config.API_ID, config.API_HASH)
    
    await client.connect()
    
    if not await client.is_user_authorized():
        print(f"\nPhone number: {config.PHONE}")
        await client.send_code_request(config.PHONE)
        code = input("Enter the code you received: ")
        await client.sign_in(config.PHONE, code)
    
    # Get the session string
    session_string = client.session.save()
    
    await client.disconnect()
    
    print("\n" + "=" * 50)
    print("YOUR SESSION STRING (save this!):")
    print("=" * 50)
    print(session_string)
    print("=" * 50)
    print("\nAdd this as SESSION_STRING environment variable in Railway")

if __name__ == '__main__':
    asyncio.run(main())
