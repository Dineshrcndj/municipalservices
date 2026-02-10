import sqlite3
import datetime
from contextlib import contextmanager
from config import Config

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    cursor = conn.cursor()
    
    # Property Tax table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS property_tax (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        unique_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        address TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        amount_paid REAL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        admin_notes TEXT
    )
    ''')
    
    # EChallan table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS echallan (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        unique_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        vehicle_number TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        amount_paid REAL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        admin_notes TEXT
    )
    ''')
    
    # Admin users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )
    ''')
    
    # Insert default admin user if not exists
    cursor.execute("SELECT * FROM admin_users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO admin_users (username, password_hash) VALUES (?, ?)",
            ('admin', 'pbkdf2:sha256:260000$your_hash_here')  # You should hash the password properly
        )
    
    conn.commit()
    conn.close()

def generate_unique_id(prefix='PT'):
    """Generate unique ID starting from 101"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    cursor = conn.cursor()
    
    if prefix == 'PT':
        cursor.execute("SELECT MAX(CAST(SUBSTR(unique_id, 3) AS INTEGER)) FROM property_tax")
    else:
        cursor.execute("SELECT MAX(CAST(SUBSTR(unique_id, 3) AS INTEGER)) FROM echallan")
    
    result = cursor.fetchone()[0]
    conn.close()
    
    if result is None:
        next_id = 101
    else:
        next_id = result + 1
    
    return f"{prefix}{next_id}"

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()