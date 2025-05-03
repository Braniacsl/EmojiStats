import discord
from discord import app_commands
import logging
# Import from project
from config import config
from utils import embed_utils
from cogs.admin import permissions # Import permissions check

log = logging.getLogger(__name__)

@app_commands.command(name="help", description=config.COMMAND_DESCRIPTIONS.get("help", "Show bot commands."))
@permissions.is_emoji_police() # Apply permission check
async def help_command(interaction: discord.Interaction):
    """Displays a list of available commands and their descriptions."""
    # Defer response
    await interaction.response.defer(ephemeral=True)

    embed = discord.Embed(
        title=f"{config.EMOJI_MAP.get('info', 'ℹ️')} AdriBot Commands",
        description="Here are the available commands:",
        color=discord.Color.blue()
    )

    # Manually list commands based on known structure
    # This is simpler than introspection in test mode without a running bot instance
    commands_info = {
        f"{config.EMOJI_MAP.get('emoji_section', '😀')} Emoji Stats": [
            ("`/emoji top [limit:1-25]`", config.COMMAND_DESCRIPTIONS.get("emoji_top", "Show most used emojis.")),
            ("`/emoji rare [limit:1-25]`", config.COMMAND_DESCRIPTIONS.get("emoji_rare", "Show least used emojis.")),
            ("`/emoji history`", config.COMMAND_DESCRIPTIONS.get("emoji_history", "View full emoji usage history.")),
        ],
        f"{config.EMOJI_MAP.get('reaction_section', '👍')} Reaction Stats": [
            ("`/reaction top [limit:1-25]`", config.COMMAND_DESCRIPTIONS.get("reaction_top", "Show most used reactions.")),
            ("`/reaction rare [limit:1-25]`", config.COMMAND_DESCRIPTIONS.get("reaction_rare", "Show least used reactions.")),
            ("`/reaction history`", config.COMMAND_DESCRIPTIONS.get("reaction_history", "View full reaction usage history.")),
        ],
        f"{config.EMOJI_MAP.get('sticker_section', '🧩')} Sticker Stats": [
            ("`/sticker top [limit:1-25]`", config.COMMAND_DESCRIPTIONS.get("sticker_top", "Show most used stickers.")),
            ("`/sticker rare [limit:1-25]`", config.COMMAND_DESCRIPTIONS.get("sticker_rare", "Show least used stickers.")),
            ("`/sticker history`", config.COMMAND_DESCRIPTIONS.get("sticker_history", "View full sticker usage history.")),
        ],
        f"{config.EMOJI_MAP.get('admin', '🛠️')} Admin Tools": [
            ("`/admin wipe_data`", config.COMMAND_DESCRIPTIONS.get("wipe_data", "[Admin] Wipe all tracked data.")),
            ("`/admin reset_data`", config.COMMAND_DESCRIPTIONS.get("reset_data", "[Admin] Reset all counts to zero.")),
        ],
        f"{config.EMOJI_MAP.get('info', 'ℹ️')} General": [
            ("`/help`", config.COMMAND_DESCRIPTIONS.get("help", "Show this help message.")),
        ],
        # Add the prefix command if applicable
        # f"{config.EMOJI_MAP.get('sync', '🔄')} Manual Sync (Owner Only)": [
        #     (f"`{config.BOT_PREFIX}sync [guild_id]`", "Manually sync slash commands."),
        # ],
    }

    for category, cmds in commands_info.items():
        value = "\n".join([f"{cmd} - {desc}" for cmd, desc in cmds])
        embed.add_field(name=category, value=value, inline=False)

    embed.set_footer(text="Use commands with the specified arguments. [Optional arguments] are shown in brackets.")

    await interaction.followup.send(embed=embed, ephemeral=True)

# Function to register this command with the bot
async def setup(bot: discord.ext.commands.Bot):
    bot.tree.add_command(help_command)
    log.info("Help command added to bot tree.")

