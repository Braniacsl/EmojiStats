import discord
import discord.ext.commands as commands
import sqlite3
import logging
# Import from project
from utils import db_utils
from config import config

log = logging.getLogger(__name__)

# Define the on_reaction_add event listener
async def on_reaction_add(reaction: discord.Reaction, user: discord.User | discord.Member):
    log.info("in reaction")
    # Ignore reactions added by the bot itself
    if user == reaction.message.author or user.bot:
        return

    # Ignore reactions in DMs if the bot is guild-focused
    if not reaction.message.guild:
        return

    # Get DB connection from the bot instance
    bot = reaction.message._state._get_client()  # Access the bot instance from the message
    db_conn = getattr(bot, "db_conn", None)
    if not db_conn:
        log.error(f"Database connection not found on bot instance in on_reaction_add for guild {reaction.message.guild.id}")
        return

    guild_id = str(reaction.message.guild.id)

    # Determine the emoji identifier
    emoji_identifier = None
    if isinstance(reaction.emoji, discord.Emoji):  # Custom emoji
        # Format as <:name:id> or <a:name:id>
        emoji_identifier = f"<{'a' if reaction.emoji.animated else ''}:{reaction.emoji.name}:{reaction.emoji.id}>"
    elif isinstance(reaction.emoji, str):  # Unicode emoji
        emoji_identifier = reaction.emoji
    else:  # PartialEmoji or other types might occur, handle if necessary
        log.warning(f"Unsupported reaction type encountered: {type(reaction.emoji)} in guild {guild_id}")
        return

    if emoji_identifier:
        log.debug(f"Found reaction: {emoji_identifier} added by {user} in guild {guild_id}")
        # Update the count in the reactions table
        db_utils.update_count(db_conn, guild_id, "reactions", emoji_identifier)
    else:
        log.error("no emoji identifier")

async def setup(bot: commands.Bot):
    """Registers the on_message event listener."""
    bot.event(on_reaction_add)
    log.info("On_message event handler registered.")
