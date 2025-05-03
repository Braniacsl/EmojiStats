import discord
from discord.ext import commands
import os
import asyncio
import sqlite3
import logging
import atexit
from dotenv import load_dotenv # To load .env file for token
#imports from this project
from config import config
from cogs.admin import permissions
from utils import db_utils
from utils import embed_utils
from cogs.events import on_message as message_event
from cogs.events import on_reaction as reaction_event
from cogs.admin import data_tools as admin_data_tools
from cogs.commands import emoji_commands as emoji
from cogs.commands import help
from cogs.commands import reaction_commands as reaction
from cogs.commands import sticker_commands as sticker

# --- Configure Logging ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(name)s: %(message)s")
log = logging.getLogger(__name__)

# --- Load Environment Variables (for TOKEN) ---
# Create a .env file in the same directory as this script
# with the line: DISCORD_BOT_TOKEN=\"YOUR_BOT_TOKEN_HERE\"
load_dotenv()
BOT_TOKEN = os.getenv("DISCORD_TOKEN")

if not BOT_TOKEN:
    log.critical("DISCORD_BOT_TOKEN not found in environment variables or .env file. Please set it.")
    exit(1)

# --- Bot Intents Setup ---
intents = config.intents

# --- Bot Instance Setup ---
bot = commands.Bot(command_prefix=config.BOT_PREFIX, intents=intents)
bot.db_conn = None # Initialize db_conn attribute

# --- Database Connection ---
def setup_database():
    """Sets up the database connection and attaches it to the bot."""
    try:
        bot.db_conn = db_utils.get_db_connection(config.DATABASE_NAME)
        atexit.register(db_utils.close_db_connection, bot.db_conn)
        log.info("Database connection established and cleanup registered.")
    except Exception as e:
        log.critical(f"Failed to establish initial database connection: {e}")
        # Exit if DB is critical for startup
        exit(1)

# --- Event: on_ready (Production Mode) ---
@bot.event
async def on_ready():
    """Called when the bot is ready and connected to Discord."""
    log.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    log.info("Setting up database...")
    setup_database() # Ensure DB is ready

    log.info("Ensuring tables for all connected guilds...")
    guild_setup_emoji = config.EMOJI_MAP.get("guild_setup", "🛡️")
    success_count = 0
    fail_count = 0
    if bot.db_conn:
        for guild in bot.guilds:
            log.info(f"Ensuring tables for guild: {guild.name} (ID: {guild.id})")
            try:
                success = db_utils.ensure_guild_tables(bot.db_conn, str(guild.id))
                if success:
                    log.info(f"{guild_setup_emoji} Successfully ensured tables for guild {guild.name}")
                    success_count += 1
                else:
                    log.error(f"❌ Failed to ensure tables for guild {guild.name}")
                    fail_count += 1
            except Exception as e:
                log.error(f"❌ Exception during table setup for guild {guild.name}: {e}")
                fail_count += 1
        log.info(f"--- Guild Table Setup Complete ({success_count} success, {fail_count} failed) ---")
    else:
        log.error("Cannot ensure guild tables: Database connection is not available.")

    log.info("Registering commands and event handlers...")
    try:
        # Setup event handlers (pass bot instance)
        # message_event.setup(bot)
        # reaction_event.setup(bot)

        # Register Slash Commands (pass bot instance)
        # await admin_data_tools.setup(bot)
        # await help.setup(bot)
        # await emoji.setup(bot)
        # await reaction.setup(bot)
        # await sticker.setup(bot)

        log.info("Command and event handler registration complete.")
        log.info("Use the `!sync` command (admin only) to sync slash commands if needed.")
        
        response = await bot.tree.sync()

        if not response:
            raise Exception("Failed to sync commands with bot.")
        else:
            log.info("Successfully synced commands.")

    except Exception as e:
        log.critical(f"Error during setup of commands/events: {e}", exc_info=True)

    log.info("Bot is ready and online!")

# --- Manual Sync Command (Admin Only - Production Mode) ---
@bot.command(name="sync", hidden=True)
@permissions.is_admin_sync() # Restrict to users with Administrator permission
async def sync(ctx: commands.Context, guild_id: int = None):
    log.info("in")
    """Manually syncs slash commands (Admin Only)."""
    sync_emoji = config.EMOJI_MAP.get("sync", "🔄")
    error_emoji = config.EMOJI_MAP.get("error", "❌")
    success_emoji = config.EMOJI_MAP.get("success", "✔️")

    await ctx.message.add_reaction(sync_emoji) # Indicate processing

    if guild_id:
        guild = discord.Object(id=guild_id)
        try:
            log.info(f"Copying global commands to guild {guild_id}...")
            bot.tree.copy_global_to(guild=guild)
            log.info(f"Syncing commands to guild {guild_id}...")
            synced = await bot.tree.sync(guild=guild)
            log.info(f"Synced {len(synced)} commands to guild {guild_id}.")
            await ctx.send(f"{success_emoji} Synced {len(synced)} commands to guild **{guild_id}**.")
        except Exception as e:
            log.error(f"Failed to sync to guild {guild_id}: {e}")
            await ctx.send(f"{error_emoji} Failed to sync to guild {guild_id}: {e}")
    else:
        try:
            log.info("Syncing global commands...")
            synced = await bot.tree.sync()
            log.info(f"Synced {len(synced)} commands globally.")
            await ctx.send(f"{success_emoji} Synced {len(synced)} commands globally. (May take up to an hour for changes to appear everywhere)")
        except Exception as e:
            log.error(f"Failed to sync globally: {e}")
            await ctx.send(f"{error_emoji} Failed to sync globally: {e}")

    try:
        await ctx.message.remove_reaction(sync_emoji, bot.user)
    except discord.errors.NotFound:
        pass # Ignore if reaction already removed

@sync.error
async def sync_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send(f"❌ {error}")
    else:
        log.error(f"Error in sync command: {error}")
        await ctx.send(f"❌ An error occurred during sync command: {error}")

# --- Global Error Handler for App Commands ---
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    """Handles errors globally for application commands."""
    log.error(f"App Command Error: {error} (Command: {interaction.command.name if interaction.command else 'Unknown'})", exc_info=True)

    error_message = "An unexpected error occurred. Please try again later."
    if isinstance(error, discord.app_commands.CommandNotFound):
        error_message = "Sorry, I don't recognize that command."
    elif isinstance(error, discord.app_commands.CheckFailure):
        # Use the error message directly if available, otherwise provide a generic one
        error_message = str(error) if str(error) else "You don't have the necessary permissions to use this command."
    elif isinstance(error, discord.app_commands.CommandOnCooldown):
        error_message = f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds."
    elif isinstance(error, discord.app_commands.MissingPermissions):
        error_message = f"You are missing the following permissions to run this command: {', '.join(error.missing_permissions)}"
    elif isinstance(error, discord.app_commands.BotMissingPermissions):
        error_message = f"I need the following permissions to run this command: {', '.join(error.missing_permissions)}"
    # Add more specific error handling as needed

    embed = embed_utils.create_error_embed(error_message)
    try:
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)
    except discord.errors.InteractionResponded:
        try:
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
             log.error(f"Failed to send error message via followup after InteractionResponded: {e}")
    except Exception as e:
        log.error(f"Failed to send error message to interaction: {e}")

# --- Event: On Guild Join ---
@bot.event
async def on_guild_join(guild: discord.Guild):
    """Sets up the necessary database tables when the bot joins a new guild."""
    log.info(f"Joined new guild: {guild.name} (ID: {guild.id})")
    if not bot.db_conn:
        log.error(f"Cannot set up tables for guild {guild.id}: Database connection is not available.")
        return

    log.info(f"Ensuring database tables for new guild {guild.name}...")
    try:
        success = db_utils.ensure_guild_tables(bot.db_conn, str(guild.id))
        if success:
            log.info(f"Successfully ensured tables for guild {guild.name}.")
            # Optional: Send welcome message
            # Find a suitable channel (system channel or first text channel)
            target_channel = guild.system_channel
            if not target_channel and guild.text_channels:
                target_channel = guild.text_channels[0]
            if target_channel:
                try:
                    await target_channel.send("Hello! I'm ready to start tracking emoji stats. Use `/help` to see my commands.")
                except discord.errors.Forbidden:
                    log.warning(f"Missing permissions to send welcome message in {guild.name}.")
        else:
            log.error(f"Failed to ensure tables for guild {guild.name}.")
    except Exception as e:
        log.error(f"Exception during table setup for new guild {guild.name}: {e}")

async def register_commands():
    log.info("Loading commands...")
    try:
        # Load extensions (commands and events)
        await bot.load_extension("cogs.events.on_message")
        await bot.load_extension("cogs.events.on_reaction")
        await bot.load_extension("cogs.admin.data_tools")
        await bot.load_extension("cogs.commands.help")
        await bot.load_extension("cogs.commands.emoji_commands")
        await bot.load_extension("cogs.commands.reaction_commands")
        await bot.load_extension("cogs.commands.sticker_commands")
        log.info("All commands loaded successfully.")
    except Exception as e:
        log.critical(f"Error during loading of commands: {e}", exc_info=True)



# --- Main Execution Guard (Production Mode) ---
if __name__ == "__main__":
    log.info("Starting bot in PRODUCTION MODE...")
    try:
        asyncio.run(register_commands())
        bot.run(BOT_TOKEN)
    except discord.errors.LoginFailure:
        log.critical("Failed to log in: Invalid Discord Bot Token provided.")
    except Exception as e:
        log.critical(f"An unexpected error occurred while running the bot: {e}", exc_info=True)
    finally:
        # Ensure DB connection is closed on exit
        if bot.db_conn:
            db_utils.close_db_connection(bot.db_conn)
            log.info("Database connection closed during shutdown.")

