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

# Define an emoji command group
emoji_group = app_commands.Group(name="emoji", description="Commands related to emoji tracking.")

@emoji_group.command(name="top", description=config.COMMAND_DESCRIPTIONS.get("emoji_top", "Show most used emojis."))
@permissions.is_emoji_police() # Apply permission check
@app_commands.describe(limit="How many top emojis to show (1-25, default 10)")
async def emoji_top(interaction: discord.Interaction, limit: app_commands.Range[int, 1, 25] = 10):
    """Displays the top N most used emojis in the server."""
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return

    # Defer response as DB query might take time
    await interaction.response.defer(ephemeral=True)

    db_conn = None
    if hasattr(interaction.client, "db_conn"):
        db_conn = interaction.client.db_conn
    else:
        log.warning("Could not access bot.db_conn, creating temporary connection for emoji_top.")
        try:
            db_conn = db_utils.get_db_connection(config.DATABASE_NAME)
        except Exception as e:
            log.error(f"Failed to get DB connection for emoji_top: {e}")
            await interaction.followup.send(embed=embed_utils.create_error_embed("Database connection error."), ephemeral=True)
            return

    if not db_conn:
         await interaction.followup.send(embed=embed_utils.create_error_embed("Database connection unavailable."), ephemeral=True)
         return

    guild_id = str(interaction.guild.id)
    try:
        top_emojis = db_utils.get_top_items(db_conn, guild_id, "emojis", limit=limit)
    except Exception as e:
        log.error(f"Error fetching top emojis for guild {guild_id}: {e}")
        await interaction.followup.send(embed=embed_utils.create_error_embed("Failed to fetch emoji data."), ephemeral=True)
        # Close temporary connection if created
        if not hasattr(interaction.client, "db_conn") and db_conn:
            db_utils.close_db_connection(db_conn)
        return

    # Close temporary connection if created
    if not hasattr(interaction.client, "db_conn") and db_conn:
        db_utils.close_db_connection(db_conn)

    if not top_emojis:
        await interaction.followup.send(embed=embed_utils.create_info_embed("No emoji usage data found yet."), ephemeral=True)
        return

    # Use pagination even for top/rare in case limit is large or for consistency
    title = f"{config.EMOJI_MAP.get('top', '👑')} Top {limit} Emojis in {interaction.guild.name}"
    await embed_utils.paginate_and_send(interaction, title, top_emojis, "emoji")

@emoji_group.command(name="rare", description=config.COMMAND_DESCRIPTIONS.get("emoji_rare", "Show least used emojis."))
@permissions.is_emoji_police() # Apply permission check
@app_commands.describe(limit="How many rare emojis to show (1-25, default 10)")
async def emoji_rare(interaction: discord.Interaction, limit: app_commands.Range[int, 1, 25] = 10):
    """Displays the N least used emojis in the server (must have been used at least once)."""
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    db_conn = None
    if hasattr(interaction.client, "db_conn"):
        db_conn = interaction.client.db_conn
    else:
        log.warning("Could not access bot.db_conn, creating temporary connection for emoji_rare.")
        try:
            db_conn = db_utils.get_db_connection(config.DATABASE_NAME)
        except Exception as e:
            log.error(f"Failed to get DB connection for emoji_rare: {e}")
            await interaction.followup.send(embed=embed_utils.create_error_embed("Database connection error."), ephemeral=True)
            return

    if not db_conn:
         await interaction.followup.send(embed=embed_utils.create_error_embed("Database connection unavailable."), ephemeral=True)
         return

    guild_id = str(interaction.guild.id)
    try:
        rare_emojis = db_utils.get_rare_items(db_conn, guild_id, "emojis", limit=limit)
    except Exception as e:
        log.error(f"Error fetching rare emojis for guild {guild_id}: {e}")
        await interaction.followup.send(embed=embed_utils.create_error_embed("Failed to fetch emoji data."), ephemeral=True)
        # Close temporary connection if created
        if not hasattr(interaction.client, "db_conn") and db_conn:
            db_utils.close_db_connection(db_conn)
        return

    # Close temporary connection if created
    if not hasattr(interaction.client, "db_conn") and db_conn:
        db_utils.close_db_connection(db_conn)

    if not rare_emojis:
        await interaction.followup.send(embed=embed_utils.create_info_embed("No emoji usage data found yet (or none with count > 0).", title="Rare Emojis"), ephemeral=True)
        return

    title = f"{config.EMOJI_MAP.get('rare', '💀')} Rarest {limit} Emojis in {interaction.guild.name}"
    await embed_utils.paginate_and_send(interaction, title, rare_emojis, "emoji")

@emoji_group.command(name="history", description=config.COMMAND_DESCRIPTIONS.get("emoji_history", "View full emoji usage history."))
@permissions.is_emoji_police() # Apply permission check
async def emoji_history(interaction: discord.Interaction):
    """Displays the full history of emoji usage, paginated."""
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    db_conn = None
    if hasattr(interaction.client, "db_conn"):
        db_conn = interaction.client.db_conn
    else:
        log.warning("Could not access bot.db_conn, creating temporary connection for emoji_history.")
        try:
            db_conn = db_utils.get_db_connection(config.DATABASE_NAME)
        except Exception as e:
            log.error(f"Failed to get DB connection for emoji_history: {e}")
            await interaction.followup.send(embed=embed_utils.create_error_embed("Database connection error."), ephemeral=True)
            return

    if not db_conn:
         await interaction.followup.send(embed=embed_utils.create_error_embed("Database connection unavailable."), ephemeral=True)
         return

    guild_id = str(interaction.guild.id)
    try:
        # Fetch all items, ordered by count descending by default in get_all_items
        all_emojis = db_utils.get_all_items(db_conn, guild_id, "emojis")
    except Exception as e:
        log.error(f"Error fetching emoji history for guild {guild_id}: {e}")
        await interaction.followup.send(embed=embed_utils.create_error_embed("Failed to fetch emoji data."), ephemeral=True)
        # Close temporary connection if created
        if not hasattr(interaction.client, "db_conn") and db_conn:
            db_utils.close_db_connection(db_conn)
        return

    # Close temporary connection if created
    if not hasattr(interaction.client, "db_conn") and db_conn:
        db_utils.close_db_connection(db_conn)

    if not all_emojis:
        await interaction.followup.send(embed=embed_utils.create_info_embed("No emoji usage data found yet.", title="Emoji History"), ephemeral=True)
        return

    title = f"{config.EMOJI_MAP.get('history', '📜')} Emoji Usage History in {interaction.guild.name}"
    await embed_utils.paginate_and_send(interaction, title, all_emojis, "emoji")

# Function to register this group with the bot
async def setup(bot: discord.ext.commands.Bot):
    bot.tree.add_command(emoji_group)
    log.info("Emoji command group added to bot tree.")

