import discord
import discord.ext.commands as commands
import sqlite3
import re
import logging
# Import from project
from utils import db_utils
from config import config

log = logging.getLogger(__name__)

# Regex to find custom emojis (both static and animated)
# <:name:id> or <a:name:id>
CUSTOM_EMOJI_REGEX = re.compile(r"<a?:([a-zA-Z0-9_]+):([0-9]+)>")

# Function to check if a character is likely a Unicode emoji
def is_unicode_emoji(char):
    # Basic check covering common emoji ranges
    code = ord(char)
    return (
        0x1F300 <= code <= 0x1F5FF or  # Misc Symbols and Pictographs
        0x1F600 <= code <= 0x1F64F or  # Emoticons
        0x1F680 <= code <= 0x1F6FF or  # Transport and Map Symbols
        0x2600 <= code <= 0x26FF or   # Misc Symbols
        0x2700 <= code <= 0x27BF or   # Dingbats
        0xFE00 <= code <= 0xFE0F or   # Variation Selectors
        0x1FA70 <= code <= 0x1FAFF    # Symbols and Pictographs Extended-A
    )

# Define the on_message event listener
async def on_message(message: discord.Message):
    # Ignore messages from the bot itself
    if message.author.bot:
        return

    # Ignore DMs if the bot is guild-focused
    if not message.guild:
        return

    # Ignore messages if content intent is missing (though we requested it)
    if message.content is None:
        return

    # Get DB connection from the bot instance
    bot = message._state._get_client()
    db_conn = getattr(bot, "db_conn", None)
    if not db_conn:
        log.error(f"Database connection not found on bot instance in on_message for guild {message.guild.id}")
        return

    guild_id = str(message.guild.id)

    # --- Track Custom Emojis ---
    custom_emojis_found = CUSTOM_EMOJI_REGEX.findall(message.content)
    for name, emoji_id in custom_emojis_found:
        full_matches = re.finditer(CUSTOM_EMOJI_REGEX, message.content)
        for match in full_matches:
            if match.group(1) == name and match.group(2) == emoji_id:
                full_emoji_str = match.group(0)
                log.debug(f"Found custom emoji: {full_emoji_str} in guild {guild_id}")
                db_utils.update_count(db_conn, guild_id, "emojis", full_emoji_str)
                break  # Process each unique match once per message scan

    # --- Track Unicode Emojis ---
    unicode_emojis_found = set()
    for char in message.content:
        if is_unicode_emoji(char):
            if char not in unicode_emojis_found:
                log.debug(f"Found Unicode emoji: {char} in guild {guild_id}")
                db_utils.update_count(db_conn, guild_id, "emojis", char)
                unicode_emojis_found.add(char)  # Count each unique emoji once per message

    # --- Track Stickers ---
    if message.stickers:
        for sticker in message.stickers:
            log.debug(f"Found sticker: {sticker.name} (ID: {sticker.id}) in guild {guild_id}")
            db_utils.update_count(db_conn, guild_id, "stickers", sticker.name, item_id=sticker.id)

    # Allow other event listeners (like commands) to process the message
    await bot.process_commands(message)

async def setup(bot: commands.Bot):
    """Registers the on_message event listener."""
    bot.event(on_message)
    log.info("On_message event handler registered.")