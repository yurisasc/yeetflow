import sqlite3
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///yeetflow.db")

def get_db_connection() -> sqlite3.Connection:
    """Get a SQLite database connection."""
    conn = sqlite3.connect(DATABASE_URL.replace("sqlite:///", ""))
    conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
    return conn

def init_db():
    """Initialize the database with basic tables."""
    create_tables()

# Placeholder for migration functions
def run_migrations():
    """Run database migrations."""
    # TODO: Implement migration system (e.g., Alembic or custom)
    pass

def create_tables():
    """Create database tables if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')
    
    # Create flows table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flows (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            user_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Create runs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS runs (
            id TEXT PRIMARY KEY,
            flow_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            status TEXT NOT NULL,
            session_url TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            artifact_path TEXT,
            FOREIGN KEY (flow_id) REFERENCES flows(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Create sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL,
            browser_session_id TEXT,
            steel_session_url TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (run_id) REFERENCES runs(id)
        )
    ''')
    
    # Create events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL,
            type TEXT NOT NULL,
            data TEXT,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (run_id) REFERENCES runs(id)
        )
    ''')
    
def seed_test_data():
    """Seed test data for development and testing."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Seed test user
        cursor.execute('''
            INSERT OR IGNORE INTO users (id, email, name, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            'test-user-id',
            'test@example.com',
            'Test User',
            '2025-09-16T10:00:00',
            '2025-09-16T10:00:00'
        ))

        # Seed test flow
        cursor.execute('''
            INSERT OR IGNORE INTO flows (id, name, description, user_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            'test-flow',
            'Test Flow',
            'A test flow for development and testing',
            'test-user-id',
            '2025-09-16T10:00:00',
            '2025-09-16T10:00:00'
        ))

        conn.commit()
        print("✅ Test data seeded successfully")

    except Exception as e:
        print(f"❌ Error seeding test data: {e}")
        conn.rollback()
    finally:
        conn.close()
