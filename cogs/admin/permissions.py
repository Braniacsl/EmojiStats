import discord
from discord.ext import commands # Import commands for check decorator
from functools import wraps
import logging
import config.config as config

log = logging.getLogger(__name__)

# Role names from config
ADMIN_ROLE_NAME = config.ADMIN_ROLE_NAME
EMOJI_POLICE_ROLE_NAME = config.EMOJI_POLICE_ROLE_NAME

# --- App Command Permission Check (for slash commands) ---
def is_emoji_police():
    """Decorator for app_commands to check if the user has Admin or EmojiPolice role."""
    async def predicate(interaction: discord.Interaction) -> bool:
        if not interaction.guild or not isinstance(interaction.user, discord.Member):
            # Cannot check permissions in DMs or if user is not a Member object
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return False

        # Check 1: Server Administrator permission
        if interaction.user.guild_permissions.administrator:
            return True

        # Check 2: Specific Role (EmojiPolice)
        try:
            emoji_police_role = discord.utils.get(interaction.guild.roles, name=EMOJI_POLICE_ROLE_NAME)
            if emoji_police_role and emoji_police_role in interaction.user.roles:
                return True
        except Exception as e:
            log.error(f"Error checking role 	{EMOJI_POLICE_ROLE_NAME}	 in guild {interaction.guild.id}: {e}")

        # If neither check passed
        await interaction.response.send_message(
            f"❌ You need the server 	{ADMIN_ROLE_NAME}	 permission or the 	{EMOJI_POLICE_ROLE_NAME}	 role to use this command.",
            ephemeral=True
        )
        return False

    return discord.app_commands.check(predicate)

# --- Context Command Permission Check (for prefix commands like !sync) ---
def is_admin_check_sync(ctx: commands.Context) -> bool:
    """Synchronous check predicate for commands.check: Checks for Administrator permission."""
    if not ctx.guild or not isinstance(ctx.author, discord.Member):
        # Cannot check permissions in DMs or if author is not a Member object
        # Raising CheckFailure is standard for commands.check predicates
        raise commands.CheckFailure("This command can only be used in a server.")

    # Check for Server Administrator permission
    if ctx.author.guild_permissions.administrator:
        return True
    else:
        # Raising CheckFailure is standard for commands.check predicates
        raise commands.CheckFailure(f"You need the server 	{ADMIN_ROLE_NAME}	 permission to use this command.")

# --- Decorator using the synchronous check ---
def is_admin_sync():
    """Decorator for context commands (commands.command) to check for Administrator permission."""
    return commands.check(is_admin_check_sync)

# --- Original Synchronous Check (kept for reference or other uses) ---
def check_permissions_sync(user: discord.Member | discord.User, guild: discord.Guild | None = None) -> bool:
    """Synchronous check for permissions (Admin or EmojiPolice). Useful outside interactions/commands."""
    if isinstance(user, discord.User) or not guild:
        # Cannot check roles for user outside a guild or if guild is None
        return False

    # Check 1: Server Administrator permission
    if user.guild_permissions.administrator:
        return True

    # Check 2: Specific Role (EmojiPolice)
    try:
        emoji_police_role = discord.utils.get(guild.roles, name=EMOJI_POLICE_ROLE_NAME)
        if emoji_police_role and emoji_police_role in user.roles:
            return True
    except Exception as e:
        log.error(f"Error checking role 	{EMOJI_POLICE_ROLE_NAME}	 for user {user.id} in guild {guild.id}: {e}")

    return False

