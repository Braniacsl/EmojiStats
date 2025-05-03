import discord
from discord import app_commands
import sqlite3
import logging

# Use relative imports within the same package
from cogs.admin import permissions
from config import config
from utils import db_utils
from utils import embed_utils
from utils import ui_components

log = logging.getLogger(__name__)

# Define an admin command group
admin_group = app_commands.Group(name="admin", description="Administrative commands for the bot.")

@admin_group.command(name="wipe_data", description=config.COMMAND_DESCRIPTIONS.get("wipe_data", "[Admin] Wipe all tracked data."))
@permissions.is_emoji_police() # Apply permission check
async def wipe_data(interaction: discord.Interaction):
    """Permanently deletes all tracked emoji, reaction, and sticker data for the server."""
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return

    # Confirmation required
    confirm_emoji = config.EMOJI_MAP.get("confirm", "✅")
    cancel_emoji = config.EMOJI_MAP.get("cancel", "❌")
    warning_emoji = config.EMOJI_MAP.get("warning", "⚠️")
    wipe_emoji = config.EMOJI_MAP.get("wipe_data", "💥")

    view = ui_components.ConfirmationView(author=interaction.user)
    embed = discord.Embed(
        title=f"{warning_emoji} Confirm Data Wipe",
        description=(
            f"This action is **IRREVERSIBLE** and will permanently delete **ALL** tracked data for this server ({interaction.guild.name}):\n"
            f"- Emoji usage counts\n"
            f"- Reaction usage counts\n"
            f"- Sticker usage counts\n\n"
            f"Click `{confirm_emoji} Confirm` to proceed or `{cancel_emoji} Cancel` to abort."
        ),
        color=discord.Color.orange()
    )

    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    # Wait for the view to finish (user confirms or cancels, or timeout)
    await view.wait()

    if view.value is True: # User confirmed
        # Get DB connection from bot instance if possible, or create new one
        # This assumes db_conn is accessible; might need adjustment based on main bot structure
        db_conn = None
        if hasattr(interaction.client, 'db_conn'):
            db_conn = interaction.client.db_conn
        else:
            # Fallback: create a temporary connection (less ideal)
            log.warning("Could not access bot.db_conn, creating temporary connection for wipe_data.")
            try:
                db_conn = db_utils.get_db_connection(config.DATABASE_NAME)
            except Exception as e:
                log.error(f"Failed to get DB connection for wipe_data: {e}")
                await interaction.followup.send(embed=embed_utils.create_error_embed("Database connection error."), ephemeral=True)
                return

        if not db_conn:
             await interaction.followup.send(embed=embed_utils.create_error_embed("Database connection unavailable."), ephemeral=True)
             return

        guild_id = str(interaction.guild.id)
        success = db_utils.wipe_guild_data(db_conn, guild_id)

        # Close temporary connection if created
        if not hasattr(interaction.client, 'db_conn') and db_conn:
            db_utils.close_db_connection(db_conn)

        if success:
            log.info(f"Data wiped for guild {guild_id} by {interaction.user}")
            await interaction.followup.send(embed=embed_utils.create_success_embed(f"{wipe_emoji} All tracked data for this server has been permanently deleted."), ephemeral=True)
        else:
            log.error(f"Failed to wipe data for guild {guild_id}")
            await interaction.followup.send(embed=embed_utils.create_error_embed("An error occurred while trying to wipe the data."), ephemeral=True)

    elif view.value is False: # User cancelled
        await interaction.followup.send(embed=embed_utils.create_info_embed("Data wipe operation cancelled."), ephemeral=True)
    else: # Timeout
        await interaction.followup.send(embed=embed_utils.create_info_embed("Data wipe confirmation timed out."), ephemeral=True)

@admin_group.command(name="reset_data", description=config.COMMAND_DESCRIPTIONS.get("reset_data", "[Admin] Reset all counts to zero."))
@permissions.is_emoji_police() # Apply permission check
async def reset_data(interaction: discord.Interaction):
    """Resets all tracked counts to zero but keeps the tracked items (emojis, reactions, stickers)."""
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return

    # Confirmation required
    confirm_emoji = config.EMOJI_MAP.get("confirm", "✅")
    cancel_emoji = config.EMOJI_MAP.get("cancel", "❌")
    warning_emoji = config.EMOJI_MAP.get("warning", "⚠️")
    reset_emoji = config.EMOJI_MAP.get("reset_data", "♻️")

    view = ui_components.ConfirmationView(author=interaction.user)
    embed = discord.Embed(
        title=f"{warning_emoji} Confirm Data Reset",
        description=(
            f"This action will reset **ALL** usage counts to **ZERO** for this server ({interaction.guild.name}):\n"
            f"- Emoji counts\n"
            f"- Reaction counts\n"
            f"- Sticker counts\n\n"
            f"Tracked items will remain, but their counts will be 0.\n"
            f"Click `{confirm_emoji} Confirm` to proceed or `{cancel_emoji} Cancel` to abort."
        ),
        color=discord.Color.orange()
    )

    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    # Wait for the view to finish
    await view.wait()

    if view.value is True: # User confirmed
        # Get DB connection (similar logic as wipe_data)
        db_conn = None
        if hasattr(interaction.client, 'db_conn'):
            db_conn = interaction.client.db_conn
        else:
            log.warning("Could not access bot.db_conn, creating temporary connection for reset_data.")
            try:
                db_conn = db_utils.get_db_connection(config.DATABASE_NAME)
            except Exception as e:
                log.error(f"Failed to get DB connection for reset_data: {e}")
                await interaction.followup.send(embed=embed_utils.create_error_embed("Database connection error."), ephemeral=True)
                return

        if not db_conn:
             await interaction.followup.send(embed=embed_utils.create_error_embed("Database connection unavailable."), ephemeral=True)
             return

        guild_id = str(interaction.guild.id)
        success = db_utils.reset_guild_counts(db_conn, guild_id)

        # Close temporary connection if created
        if not hasattr(interaction.client, 'db_conn') and db_conn:
            db_utils.close_db_connection(db_conn)

        if success:
            log.info(f"Data counts reset for guild {guild_id} by {interaction.user}")
            await interaction.followup.send(embed=embed_utils.create_success_embed(f"{reset_emoji} All tracked counts for this server have been reset to zero."), ephemeral=True)
        else:
            log.error(f"Failed to reset counts for guild {guild_id}")
            await interaction.followup.send(embed=embed_utils.create_error_embed("An error occurred while trying to reset the data counts."), ephemeral=True)

    elif view.value is False: # User cancelled
        await interaction.followup.send(embed=embed_utils.create_info_embed("Data reset operation cancelled."), ephemeral=True)
    else: # Timeout
        await interaction.followup.send(embed=embed_utils.create_info_embed("Data reset confirmation timed out."), ephemeral=True)

# Function to register this group with the bot
async def setup(bot: discord.ext.commands.Bot):
    bot.tree.add_command(admin_group)
    log.info("Admin command group added to bot tree.")

