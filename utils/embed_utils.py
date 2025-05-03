import discord
#import stuff from this project
from config import config
from utils.ui_components import PaginatorView

# --- Embed Creation Utilities ---

def create_error_embed(message: str) -> discord.Embed:
    """Creates a standard error embed."""
    embed = discord.Embed(
        title=f"{config.EMOJI_MAP.get('error', '❌')} Error",
        description=message,
        color=discord.Color.red()
    )
    return embed

def create_success_embed(message: str, title: str = "Success") -> discord.Embed:
    """Creates a standardized success embed."""
    embed = discord.Embed(
        title=f"{config.EMOJI_MAP.get('success', '✔️')} {title}",
        description=message,
        color=discord.Color.green()
    )
    return embed

def create_info_embed(message: str, title: str = "Information") -> discord.Embed:
    """Creates a standardized informational embed."""
    embed = discord.Embed(
        title=f"{config.EMOJI_MAP.get('info', 'ℹ️')} {title}",
        description=message,
        color=discord.Color.blue()
    )
    return embed

def create_stats_embed(interaction: discord.Interaction, title: str, data: list, item_type: str, page_num: int, total_pages: int) -> discord.Embed:
    """Creates a standardized embed for displaying stats (emojis, reactions, stickers)."""
    embed = discord.Embed(
        title=title,
        color=discord.Color.blurple() # Or another suitable color
    )
    guild_name = interaction.guild.name if interaction.guild else "Direct Message"
    icon_url = interaction.guild.icon.url if interaction.guild and interaction.guild.icon else None
    embed.set_author(name=f"Stats for {guild_name}", icon_url=icon_url)

    if not data:
        embed.description = f"No {item_type} data found for this page."
    else:
        lines = []
        start_rank = (page_num - 1) * config.PAGINATION_DEFAULT_LIMIT + 1
        for i, item in enumerate(data):
            rank = start_rank + i
            name = item["name"] # Assumes name is always present
            count = item["count"]
            lines.append(f"`{rank}.` {name} - **{count}** uses")

        embed.description = "\n".join(lines)

    embed.set_footer(text=f"Page {page_num}/{total_pages}")
    return embed

async def paginate_and_send(interaction: discord.Interaction, title: str, all_data: list, item_type: str):
    """Handles pagination for a list of data and sends embeds with navigation."""
    items_per_page = config.PAGINATION_DEFAULT_LIMIT
    if not all_data:
        embed = create_info_embed(f"No {item_type} data found.", title=title)
        # Send ephemeral response
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    chunks = [all_data[i:i + items_per_page] for i in range(0, len(all_data), items_per_page)]
    total_pages = len(chunks)

    def get_page_embed(page_num):
        if 1 <= page_num <= total_pages:
            return create_stats_embed(interaction, title, chunks[page_num-1], item_type, page_num, total_pages)
        else:
            return create_error_embed("Invalid page number requested.")

    initial_embed = get_page_embed(1)
    view = PaginatorView(interaction.user, total_pages, get_page_embed) if total_pages > 1 else discord.ui.View()

    # Send ephemeral response
    if interaction.response.is_done():
        await interaction.followup.send(embed=initial_embed, view=view, ephemeral=True)
    else:
        await interaction.response.send_message(embed=initial_embed, view=view, ephemeral=True)

    # View timeout is handled within PaginatorView

