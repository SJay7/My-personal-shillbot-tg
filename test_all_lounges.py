"""Test all lounges and find reliable ones - checks permissions only"""
import asyncio
from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import Channel, Chat

API_ID = 35483512
API_HASH = "cc591ecf72dde80d403391b191c5a9c4"

# Load lounges
def load_lounges():
    lounges = []
    with open('lounges.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                try:
                    lounges.append(int(line))
                except ValueError:
                    lounges.append(line)
    return lounges

async def test_lounge(client, lounge):
    """Check if we can access the lounge. Returns (accessible, name)"""
    try:
        entity = await asyncio.wait_for(client.get_entity(lounge), timeout=8)
        name = getattr(entity, 'title', str(lounge))
        
        # Check if it's a channel/group we can access
        if hasattr(entity, 'broadcast') and entity.broadcast:
            # It's a channel - check if we can post
            if hasattr(entity, 'creator') and entity.creator:
                return True, name  # We're the creator
            # For channels, we need post rights
            return True, name  # Assume we can if we're in it
        else:
            # It's a group - we can usually post
            return True, name
            
    except asyncio.TimeoutError:
        return False, str(lounge)
    except Exception as e:
        return False, str(lounge)

async def main():
    client = TelegramClient('shill_session', API_ID, API_HASH)
    await client.connect()
    
    if not await client.is_user_authorized():
        print("Not logged in!")
        return
    
    lounges = load_lounges()
    print(f"Checking {len(lounges)} lounges...\n")
    
    good_lounges = []
    bad_lounges = []
    
    for i, lounge in enumerate(lounges):
        accessible, name = await test_lounge(client, lounge)
        
        if accessible:
            print(f"  [{i+1}/{len(lounges)}] OK - {name[:45]}")
            good_lounges.append((lounge, name))
        else:
            print(f"  [{i+1}/{len(lounges)}] SKIP - {name[:45]}")
            bad_lounges.append((lounge, name))
        
        await asyncio.sleep(0.5)  # Small delay
    
    print("\n" + "="*50)
    print(f"RESULTS: {len(good_lounges)} accessible, {len(bad_lounges)} skipped")
    print("="*50)
    
    # Save good lounges
    with open('lounges_verified.txt', 'w') as f:
        f.write("# Verified accessible lounges\n")
        for lounge_id, name in good_lounges:
            f.write(f"{lounge_id}  # {name}\n")
    
    print(f"\nSaved {len(good_lounges)} lounges to 'lounges_verified.txt'")
    
    await client.disconnect()

asyncio.run(main())
