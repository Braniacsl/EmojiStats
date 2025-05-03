import discord
from typing import Callable, Any
from config import config 

class ConfirmationView(discord.ui.View):
    """A view that asks for confirmation (Yes/No)."""
    def __init__(self, author: discord.User, *, timeout=60.0):
        super().__init__(timeout=timeout)
        self.value = None # Stores the result (True for confirm, False for cancel)
        self.author = author
        self.interaction = None # To store the interaction that confirmed/cancelled

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Ensure only the command author can interact."""
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ This confirmation is not for you.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="✅ Confirm", style=discord.ButtonStyle.danger) # Danger style for destructive actions
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        self.interaction = interaction
        # Disable all buttons after selection
        for item in self.children:
            item.disabled = True
        # Update the original message to show the view is disabled
        await interaction.response.edit_message(view=self)
        self.stop()

    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        self.interaction = interaction
        # Disable all buttons after selection
        for item in self.children:
            item.disabled = True
        # Update the original message to show the view is disabled
        await interaction.response.edit_message(view=self)
        self.stop()

    async def on_timeout(self):
        """Handle view timeout."""
        # Check if self.children is available and not empty
        if hasattr(self, children) and self.children:
            # Disable all buttons on timeout
            for item in self.children:
                item.disabled = True
            # Try to edit the original message if an interaction context is available
            # This might fail if the original message interaction is lost
            # A more robust approach might involve storing the message ID
            # but for simplicity, we try editing via the last known interaction if available.
            if self.interaction:
                try:
                    await self.interaction.edit_original_response(view=self)
                except discord.NotFound:
                    pass # Original message might have been deleted
                except discord.HTTPException as e:
                    print(f"Error editing message on timeout: {e}") # Log error
        self.stop()

class PaginatorView(discord.ui.View):
    """A view for paginating embeds."""
    def __init__(self, author: discord.User, total_pages: int, embed_factory: Callable[[int], discord.Embed], *, timeout=180.0):
        super().__init__(timeout=timeout)
        self.author = author
        self.total_pages = total_pages
        self.embed_factory = embed_factory
        self.current_page = 1
        self._update_buttons()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Ensure only the command author can interact."""
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ You cannot control this pagination.", ephemeral=True)
            return False
        return True

    def _update_buttons(self):
        """Enable/disable buttons based on the current page."""
        # Find buttons by custom_id (more reliable than index)
        first_page_button = discord.utils.get(self.children, custom_id="go_first")
        prev_page_button = discord.utils.get(self.children, custom_id="go_prev")
        next_page_button = discord.utils.get(self.children, custom_id="go_next")
        last_page_button = discord.utils.get(self.children, custom_id="go_last")

        if first_page_button: first_page_button.disabled = self.current_page == 1
        if prev_page_button: prev_page_button.disabled = self.current_page == 1
        if next_page_button: next_page_button.disabled = self.current_page == self.total_pages
        if last_page_button: last_page_button.disabled = self.current_page == self.total_pages

    async def _update_embed(self, interaction: discord.Interaction):
        """Update the message with the embed for the current page."""
        self._update_buttons()
        embed = self.embed_factory(self.current_page)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(emoji=config.EMOJI_MAP.get("page_first", "⏪"), style=discord.ButtonStyle.secondary, custom_id="go_first")
    async def first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = 1
        await self._update_embed(interaction)

    @discord.ui.button(emoji=config.EMOJI_MAP.get("page_prev", "◀️"), style=discord.ButtonStyle.primary, custom_id="go_prev")
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page -= 1
        await self._update_embed(interaction)

    @discord.ui.button(emoji=config.EMOJI_MAP.get("page_next", "▶️"), style=discord.ButtonStyle.primary, custom_id="go_next")
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page += 1
        await self._update_embed(interaction)

    @discord.ui.button(emoji=config.EMOJI_MAP.get("page_last", "⏩"), style=discord.ButtonStyle.secondary, custom_id="go_last")
    async def last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = self.total_pages
        await self._update_embed(interaction)

    async def on_timeout(self):
        """Handle view timeout by disabling buttons."""
        # Check if self.children is available and not empty
        if hasattr(self, children) and self.children:
            for item in self.children:
                item.disabled = True
            # Try to edit the original message if an interaction context is available
            # Similar timeout handling as ConfirmationView
            # Find the interaction associated with the view if possible (might need better state management)
            # For now, assume the last interaction might be available if needed, but it's unreliable.
            # A better way is to store the original message reference.
            # Let's just disable buttons and stop.
        self.stop()

