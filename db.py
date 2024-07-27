import sqlite3
import os
from datetime import datetime
import random
import string

DATABASE_FILE = "discord_auth.db"

def initialize_database():
    if not os.path.exists(DATABASE_FILE):
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        # Create Users table
        c.execute('''CREATE TABLE Users
                     (discord_id TEXT PRIMARY KEY,
                      balance REAL,
                      total_hits INTEGER,
                      registration_datetime TEXT,
                      keys_used INTEGER)''')
        # Create Keys table
        c.execute('''CREATE TABLE Keys
                     (key TEXT PRIMARY KEY,
                      value TEXT,
                      used INTEGER,
                      discord_id TEXT,
                      used_datetime TEXT)''')
        conn.commit()
        conn.close()

def check_key_exist(key):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM Keys WHERE key=?", (key,))
    result = c.fetchone()
    conn.close()
    return result is not None

def get_user_balance(discord_id):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("SELECT balance FROM Users WHERE discord_id=?", (discord_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0.0

def increment_user_hits(discord_id):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("UPDATE Users SET total_hits = total_hits + 1 WHERE discord_id = ?", (discord_id,))
    conn.commit()
    conn.close()

def check_key_used(key):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("SELECT used FROM Keys WHERE key=?", (key,))
    result = c.fetchone()
    conn.close()
    return result[0] == 1 if result else None

def check_user_balance(discord_id, price):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("SELECT balance FROM Users WHERE discord_id=?", (discord_id,))
    result = c.fetchone()
    if result:
        balance = result[0]
        return balance >= price
    return False

def mark_key_used(key, discord_id):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    used_datetime = datetime.now().isoformat()
    c.execute("UPDATE Keys SET used=1, discord_id=?, used_datetime=? WHERE key=?", (discord_id, used_datetime, key))
    conn.commit()
    conn.close()
    return "Key successfully redeemed."

def add_balance(discord_id, amount):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("UPDATE Users SET balance=balance+? WHERE discord_id=?", (amount, discord_id))
    conn.commit()
    conn.close()

def deduct_balance(discord_id, amount):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("UPDATE Users SET balance=balance-? WHERE discord_id=?", (amount, discord_id))
    conn.commit()
    conn.close()

def lookup_key(key):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM Keys WHERE key=?", (key,))
    result = c.fetchone()
    conn.close()
    return result

def lookup_user_id(discord_id):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM Users WHERE discord_id=?", (discord_id,))
    result = c.fetchone()
    conn.close()
    return result

def get_key_value(key):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("SELECT value FROM Keys WHERE key=?", (key,))
    result = c.fetchone()
    conn.close()
    return float(result[0]) if result else None

def redeem(discord_id, key):
    
    mark_key_used(key, discord_id)
    return "Key successfully redeemed."

def does_user_exist(discord_id):
    user_data = lookup_user_id(discord_id)
    return user_data is not None

def register(discord_id, key):
    if does_user_exist(discord_id):
        return "User already registered."
    
    if not check_key_exist(key):
        return "Key does not exist."
    
    key_data = lookup_key(key)
    balance = float(key_data[1])  # Assuming balance is stored as string in key value
    registration_datetime = datetime.now().isoformat()
    
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO Users VALUES (?, ?, ?, ?, ?)", (discord_id, balance, 0, registration_datetime, 0))
    conn.commit()
    conn.close()
    
    mark_key_used(key, discord_id)
    
    return "User registered successfully."

def gen_keys(amount):
    keys = []
    for _ in range(amount):
        key = ''.join(random.choices(string.hexdigits.upper(), k=16))
        keys.append(key)
    return keys

def insert_keys(keys, value):
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    for key in keys:
        c.execute("INSERT INTO Keys (key, value, used) VALUES (?, ?, ?)", (key, value, 0))
        print(f"Inserted key: {key}")
    conn.commit()
    conn.close()

initialize_database()  # Ensure the database and tables are initialized when the module is imported
