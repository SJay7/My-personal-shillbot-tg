"""
Script to get all groups from a Telegram folder
"""
import asyncio
from telethon import TelegramClient
from telethon.tl.functions.messages import GetDialogFiltersRequest
import config

async def main():
    client = TelegramClient(config.SESSION_NAME, config.API_ID, config.API_HASH)
    
    await client.connect()
    
    if not await client.is_user_authorized():
        print("ERROR: Not logged in. Run 'python login.py' first!")
        await client.disconnect()
        return
    
    print("Connected! Fetching your Telegram folders...\n")
    
    # Get all dialog filters (folders)
    result = await client(GetDialogFiltersRequest())
    
    print("=" * 50)
    print("YOUR TELEGRAM FOLDERS:")
    print("=" * 50)
    
    target_folder = None
    
    for folder in result.filters:
        # Skip default/all chats
        if hasattr(folder, 'title'):
            # Handle both string and TextWithEntities
            title = folder.title
            if hasattr(title, 'text'):
                title = title.text
            title = str(title)
            
            print(f"\n[FOLDER] {title}")
            print(f"   ID: {folder.id}")
            
            # Check if this is the shill groups folder
            if "shill" in title.lower():
                target_folder = folder
                print("   ^^^ THIS LOOKS LIKE YOUR SHILL FOLDER! ^^^")
    
    if target_folder:
        # Get title as string
        folder_title = target_folder.title
        if hasattr(folder_title, 'text'):
            folder_title = folder_title.text
        folder_title = str(folder_title)
        
        print("\n" + "=" * 50)
        print(f"GROUPS IN '{folder_title}' FOLDER:")
        print("=" * 50)
        
        # Get all dialogs
        dialogs = await client.get_dialogs()
        
        # Filter to groups that are in this folder
        # The folder contains include_peers which lists the chats
        if hasattr(target_folder, 'include_peers'):
            included_ids = set()
            for peer in target_folder.include_peers:
                if hasattr(peer, 'channel_id'):
                    included_ids.add(-1000000000000 - peer.channel_id)
                elif hasattr(peer, 'chat_id'):
                    included_ids.add(-peer.chat_id)
            
            count = 0
            for dialog in dialogs:
                if dialog.id in included_ids or dialog.entity.id in included_ids:
                    count += 1
                    name = dialog.name or "Unknown"
                    # Strip emojis for Windows console
                    safe_name = name.encode('ascii', 'ignore').decode('ascii').strip() or "Group"
                    print(f"  {count}. {safe_name}")
                    print(f"     ID: {dialog.id}")
            
            if count == 0:
                # Try alternate method - match by getting peers directly
                print("\nTrying alternate method...")
                for peer in target_folder.include_peers:
                    try:
                        entity = await client.get_entity(peer)
                        name = getattr(entity, 'title', None) or getattr(entity, 'name', 'Unknown')
                        safe_name = name.encode('ascii', 'ignore').decode('ascii').strip() or "Group"
                        count += 1
                        print(f"  {count}. {safe_name}")
                        print(f"     ID: {entity.id}")
                    except Exception as e:
                        print(f"  Could not resolve peer: {e}")
            
            print(f"\nTotal groups in folder: {count}")
    else:
        print("\n[!] Could not find a 'Shill groups' folder.")
        print("Make sure you have a folder with 'shill' in the name.")
    
    await client.disconnect()
    print("\nDone!")

if __name__ == '__main__':
    asyncio.run(main())

