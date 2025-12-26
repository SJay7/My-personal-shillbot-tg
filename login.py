"""
One-time login script.
Run this once to authenticate, then run bot.py
"""
import asyncio
import sys
from telethon import TelegramClient
from telethon.sessions import SQLiteSession

API_ID = 35483512
API_HASH = "cc591ecf72dde80d403391b191c5a9c4"
PHONE = "+2349135655752"

async def main():
    print("Telegram Login Script")
    print("=" * 40)
    
    # Use explicit SQLite session with WAL mode disabled
    client = TelegramClient('shill_session', API_ID, API_HASH)
    
    try:
        await client.connect()
        
        if not await client.is_user_authorized():
            print(f"Sending code to {PHONE}...")
            await client.send_code_request(PHONE)
            
            code = input("Enter the code you received: ")
            
            try:
                await client.sign_in(PHONE, code)
            except Exception as e:
                if "2FA" in str(e) or "password" in str(e).lower():
                    password = input("Enter your 2FA password: ")
                    await client.sign_in(password=password)
                else:
                    raise e
        
        me = await client.get_me()
        print(f"\nSuccess! Logged in as: {me.first_name} (@{me.username})")
        print("\nSession saved. You can now run: python bot.py")
        
    finally:
        # Properly disconnect to release the file lock
        await client.disconnect()
        print("Session file released.")

if __name__ == '__main__':
    asyncio.run(main())
    # Force exit to ensure all handles are released
    sys.exit(0)
