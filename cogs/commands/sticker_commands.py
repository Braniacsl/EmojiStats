import discord
from discord import app_commands
import sqlite3
import logging
# Import from project
from config import config
from utils import db_utils
from utils import embed_utils
from cogs.admin import permissions # Import permissions check

log = logging.getLogger(__name__)

# Define a sticker command group
sticker_group = app_commands.Group(name="sticker", description="Commands related to sticker tracking.")

@sticker_group.command(name="top", description=config.COMMAND_DESCRIPTIONS.get("sticker_top", "Show most used stickers."))
@permissions.is_emoji_police() # Apply permission check
@app_commands.describe(limit="How many top stickers to show (1-25, default 10)")
async def sticker_top(interaction: discord.Interaction, limit: app_commands.Range[int, 1, 25] = 10):
    """Displays the top N most used stickers in the server."""
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    db_conn = None
    if hasattr(interaction.client, "db_conn"):
        db_conn = interaction.client.db_conn
    else:
        log.warning("Could not access bot.db_conn, creating temporary connection for sticker_top.")
        try:
            db_conn = db_utils.get_db_connection(config.DATABASE_NAME)
        except Exception as e:
            log.error(f"Failed to get DB connection for sticker_top: {e}")
            await interaction.followup.send(embed=embed_utils.create_error_embed("Database connection error."), ephemeral=True)
            return

    if not db_conn:
         await interaction.followup.send(embed=embed_utils.create_error_embed("Database connection unavailable."), ephemeral=True)
         return

    guild_id = str(interaction.guild.id)
    try:
        top_stickers = db_utils.get_top_items(db_conn, guild_id, "stickers", limit=limit)
    except Exception as e:
        log.error(f"Error fetching top stickers for guild {guild_id}: {e}")
        await interaction.followup.send(embed=embed_utils.create_error_embed("Failed to fetch sticker data."), ephemeral=True)
        # Close temporary connection if created
        if not hasattr(interaction.client, "db_conn") and db_conn:
            db_utils.close_db_connection(db_conn)
        return

    # Close temporary connection if created
    if not hasattr(interaction.client, "db_conn") and db_conn:
        db_utils.close_db_connection(db_conn)

    if not top_stickers:
        await interaction.followup.send(embed=embed_utils.create_info_embed("No sticker usage data found yet."), ephemeral=True)
        return

    title = f"{config.EMOJI_MAP.get('sticker_section', '🧩')} Top {limit} Stickers in {interaction.guild.name}"
    # Note: embed_utils expects name and count. get_items for stickers returns name, sticker_id, count.
    # We need to adjust how data is passed or how embed_utils handles it if sticker_id is needed.
    # For now, assuming embed_utils only uses name and count.
    await embed_utils.paginate_and_send(interaction, title, top_stickers, "sticker")

@sticker_group.command(name="rare", description=config.COMMAND_DESCRIPTIONS.get("sticker_rare", "Show least used stickers."))
@permissions.is_emoji_police() # Apply permission check
@app_commands.describe(limit="How many rare stickers to show (1-25, default 10)")
async def sticker_rare(interaction: discord.Interaction, limit: app_commands.Range[int, 1, 25] = 10):
    """Displays the N least used stickers in the server (must have been used at least once)."""
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    db_conn = None
    if hasattr(interaction.client, "db_conn"):
        db_conn = interaction.client.db_conn
    else:
        log.warning("Could not access bot.db_conn, creating temporary connection for sticker_rare.")
        try:
            db_conn = db_utils.get_db_connection(config.DATABASE_NAME)
        except Exception as e:
            log.error(f"Failed to get DB connection for sticker_rare: {e}")
            await interaction.followup.send(embed=embed_utils.create_error_embed("Database connection error."), ephemeral=True)
            return

    if not db_conn:
         await interaction.followup.send(embed=embed_utils.create_error_embed("Database connection unavailable."), ephemeral=True)
         return

    guild_id = str(interaction.guild.id)
    try:
        rare_stickers = db_utils.get_rare_items(db_conn, guild_id, "stickers", limit=limit)
    except Exception as e:
        log.error(f"Error fetching rare stickers for guild {guild_id}: {e}")
        await interaction.followup.send(embed=embed_utils.create_error_embed("Failed to fetch sticker data."), ephemeral=True)
        # Close temporary connection if created
        if not hasattr(interaction.client, "db_conn") and db_conn:
            db_utils.close_db_connection(db_conn)
        return

    # Close temporary connection if created
    if not hasattr(interaction.client, "db_conn") and db_conn:
        db_utils.close_db_connection(db_conn)

    if not rare_stickers:
        await interaction.followup.send(embed=embed_utils.create_info_embed("No sticker usage data found yet (or none with count > 0).", title="Rare Stickers"), ephemeral=True)
        return

    title = f"{config.EMOJI_MAP.get('rare', '💀')} Rarest {limit} Stickers in {interaction.guild.name}"
    await embed_utils.paginate_and_send(interaction, title, rare_stickers, "sticker")

@sticker_group.command(name="history", description=config.COMMAND_DESCRIPTIONS.get("sticker_history", "View full sticker usage history."))
@permissions.is_emoji_police() # Apply permission check
async def sticker_history(interaction: discord.Interaction):
    """Displays the full history of sticker usage, paginated."""
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    db_conn = None
    if hasattr(interaction.client, "db_conn"):
        db_conn = interaction.client.db_conn
    else:
        log.warning("Could not access bot.db_conn, creating temporary connection for sticker_history.")
        try:
            db_conn = db_utils.get_db_connection(config.DATABASE_NAME)
        except Exception as e:
            log.error(f"Failed to get DB connection for sticker_history: {e}")
            await interaction.followup.send(embed=embed_utils.create_error_embed("Database connection error."), ephemeral=True)
            return

    if not db_conn:
         await interaction.followup.send(embed=embed_utils.create_error_embed("Database connection unavailable."), ephemeral=True)
         return

    guild_id = str(interaction.guild.id)
    try:
        # Fetch all items, ordered by count descending
        all_stickers = db_utils.get_all_items(db_conn, guild_id, "stickers")
    except Exception as e:
        log.error(f"Error fetching sticker history for guild {guild_id}: {e}")
        await interaction.followup.send(embed=embed_utils.create_error_embed("Failed to fetch sticker data."), ephemeral=True)
        # Close temporary connection if created
        if not hasattr(interaction.client, "db_conn") and db_conn:
            db_utils.close_db_connection(db_conn)
        return

    # Close temporary connection if created
    if not hasattr(interaction.client, "db_conn") and db_conn:
        db_utils.close_db_connection(db_conn)

    if not all_stickers:
        await interaction.followup.send(embed=embed_utils.create_info_embed("No sticker usage data found yet.", title="Sticker History"), ephemeral=True)
        return

    title = f"{config.EMOJI_MAP.get('history', '📜')} Sticker Usage History in {interaction.guild.name}"
    await embed_utils.paginate_and_send(interaction, title, all_stickers, "sticker")

# Function to register this group with the bot
async def setup(bot: discord.ext.commands.Bot):
    bot.tree.add_command(sticker_group)
    log.info("Sticker command group added to bot tree.")

