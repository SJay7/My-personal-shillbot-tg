"""Test lounges with real posts (text only, no spam - just first msg truncated)"""
import asyncio
from telethon import TelegramClient
from telethon.errors import FloodWaitError, ChatWriteForbiddenError, UserBannedInChannelError

API_ID = 35483512
API_HASH = "cc591ecf72dde80d403391b191c5a9c4"

# Test message - short and harmless
TEST_MSG = "👋"

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
    """Actually try to send a message. Returns (success, name, error)"""
    name = str(lounge)
    try:
        entity = await asyncio.wait_for(client.get_entity(lounge), timeout=8)
        name = getattr(entity, 'title', str(lounge))[:40]
        
        # Try to send
        msg = await asyncio.wait_for(
            client.send_message(entity, TEST_MSG),
            timeout=15
        )
        
        # Delete immediately
        try:
            await client.delete_messages(entity, msg)
        except:
            pass  # If delete fails, no big deal
        
        return True, name, None
        
    except asyncio.TimeoutError:
        return False, name, "Timeout"
    except ChatWriteForbiddenError:
        return False, name, "Write forbidden"
    except UserBannedInChannelError:
        return False, name, "Banned"
    except FloodWaitError as e:
        return False, name, f"Flood wait {e.seconds}s"
    except Exception as e:
        err = str(e)[:25]
        return False, name, err

async def main():
    client = TelegramClient('shill_session', API_ID, API_HASH)
    await client.connect()
    
    if not await client.is_user_authorized():
        print("Not logged in!")
        return
    
    me = await client.get_me()
    print(f"Logged in as: {me.first_name}\n")
    
    lounges = load_lounges()
    print(f"Testing {len(lounges)} lounges with real posts...")
    print("(Sending 👋 and immediately deleting)\n")
    
    good = []
    bad = []
    
    for i, lounge in enumerate(lounges):
        success, name, error = await test_lounge(client, lounge)
        
        if success:
            print(f"  [{i+1:3}/{len(lounges)}] ✓ {name}")
            good.append((lounge, name))
        else:
            print(f"  [{i+1:3}/{len(lounges)}] ✗ {name} - {error}")
            bad.append((lounge, name, error))
        
        # 3 sec delay to avoid flood
        await asyncio.sleep(3)
    
    print("\n" + "="*50)
    print(f"WORKING: {len(good)} | FAILED: {len(bad)}")
    print("="*50)
    
    # Save good ones
    with open('lounges_working.txt', 'w') as f:
        f.write("# Tested working lounges\n\n")
        for lid, name in good:
            f.write(f"{lid}  # {name}\n")
    
    print(f"\n✓ Saved {len(good)} working lounges to 'lounges_working.txt'")
    print("\nTo use: copy lounges_working.txt lounges.txt")
    
    await client.disconnect()

asyncio.run(main())




