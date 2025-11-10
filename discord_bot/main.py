import asyncio

import bot.commands  # noqa: F401 - Import to register commands with bot
from bot.bot import bot, start_bot
from config import config
from firestore_client import initialize_firebase


async def main():
    """Run Discord bot standalone"""
    print("🤖 Starting Impostor Discord Bot...")
    
    try:
        config.validate()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        return
    
    initialize_firebase()
    print("✅ Firebase initialized")
    
    while True:
        try:
            await start_bot()
        except KeyboardInterrupt:
            print("\n👋 Shutting down bot...")
            await bot.close()
            break
        except Exception as e:
            print(f"❌ Bot error: {e}")
            print("⚠️ Bot will restart in 10 seconds...")
            await asyncio.sleep(10)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"❌ Fatal error: {e}")

