import logging
import os
import sqlite3

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///yeetflow.db")


def get_db_connection() -> sqlite3.Connection:
    """Get a SQLite database connection."""
    db_path = DATABASE_URL.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.row_factory = sqlite3.Row  # dict-like access to rows
    return conn


def init_db():
    """Initialize the database with basic tables."""
    create_tables()


# Placeholder for migration functions
def run_migrations():
    """Run database migrations."""
    # TODO: Implement migration system (e.g., Alembic or custom)


def create_tables():
    """Create database tables if they don't exist."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # Create users table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                name TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """,
        )

        # Create flows table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS flows (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                user_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """,
        )

        # Create runs table
        cursor.execute(
            """
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
        """,
        )

        # Create sessions table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                browser_session_id TEXT,
                steel_session_url TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (run_id) REFERENCES runs(id)
            )
        """,
        )

        # Create events table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                type TEXT NOT NULL,
                data TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (run_id) REFERENCES runs(id)
            )
        """,
        )

        conn.commit()

    except sqlite3.Error:
        logger.exception("❌ Database error creating tables")
        conn.rollback()

    finally:
        conn.close()


def seed_test_data():
    """Seed test data for development and testing."""
    create_tables()
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Seed test user
        cursor.execute(
            """
            INSERT OR IGNORE INTO users (id, email, name, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                "550e8400-e29b-41d4-a716-446655440000",
                "test@example.com",
                "Test User",
                "2025-09-16T10:00:00",
                "2025-09-16T10:00:00",
            ),
        )

        # Seed test flows for integration tests
        test_flows = [
            (
                "550e8400-e29b-41d4-a716-446655440000",
                "Test Flow",
                "A test flow for development and testing",
            ),
            (
                "550e8400-e29b-41d4-a716-446655440001",
                "HITL Flow",
                "A flow that requires human-in-the-loop interaction",
            ),
            (
                "550e8400-e29b-41d4-a716-446655440002",
                "Auto Complete Flow",
                "A flow that completes automatically",
            ),
            (
                "550e8400-e29b-41d4-a716-446655440003",
                "PDF Generation Flow",
                "A flow that generates PDF artifacts",
            ),
            (
                "550e8400-e29b-41d4-a716-446655440004",
                "Large Output Flow",
                "A flow that generates large output files",
            ),
            (
                "550e8400-e29b-41d4-a716-446655440005",
                "Multi HITL Flow",
                "A flow with multiple human interaction points",
            ),
        ]

        for flow_id, name, description in test_flows:
            cursor.execute(
                """
                INSERT OR IGNORE INTO flows (
                    id, name, description, user_id, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    flow_id,
                    name,
                    description,
                    "550e8400-e29b-41d4-a716-446655440000",
                    "2025-09-16T10:00:00",
                    "2025-09-16T10:00:00",
                ),
            )

        conn.commit()
        logger.info("✅ Test data seeded successfully")

    except sqlite3.Error:
        logger.exception("❌ Database error seeding test data")
        conn.rollback()
    finally:
        conn.close()
