import asyncio
import sys

import bot.commands  # noqa: F401 - Import to register commands with bot
from bot.bot import bot, start_bot
from config import config
from firestore_client import initialize_firebase
from firestore_listener import FirestoreListener
from loguru import logger

# Configure loguru
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO",
)


async def main():
    """Run Discord bot standalone"""
    logger.info("🤖 Starting Impostor Discord Bot...")

    try:
        config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return

    initialize_firebase()
    logger.success("Firebase initialized")

    # Initialize Firestore listener
    listener = FirestoreListener(bot, config.WEB_URL)
    bot.firestore_listener = listener  # Attach to bot for access in commands
    logger.success("Firestore listener initialized")

    while True:
        try:
            await start_bot()
        except KeyboardInterrupt:
            logger.info("Shutting down bot...")
            listener.cleanup()  # Clean up listeners
            await bot.close()
            break
        except Exception as e:
            logger.error(f"Bot error: {e}")
            logger.warning("Bot will restart in 10 seconds...")
            await asyncio.sleep(10)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
