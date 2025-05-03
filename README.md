# EmojiStatsBot (Refactored)
*A Discord bot that tracks emoji, reaction, and sticker usage per server, providing detailed statistics and leaderboards.*
## ✨ Features

    Per-Server Statistics: Tracks usage independently for each server the bot is in.
    Comprehensive Tracking: Monitors custom emojis, standard Unicode emojis (in reactions), and stickers.
    Modular Codebase: Refactored into organized modules for commands, events, admin tools, and utilities.
    Detailed History: View complete usage history for emojis, reactions, and stickers (/emoji_history, /reaction_history, /sticker_history).
    Leaderboards: Display top-10 and rare-10 usage (/emoji_top10, /emoji_rare10, etc.).
    Admin Tools: Secure commands for wiping or resetting server-specific data (/wipe_data, /reset_data).
    SQLite Database: Stores data locally in emoji_stats.db with guild-specific tables.
    Easy Setup: Configuration via .env file and clear setup guide.
    Slash Commands: Utilizes Discord's modern slash command interface.

## 🛠️ Commands
All commands use Discord's slash command interface (/). Access requires Administrator permissions or the EmojiPolice role.
### General:
    /help: Displays this list of commands and their 
    descriptions.

### Emoji Stats:

    /emoji_history: 📜 View full emoji usage history (paginated).
    /emoji_top10: 👑 Show the top 10 most used emojis.
    /emoji_rare10: 💀 Show the 10 least used emojis.

### Reaction Stats:

    /reaction_history: 📜 View full reaction usage history (paginated).
    /reaction_top10: 👑 Show the top 10 most used reactions.
    /reaction_rare10: 💀 Show the 10 least used reactions.

### Sticker Stats:

    /sticker_history: 📜 View full sticker usage history (paginated).
    /sticker_top10: 👑 Show the top 10 most used stickers.
    /sticker_rare10: 💀 Show the 10 least used stickers.

### Admin Tools:

    /wipe_data: 💥 DELETE ALL tracked data for this server (requires confirmation).
    /reset_data: ♻️ Reset all counts to zero for this server (requires confirmation).
    !sync [guild_id] (Prefix Command - Bot Owner Only): 🔄 Manually syncs slash commands globally or to a specific guild.

## 🚀 Multi-Server Support
Yes! This refactored version fully supports per-server statistics. All data is stored in separate tables for each Discord server (guild), ensuring privacy and accurate tracking across multiple communities.
## ⚙️ Setup
To set up and run this project locally, follow the steps below

### 1. Clone the Repository
First, clone the repository to your local machine using the following command:
```bash
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```
___
### 2. Create and Activate a Virtual Environment
It is recommended to use a virtual environment to manage dependencies.

- Create a virtual environment :
```bash
python -m venv .venv
```
- Activate the virtual environment :
    - On Windows :
    ```bash
    .venv\Scripts\activate
    ```
    - On macOS/Linux :
    ```bash
    source .venv/bin/activate
    ```
Once activated, you should see (.venv) in your terminal prompt, indicating that the virtual environment is active.
___
### 3. Add Your API Key
Before proceeding, you need to add your API key to the project.

- Locate the .env.example file in the root of the repository.
- Rename it to .env:
```bash
cp .env.example .env
```
- Open the .env file in a text editor and replace the placeholder value with your actual API key:
```
API_KEY=your_api_key_here
```
### 4. Install Dependencies
Install the required dependencies using the requirements.txt file:

```bash
pip install -r requirements.txt
```
___
### 5. Test Your Setup
Before running the bot, you can verify that your connection and credentials are working by running the test script:

```bash
python test_setup.py
```
- If everything is configured correctly, the script will confirm that the connection and credentials are functional.
- If there are any issues, check your configuration files or credentials.
___
### 6. Run the Bot
Once your setup is verified, you can start the bot by running:

```bash
python my_bot.py
```
- The bot should now be operational and ready to interact with your server.
___
Notes
- Ensure that you have Python 3.8 or higher installed on your system.
- If you encounter any issues during setup, consult the Troubleshooting section or open an issue in the repository.
___

🏆 Credits
This bot uses code originally created by SethCohen 💜

    🤖 Original Bot ID: 757326308547100712
    🔗 Source: Emoji Utilities GitHub
    📄 License: MIT
    👾 Used under: MIT License Terms

📄 MIT License (Full Text)
MIT License
Copyright (c) 2020 SethCohen
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.