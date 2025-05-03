EmojiStatsBot - Easy Setup Guide (For Dummies Like Me!)
Hey there! 👋 So you want to run this cool Emoji Stats Bot? Awesome! This guide will walk you through setting it up, step-by-step, even if you don't code (like me!). We'll use Visual Studio Code (VS Code) because it makes things easier.
🧰 What You Need First
Make sure you have these ready:

    ✅ Python: Version 3.8 or newer. (If you're not sure, open a terminal/PowerShell and type python --version or python3 --version).
    ✅ Discord Bot Token: Your secret key for the bot. Get it from the Discord Developer Portal . Keep it safe!
    ✅ VS Code: The code editor we'll use. Download it here if you don't have it.
    ✅ Terminal/PowerShell: A command window. VS Code has one built-in (Terminal > New Terminal).

🗂️ Getting Your Files Organized (Super Important!)
When we're done, your main project folder in VS Code should look something like this:

YourMainProjectFolder/ (e.g., AdriBotTheFirst)
└── emoji_stats_bot/       <-- This is the main bot package!
    ├── admin/             <-- Folder for admin stuff
    │   ├── __init__.py    <-- Empty file, tells Python it's a package part
    │   └── ... (other admin files)
    ├── commands/          <-- Folder for bot commands
    │   ├── __init__.py    <-- Empty file
    │   └── ... (other command files)
    ├── events/            <-- Folder for bot events (like seeing messages)
    │   ├── __init__.py    <-- Empty file
    │   └── ... (other event files)
    ├── bot-env/           <-- Your Python virtual spot (keeps things tidy)
    ├── __init__.py        <-- Empty file for the main package
    ├── config.py          <-- Bot settings
    ├── db_utils.py        <-- Database helpers
    ├── embed_utils.py     <-- Makes messages look pretty
    ├── my_bot.py          <-- The main brain of the bot!
    ├── .env               <-- Where your secret token lives
    ├── requirements.txt   <-- List of things the bot needs to run
    ├── SETUP_GUIDE.md     <-- This guide!
    └── emoji_stats.db     <-- The bot's memory (created automatically)
    └── (Maybe .gitignore, README.md, etc.)

Key things:

    All the bot's code lives inside the emoji_stats_bot folder.
    Those __init__.py files are important, even though they're empty!

🔧 Let's Set It Up! Step-by-Step

    Open Your Project in VS Code:
        Go to File > Open Folder... and choose your main project folder (the one containing emoji_stats_bot).
    Create a Clean Space (Virtual Environment):
        Open the terminal in VS Code (Terminal > New Terminal).
        Go into the bot's folder: Type cd emoji_stats_bot and press Enter.
        Create the virtual space: Type python -m venv bot-env (or python3) and press Enter. You'll see a new bot-env folder appear.
    Activate the Clean Space:
        Windows (PowerShell/CMD): Type .\bot-env\Scripts\activate and press Enter.
        Mac/Linux (Bash/Zsh): Type source bot-env/bin/activate and press Enter.
        You should see (bot-env) at the start of your terminal line. Success! ✨
        VS Code might ask if you want to use this new environment. Say yes! If not, click the Python version in the bottom bar and select the one inside bot-env.
    Install the Bot's Tools (Dependencies):
        Make sure (bot-env) is still active in your terminal.
        Type pip install -r requirements.txt (or pip3) and press Enter.
        Wait for it to download and install everything listed in requirements.txt.
    Tell the Bot Its Secret Token (.env file):
        Find the .env file inside the emoji_stats_bot folder.
        Open it and change the line to:
        env

        DISCORD_TOKEN="YOUR_ACTUAL_BOT_TOKEN"
        (Replace YOUR_ACTUAL_BOT_TOKEN with the real token you got from Discord).
        🟠 Safety First! Make sure your .gitignore file lists .env and bot-env/ so you don't accidentally share your token online!
    Start the Bot! 🎉
        Make sure (bot-env) is active in the terminal.
        Go back to the main project folder (the one above emoji_stats_bot): Type cd .. and press Enter.
        Run the bot: Type python -m emoji_stats_bot.my_bot and press Enter.
        The -m tells Python to run it correctly now that the code is in a package.
        You should see messages in the terminal saying the bot is logging in and ready!
    Make Commands Appear (Syncing):
        Sometimes slash commands (/) need a little nudge to show up the first time.
        Go to a Discord channel where your bot is.
        Type !sync (or whatever prefix is in config.py, default is !).
        Only the Bot Owner can do this!
        It might take a minute (or up to an hour for all servers) for commands to appear everywhere.

🤔 Uh Oh! Something Went Wrong? (Troubleshooting)

    Error messages? Try running the test script! Make sure (bot-env) is active, go into the emoji_stats_bot folder (cd emoji_stats_bot), and run:
    bash

    python test_setup.py

    It checks for common problems like missing files, bad tokens, or missing tools.
    ModuleNotFoundError? Did you activate the virtual environment ((bot-env))? Did pip install -r requirements.txt finish without errors? Are you running the bot with python -m emoji_stats_bot.my_bot from the correct folder?
    Invalid Token? Double-check the token in your .env file. No extra spaces or quotes?
    Commands not showing up? Try the !sync command again. Wait a bit. Make sure the bot has application.commands scope enabled in the Developer Portal when you invited it.
    Permission errors in Discord? Make sure the bot has permissions to read messages, send messages, use emojis/stickers, add reactions, etc., in the server settings.

🛑 How to Stop the Bot

    Go back to the terminal window where the bot is running.
    Press Ctrl + C on your keyboard.

🗝️ How to Start the Bot

    python my_bot.py

That's it! You should be all set. Have fun with your stats! 😄