import discord

# --- Bot Settings ---
BOT_PREFIX = "!" # Or None if only using slash commands
DATABASE_NAME = "emoji_stats.db"

# --- Role Names (Case-sensitive) ---
# Used for permission checks. Ensure these match the roles in the target Discord server.
ADMIN_ROLE_NAME = "Administrator"
EMOJI_POLICE_ROLE_NAME = "EmojiPolice"

# --- Emojis for UI ---
# Using common Unicode emojis as defaults. Can be customized.
EMOJI_MAP = {
    "top": "👑",
    "rare": "💀",
    "history": "📜",
    "wipe_data": "💥",
    "reset_data": "♻️",
    "sync": "🔄",
    "error": "❌",
    "confirm": "✅",
    "cancel": "❌", # Often same as error
    "info": "ℹ️",
    "stats": "📊",
    "leaderboard": "🏆",
    "admin": "🛠️",
    "emoji_section": "😀",
    "reaction_section": "👍",
    "sticker_section": "🧩",
    "success": "✔️",
    "warning": "⚠️",
    "page_next": "▶️",
    "page_prev": "◀️",
    "page_first": "⏪",
    "page_last": "⏩",
    "guild_setup": "🛡️",
}

# --- Command Descriptions (Optional, for help command) ---
COMMAND_DESCRIPTIONS = {
    "emoji_history": "View full emoji usage history (paginated).",
    "emoji_top": "Show the most used emojis (default 10).",
    "emoji_rare": "Show the least used emojis (default 10).",
    "reaction_history": "View full reaction usage history (paginated).",
    "reaction_top": "Show the most used reactions (default 10).",
    "reaction_rare": "Show the least used reactions (default 10).",
    "sticker_history": "View full sticker usage history (paginated).",
    "sticker_top": "Show the most used stickers (default 10).",
    "sticker_rare": "Show the least used stickers (default 10).",
    "wipe_data": "[Admin] Permanently delete ALL tracked data for this server.",
    "reset_data": "[Admin] Reset all usage counts to zero (keeps items tracked).",
    "help": "List all available commands and their functions.",
}

# --- Discord Intents (Required for the bot to function) ---
# These define what events the bot listens to.
intents = discord.Intents.default()
intents.messages = True         # To read messages for emojis/stickers
intents.message_content = True  # REQUIRED to read message content
intents.reactions = True        # To track reactions
intents.guilds = True           # For guild information and setup
intents.members = True          # REQUIRED for checking roles/permissions

# --- Test Mode Configuration ---
# Simulate guild IDs for testing purposes when not connected to Discord
TEST_MODE_GUILD_IDS = [123456789012345678, 987654321098765432] # Example IDs
TEST_MODE_GUILD_NAMES = { # Optional: Map IDs to names for clearer logs
    123456789012345678: "Test Server Alpha",
    987654321098765432: "Test Server Beta",
}

# --- Pagination Settings ---
PAGINATION_DEFAULT_LIMIT = 10 # Items per page

