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

# Define a reaction command group
reaction_group = app_commands.Group(name="reaction", description="Commands related to reaction tracking.")

@reaction_group.command(name="top", description=config.COMMAND_DESCRIPTIONS.get("reaction_top", "Show most used reactions."))
@permissions.is_emoji_police() # Apply permission check
@app_commands.describe(limit="How many top reactions to show (1-25, default 10)")
async def reaction_top(interaction: discord.Interaction, limit: app_commands.Range[int, 1, 25] = 10):
    """Displays the top N most used reactions in the server."""
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    db_conn = None
    if hasattr(interaction.client, "db_conn"):
        db_conn = interaction.client.db_conn
    else:
        log.warning("Could not access bot.db_conn, creating temporary connection for reaction_top.")
        try:
            db_conn = db_utils.get_db_connection(config.DATABASE_NAME)
        except Exception as e:
            log.error(f"Failed to get DB connection for reaction_top: {e}")
            await interaction.followup.send(embed=embed_utils.create_error_embed("Database connection error."), ephemeral=True)
            return

    if not db_conn:
         await interaction.followup.send(embed=embed_utils.create_error_embed("Database connection unavailable."), ephemeral=True)
         return

    guild_id = str(interaction.guild.id)
    try:
        top_reactions = db_utils.get_top_items(db_conn, guild_id, "reactions", limit=limit)
    except Exception as e:
        log.error(f"Error fetching top reactions for guild {guild_id}: {e}")
        await interaction.followup.send(embed=embed_utils.create_error_embed("Failed to fetch reaction data."), ephemeral=True)
        # Close temporary connection if created
        if not hasattr(interaction.client, "db_conn") and db_conn:
            db_utils.close_db_connection(db_conn)
        return

    # Close temporary connection if created
    if not hasattr(interaction.client, "db_conn") and db_conn:
        db_utils.close_db_connection(db_conn)

    if not top_reactions:
        await interaction.followup.send(embed=embed_utils.create_info_embed("No reaction usage data found yet."), ephemeral=True)
        return

    title = f"{config.EMOJI_MAP.get('leaderboard', '🏆')} Top {limit} Reactions in {interaction.guild.name}"
    await embed_utils.paginate_and_send(interaction, title, top_reactions, "reaction")

@reaction_group.command(name="rare", description=config.COMMAND_DESCRIPTIONS.get("reaction_rare", "Show least used reactions."))
@permissions.is_emoji_police() # Apply permission check
@app_commands.describe(limit="How many rare reactions to show (1-25, default 10)")
async def reaction_rare(interaction: discord.Interaction, limit: app_commands.Range[int, 1, 25] = 10):
    """Displays the N least used reactions in the server (must have been used at least once)."""
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    db_conn = None
    if hasattr(interaction.client, "db_conn"):
        db_conn = interaction.client.db_conn
    else:
        log.warning("Could not access bot.db_conn, creating temporary connection for reaction_rare.")
        try:
            db_conn = db_utils.get_db_connection(config.DATABASE_NAME)
        except Exception as e:
            log.error(f"Failed to get DB connection for reaction_rare: {e}")
            await interaction.followup.send(embed=embed_utils.create_error_embed("Database connection error."), ephemeral=True)
            return

    if not db_conn:
         await interaction.followup.send(embed=embed_utils.create_error_embed("Database connection unavailable."), ephemeral=True)
         return

    guild_id = str(interaction.guild.id)
    try:
        rare_reactions = db_utils.get_rare_items(db_conn, guild_id, "reactions", limit=limit)
    except Exception as e:
        log.error(f"Error fetching rare reactions for guild {guild_id}: {e}")
        await interaction.followup.send(embed=embed_utils.create_error_embed("Failed to fetch reaction data."), ephemeral=True)
        # Close temporary connection if created
        if not hasattr(interaction.client, "db_conn") and db_conn:
            db_utils.close_db_connection(db_conn)
        return

    # Close temporary connection if created
    if not hasattr(interaction.client, "db_conn") and db_conn:
        db_utils.close_db_connection(db_conn)

    if not rare_reactions:
        await interaction.followup.send(embed=embed_utils.create_info_embed("No reaction usage data found yet (or none with count > 0).", title="Rare Reactions"), ephemeral=True)
        return

    title = f"{config.EMOJI_MAP.get('rare', '💀')} Rarest {limit} Reactions in {interaction.guild.name}"
    await embed_utils.paginate_and_send(interaction, title, rare_reactions, "reaction")

@reaction_group.command(name="history", description=config.COMMAND_DESCRIPTIONS.get("reaction_history", "View full reaction usage history."))
@permissions.is_emoji_police() # Apply permission check
async def reaction_history(interaction: discord.Interaction):
    """Displays the full history of reaction usage, paginated."""
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    db_conn = None
    if hasattr(interaction.client, "db_conn"):
        db_conn = interaction.client.db_conn
    else:
        log.warning("Could not access bot.db_conn, creating temporary connection for reaction_history.")
        try:
            db_conn = db_utils.get_db_connection(config.DATABASE_NAME)
        except Exception as e:
            log.error(f"Failed to get DB connection for reaction_history: {e}")
            await interaction.followup.send(embed=embed_utils.create_error_embed("Database connection error."), ephemeral=True)
            return

    if not db_conn:
         await interaction.followup.send(embed=embed_utils.create_error_embed("Database connection unavailable."), ephemeral=True)
         return

    guild_id = str(interaction.guild.id)
    try:
        # Fetch all items, ordered by count descending
        all_reactions = db_utils.get_all_items(db_conn, guild_id, "reactions")
    except Exception as e:
        log.error(f"Error fetching reaction history for guild {guild_id}: {e}")
        await interaction.followup.send(embed=embed_utils.create_error_embed("Failed to fetch reaction data."), ephemeral=True)
        # Close temporary connection if created
        if not hasattr(interaction.client, "db_conn") and db_conn:
            db_utils.close_db_connection(db_conn)
        return

    # Close temporary connection if created
    if not hasattr(interaction.client, "db_conn") and db_conn:
        db_utils.close_db_connection(db_conn)

    if not all_reactions:
        await interaction.followup.send(embed=embed_utils.create_info_embed("No reaction usage data found yet.", title="Reaction History"), ephemeral=True)
        return

    title = f"{config.EMOJI_MAP.get('history', '📜')} Reaction Usage History in {interaction.guild.name}"
    await embed_utils.paginate_and_send(interaction, title, all_reactions, "reaction")

# Function to register this group with the bot
async def setup(bot: discord.ext.commands.Bot):
    bot.tree.add_command(reaction_group)
    log.info("Reaction command group added to bot tree.")

