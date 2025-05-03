import sqlite3
import time
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)

# --- Database Connection ---
def get_db_connection(db_path="emoji_stats.db"):
    """Establish a connection to the SQLite database with retry logic."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Increased timeout, added check_same_thread=False for potential async use cases
            # though direct async operations on the connection itself are not recommended.
            conn = sqlite3.connect(db_path, timeout=10, check_same_thread=False)
            conn.row_factory = sqlite3.Row # Return rows as dictionary-like objects
            # Execute PRAGMA settings for performance and safety
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("PRAGMA journal_mode=WAL;")  # Write-Ahead Logging for concurrency
            conn.execute("PRAGMA synchronous = NORMAL;") # Balance performance and safety
            conn.execute("PRAGMA cache_size=-4000;")  # Increase cache size (e.g., 4MB)
            log.info(f"Database connection successful to {db_path}")
            return conn
        except sqlite3.Error as e:
            log.warning(f"DB connection failed (attempt {attempt+1}/{max_retries}) 	 {e}")
            if attempt == max_retries - 1:
                log.error("Max retries reached. Could not connect to database.")
                raise # Re-raise the last exception
            time.sleep(1) # Wait before retrying
    return None # Should not be reached if raise works

# --- Database Execution Wrapper ---
def safe_db_execute(conn, query, params=()):
    """Execute a database query safely with error handling and rollback."""
    if not conn:
        log.error("Cannot execute query: No database connection.")
        return False, None # Indicate failure, return no cursor
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        # log.debug(f"Executed: {query} with {params}") # Optional: for debugging
        return True, cursor # Indicate success, return cursor for fetching results if needed
    except sqlite3.Error as e:
        log.error(f"Database error during execute: {e} (Query: {query}, Params: {params})")
        if conn:
            try:
                conn.rollback()
                log.info("Database rollback successful.")
            except sqlite3.Error as rb_e:
                log.error(f"Error during rollback: {rb_e}")
        return False, None # Indicate failure
    # No finally block needed to close cursor if we return it

# --- Table Name Sanitization ---
def sanitize_table_name(name):
    """Sanitize table names to prevent SQL injection by allowing only alphanumeric and underscore."""
    # Ensure input is a string before processing
    name_str = str(name)
    # Basic check to prevent purely numeric names starting with a digit if that causes issues
    if name_str.isdigit():
        name_str = f"_{name_str}" # Prepend underscore if purely numeric
    # Filter characters
    sanitized = "".join(c for c in name_str if c.isalnum() or c == "_")
    # Ensure it's not empty after sanitization
    if not sanitized:
        raise ValueError(f"Invalid name for table sanitization: {name}")
    return sanitized

# --- Guild Table Management ---
def ensure_guild_tables(conn, guild_id):
    """Create required tables for a specific guild if they don't exist."""
    try:
        sanitized_id = sanitize_table_name(guild_id)
    except ValueError as e:
        log.error(f"Invalid guild ID for table creation: {guild_id} - {e}")
        return False

    tables = {
        # Using name for emoji/reaction for simplicity, assuming they are unique strings
        # Using sticker_id as primary key as name might not be unique or could change
        "emojis": "name TEXT PRIMARY KEY, count INTEGER DEFAULT 0 NOT NULL, last_used TIMESTAMP",
        "reactions": "name TEXT PRIMARY KEY, count INTEGER DEFAULT 0 NOT NULL, last_used TIMESTAMP",
        "stickers": "sticker_id TEXT PRIMARY KEY, name TEXT, count INTEGER DEFAULT 0 NOT NULL, last_used TIMESTAMP"
    }
    success = True
    for table_type, schema in tables.items():
        # Use f-string correctly for table name construction
        safe_table_name = f"guild_{sanitized_id}_{table_type}"
        query = f"CREATE TABLE IF NOT EXISTS {safe_table_name} ({schema});"
        executed, _ = safe_db_execute(conn, query)
        if not executed:
            log.error(f"Failed to ensure table {safe_table_name} for guild {guild_id}")
            success = False # Mark failure but continue trying other tables
        # else: # Optional: for debugging
            # log.debug(f"Ensured table {safe_table_name} exists.")
    return success

# --- Data Retrieval Functions ---
def get_items(conn, guild_id, table_type, order_by="count", ascending=False, limit=None):
    """Fetch items (emoji, reaction, sticker) from a guild's table."""
    try:
        sanitized_id = sanitize_table_name(guild_id)
        table_name = f"guild_{sanitized_id}_{table_type}"
    except ValueError as e:
        log.error(f"Invalid guild ID or table type for get_items: {guild_id}, {table_type} - {e}")
        return []

    column = "name" # Default column to select (emoji/reaction name)
    if table_type == "stickers":
        column = "name, sticker_id" # Select sticker name and ID

    order_direction = "ASC" if ascending else "DESC"
    limit_clause = f"LIMIT {int(limit)}" if limit is not None and isinstance(limit, int) and limit > 0 else ""

    # Ensure order_by is a valid column to prevent injection
    valid_columns = ["name", "count", "last_used"]
    if table_type == "stickers":
        valid_columns.append("sticker_id")
    if order_by not in valid_columns:
        log.warning(f"Invalid order_by column specified: {order_by}. Defaulting to 'count'.")
        order_by = "count"

    # Corrected query formatting
    query = f"SELECT {column}, count FROM {table_name} WHERE count > 0 ORDER BY {order_by} {order_direction} {limit_clause};"
    executed, cursor = safe_db_execute(conn, query)
    if executed and cursor:
        try:
            return cursor.fetchall()
        except sqlite3.Error as fetch_err:
            log.error(f"Error fetching results: {fetch_err}")
            return []
        finally:
            cursor.close()
    return [] # Return empty list on failure or no results

def get_all_items(conn, guild_id, table_type):
    """Fetch all items regardless of count for a guild's table, ordered by count descending."""
    # No limit needed
    return get_items(conn, guild_id, table_type, order_by="count", ascending=False, limit=None)

def get_top_items(conn, guild_id, table_type, limit=10):
    """Fetch the top N most used items."""
    return get_items(conn, guild_id, table_type, order_by="count", ascending=False, limit=limit)

def get_rare_items(conn, guild_id, table_type, limit=10):
    """Fetch the N least used items (with count > 0)."""
    return get_items(conn, guild_id, table_type, order_by="count", ascending=True, limit=limit)

def get_tracking_since(conn, guild_id, table_type):
    """Get the earliest tracking date for a specific table type in a guild."""
    try:
        sanitized_id = sanitize_table_name(guild_id)
        table_name = f"guild_{sanitized_id}_{table_type}"
    except ValueError as e:
        log.error(f"Invalid guild ID or table type for get_tracking_since: {guild_id}, {table_type} - {e}")
        return None

    query = f"SELECT MIN(last_used) FROM {table_name};"
    executed, cursor = safe_db_execute(conn, query)
    if executed and cursor:
        try:
            result = cursor.fetchone()
            return result[0] if result and result[0] else None
        except sqlite3.Error as fetch_err:
            log.error(f"Error fetching tracking date: {fetch_err}")
            return None
        finally:
            cursor.close()
    return None

# --- Data Update Functions ---
def update_count(conn, guild_id, table_type, item_name, item_id=None):
    """Increment the count for an emoji, reaction, or sticker."""
    try:
        sanitized_id = sanitize_table_name(guild_id)
        table_name = f"guild_{sanitized_id}_{table_type}"
    except ValueError as e:
        log.error(f"Invalid guild ID or table type for update_count: {guild_id}, {table_type} - {e}")
        return False

    now = datetime.utcnow()

    if table_type == "stickers":
        if not item_id:
            log.error("Sticker ID is required to update sticker count.")
            return False
        # Upsert for stickers based on sticker_id
        # Use standard Python string formatting for the query
        # Ensure excluded.last_used and excluded.name are used correctly
        query = (
            f"INSERT INTO {table_name} (sticker_id, name, count, last_used) VALUES (?, ?, 1, ?) "
            f"ON CONFLICT(sticker_id) DO UPDATE SET count = count + 1, last_used = excluded.last_used, name = excluded.name;"
        )
        params = (str(item_id), item_name, now)
    else:
        # Upsert for emojis/reactions based on name
        # Ensure excluded.last_used is used correctly
        query = (
            f"INSERT INTO {table_name} (name, count, last_used) VALUES (?, 1, ?) "
            f"ON CONFLICT(name) DO UPDATE SET count = count + 1, last_used = excluded.last_used;"
        )
        params = (item_name, now)

    executed, cursor = safe_db_execute(conn, query, params)
    if cursor:
        cursor.close() # Close cursor after execution
    return executed

# --- Data Deletion/Reset Functions ---
def wipe_guild_data(conn, guild_id):
    """Delete all rows from all tracking tables for a specific guild."""
    try:
        sanitized_id = sanitize_table_name(guild_id)
    except ValueError as e:
        log.error(f"Invalid guild ID for wipe_guild_data: {guild_id} - {e}")
        return False

    success = True
    for table_type in ["emojis", "reactions", "stickers"]:
        table_name = f"guild_{sanitized_id}_{table_type}"
        query = f"DELETE FROM {table_name};"
        executed, cursor = safe_db_execute(conn, query)
        if cursor:
            cursor.close()
        if not executed:
            log.error(f"Failed to wipe data from {table_name}")
            success = False
    return success

def reset_guild_counts(conn, guild_id):
    """Reset all counts to zero in tracking tables for a specific guild."""
    try:
        sanitized_id = sanitize_table_name(guild_id)
    except ValueError as e:
        log.error(f"Invalid guild ID for reset_guild_counts: {guild_id} - {e}")
        return False

    success = True
    for table_type in ["emojis", "reactions", "stickers"]:
        table_name = f"guild_{sanitized_id}_{table_type}"
        query = f"UPDATE {table_name} SET count = 0;"
        executed, cursor = safe_db_execute(conn, query)
        if cursor:
            cursor.close()
        if not executed:
            log.error(f"Failed to reset counts in {table_name}")
            success = False
    return success

# --- Utility to close connection ---
def close_db_connection(conn):
    """Close the database connection if it's open."""
    if conn:
        try:
            conn.close()
            log.info("Database connection closed.")
        except sqlite3.Error as e:
            log.error(f"Error closing database connection: {e}")

