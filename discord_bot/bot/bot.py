import asyncio

import discord
from config import config
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"✅ Discord bot logged in as {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")


@bot.event
async def on_disconnect():
    print("⚠️ Discord bot disconnected")


@bot.event
async def on_resumed():
    print("✅ Discord bot resumed connection")


@bot.event
async def on_error(event, *args, **kwargs):
    print(f"❌ Discord bot error in {event}: {args} {kwargs}")


async def start_bot():
    """Start Discord bot with automatic reconnection"""
    max_retries = 5
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            print(f"🤖 Starting Discord bot (attempt {attempt + 1}/{max_retries})...")
            await bot.start(config.DISCORD_TOKEN)
        except discord.errors.ConnectionClosed as e:
            print(f"⚠️ Connection closed: {e}. Reconnecting in {retry_delay}s...")
            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 60)
        except discord.errors.HTTPException as e:
            print(f"❌ HTTP error: {e}. Retrying in {retry_delay}s...")
            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 60)
        except Exception as e:
            print(f"❌ Unexpected error starting bot: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay}s...")
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 60)
            else:
                print("❌ Max retries reached. Bot startup failed.")
                raise

