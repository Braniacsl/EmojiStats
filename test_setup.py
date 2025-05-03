import os
import sys
import asyncio
import sqlite3  # <-- Added missing import here

# --- Dependency Check ---
def check_imports():
    print("🔍 Checking required libraries...")
    missing_libs = []
    try:
        import discord
        print("  ✅ discord.py found.")
    except ImportError:
        missing_libs.append("discord.py")
        print("  ❌ discord.py not found.")

    try:
        from dotenv import load_dotenv
        print("  ✅ python-dotenv found.")
    except ImportError:
        missing_libs.append("python-dotenv")
        print("  ❌ python-dotenv not found.")

    # Check if sqlite3 module itself is available (should always be)
    try:
        # No need to import again if already imported at top level
        pass
        print("  ✅ sqlite3 found (standard library).")
    except ImportError:
        missing_libs.append("sqlite3")
        print("  ❌ sqlite3 not found (unexpected!).")

    if missing_libs:
        print(f"\n⚠️ Please install missing libraries: pip install {' '.join(missing_libs)}")
        return False
    print("✅ All required libraries seem to be installed.")
    return True

# --- Environment Check ---
def check_environment():
    print("\n🔍 Checking environment (.env file and token)...")
    # Assume .env is in the same directory as this script, or the parent if script is in a subfolder
    script_dir = os.path.dirname(__file__)
    env_path = os.path.join(script_dir, ".env")
    if not os.path.exists(env_path):
        # If not found, check one level up (common if test script is in a /tests folder)
        env_path_parent = os.path.join(os.path.dirname(script_dir), ".env")
        if os.path.exists(env_path_parent):
            env_path = env_path_parent
        else:
            print(f"❌ ERROR: .env file NOT found in {script_dir} or its parent directory.")
            return None  # Indicate failure to find .env

    print(f"  ✅ .env file found at: {env_path}")
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=env_path)

    token = os.getenv("DISCORD_TOKEN")
    if token and len(token) > 50:  # Basic sanity check for token length
        print(f"  ✅ DISCORD_TOKEN loaded successfully (length: {len(token)}). Note: Length check is basic.")
        return token
    elif token:
        print(f"  ⚠️ WARNING: DISCORD_TOKEN loaded but seems short (length: {len(token)}). Is it correct?")
        return token  # Return potentially short token for API check
    else:
        print("  ❌ ERROR: DISCORD_TOKEN not found or empty in .env file.")
        return None

# --- Database Structure Check ---
def check_database(db_name="emoji_stats.db"):
    print(f"\n🔍 Checking database structure (\"{db_name}\")...")
    db_path = os.path.join(os.path.dirname(__file__), db_name)
    if not os.path.exists(db_path):
        print(f"  ⚠️ Database file \"{db_path}\" not found. This is normal if the bot hasn't run yet.")
        return True  # Not an error if file doesn't exist yet

    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        db_ok = True

        # Check for old tables (indicates need for migration/deletion)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='emoji_stats'")
        if cursor.fetchone():
            print("  ❌ OLD STRUCTURE DETECTED: Found unified \"emoji_stats\" table.")
            print("     -> Recommendation: Delete the emoji_stats.db file and let the bot recreate it.")
            db_ok = False  # Mark as needing attention
        else:
            print("  ✅ Correct Structure: No legacy \"emoji_stats\" table found.")

        # Check if any new guild-specific tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'guild\\_%\\_emojis' ESCAPE '\\' LIMIT 1")
        if cursor.fetchone():
            print("  ✅ Guild-specific tables (e.g., guild_..._emojis) exist.")
        else:
            print("  ℹ️ No guild-specific tables found yet (normal if bot hasn't run in any servers).")

        conn.close()
        print("✅ Database structure check completed.")
        return db_ok

    except sqlite3.Error as e:
        print(f"  ❌ Database check failed with error: {e}")
        if conn:
            conn.close()
        return False
    except Exception as e:
        print(f"  ❌ An unexpected error occurred during database check: {e}")
        if conn:
            conn.close()
        return False

# --- Discord API Check ---
async def check_discord_api(token):
    print("\n🌐 Testing Discord API connection...")
    if not token:
        print("  ❌ Cannot test Discord API: Token not loaded.")
        return False

    import discord
    intents = discord.Intents.default()  # Use minimal intents for login test
    client = discord.Client(intents=intents)
    login_successful = False

    try:
        @client.event
        async def on_ready():
            nonlocal login_successful
            print(f"  ✅ Discord API connection successful (Logged in as: {client.user}).")
            login_successful = True
            await client.close()  # Close connection immediately after successful login

        # Run the client
        # Use asyncio.wait_for to add a timeout
        try:
            await asyncio.wait_for(client.start(token), timeout=15.0)
        except asyncio.TimeoutError:
            print("  ❌ Discord API connection timed out (15 seconds).")
            # Attempt to close gracefully if possible
            if not client.is_closed():
                await client.close()
            return False
        except discord.LoginFailure:
            print("  ❌ Discord API Login Failed: Invalid token provided in .env file.")
            return False
        except discord.PrivilegedIntentsRequired:
            print("  ❌ Discord API Error: Missing Privileged Intents (like Members or Message Content). Check bot settings on Discord Developer Portal.")
            return False
        except Exception as e:
            # Catch other potential errors during client.start
            print(f"  ❌ An error occurred during Discord client startup: {e}")
            if not client.is_closed():
                await client.close()
            return False

        # This part might not be reached if timeout or error occurs, handled above
        return login_successful

    except Exception as e:
        # Catch errors during client initialization or event setup
        print(f"  ❌ An unexpected error occurred setting up Discord client: {e}")
        return False

# --- Main Execution ---
async def main():
    print("--- Starting Bot Setup Test --- (Run from your bot's main directory)")
    results = {}

    results["imports"] = check_imports()
    if not results["imports"]:
        print("\n--- Test Aborted: Missing libraries. ---")
        sys.exit(1)

    token = check_environment()
    results["environment"] = (token is not None)

    results["database"] = check_database()

    # Only check Discord API if environment setup was successful
    if results["environment"]:
        results["discord_api"] = await check_discord_api(token)
    else:
        results["discord_api"] = False
        print("\nSkipping Discord API check due to environment setup issues.")

    print("\n--- Test Summary ---")
    all_passed = True
    for test_name, passed in results.items():
        status_icon = "✅" if passed else "❌"
        # Special case for database: ⚠️ if structure is old but check didn't fail
        if test_name == "database" and not passed and os.path.exists("emoji_stats.db"):
            # Check if the failure was due to old structure specifically
            conn_temp = None  # Initialize conn_temp
            try:
                conn_temp = sqlite3.connect("emoji_stats.db")
                cursor_temp = conn_temp.cursor()
                cursor_temp.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='emoji_stats'")
                if cursor_temp.fetchone():
                    status_icon = "⚠️"  # Mark as warning if old structure was the only issue
            except sqlite3.Error as db_err:
                print(f"  (Error during summary db check: {db_err})")  # Log error if summary check fails
            finally:
                if conn_temp:
                    conn_temp.close()

        print(f"  {status_icon} {test_name.replace('_', ' ').title()}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n🎉 All basic setup checks passed!")
    else:
        print("\n🔧 Some setup checks failed or require attention. Please review the errors above.")

if __name__ == "__main__":
    # Use asyncio.run() to execute the async main function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")