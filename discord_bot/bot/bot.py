import asyncio

import discord
from config import config
from discord.ext import commands
from loguru import logger

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    logger.success(f"Discord bot logged in as {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        logger.success(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")


@bot.event
async def on_disconnect():
    logger.warning("Discord bot disconnected")


@bot.event
async def on_resumed():
    logger.success("Discord bot resumed connection")


@bot.event
async def on_error(event, *args, **kwargs):
    logger.error(f"Discord bot error in {event}: {args} {kwargs}")


async def start_bot():
    """Start Discord bot with automatic reconnection"""
    max_retries = 5
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            logger.info(f"Starting Discord bot (attempt {attempt + 1}/{max_retries})...")
            await bot.start(config.DISCORD_TOKEN)
        except discord.errors.ConnectionClosed as e:
            logger.warning(f"Connection closed: {e}. Reconnecting in {retry_delay}s...")
            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 60)
        except discord.errors.HTTPException as e:
            logger.error(f"HTTP error: {e}. Retrying in {retry_delay}s...")
            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 60)
        except Exception as e:
            logger.error(f"Unexpected error starting bot: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay}s...")
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 60)
            else:
                logger.error("Max retries reached. Bot startup failed.")
                raise

