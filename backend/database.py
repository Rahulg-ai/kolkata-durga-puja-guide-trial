import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from psycopg.rows import dict_row
import psycopg


# =========================================================
# PROJECT PATHS
# =========================================================

BASE_DIR = Path(
    __file__
).resolve().parents[1]


load_dotenv(
    BASE_DIR / ".env"
)


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    ""
)


SQLITE_DB_FILE = (
    BASE_DIR
    / "data"
    / "durga_puja.db"
)


# =========================================================
# DATABASE TYPE
# =========================================================

USE_POSTGRES = bool(
    DATABASE_URL.strip()
)


# =========================================================
# CONNECTION
# =========================================================

def get_connection():
    """
    Return a database connection.

    Local development:
        Uses SQLite when DATABASE_URL is not configured.

    Vercel / production:
        Uses Supabase PostgreSQL when DATABASE_URL
        is configured.

    Supabase's transaction pooler is recommended for
    serverless applications such as Vercel.
    """

    if USE_POSTGRES:

        connection = psycopg.connect(
            DATABASE_URL,
            row_factory=dict_row,
        )

        return connection


    # -----------------------------------------------------
    # LOCAL SQLITE FALLBACK
    # -----------------------------------------------------

    SQLITE_DB_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


    connection = sqlite3.connect(
        SQLITE_DB_FILE
    )


    connection.row_factory = (
        sqlite3.Row
    )


    # Enable foreign-key enforcement.
    connection.execute(
        "PRAGMA foreign_keys = ON"
    )


    return connection


# =========================================================
# INITIALIZE DATABASE
# =========================================================

def init_database():

    connection = get_connection()


    try:

        if USE_POSTGRES:

            # =============================================
            # POSTGRESQL / SUPABASE
            # =============================================

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS supporters (
                    id BIGSERIAL PRIMARY KEY,

                    display_name TEXT NOT NULL,

                    normalized_name TEXT NOT NULL UNIQUE,

                    total_amount INTEGER NOT NULL DEFAULT 0,

                    is_visible INTEGER NOT NULL DEFAULT 1,

                    created_at TIMESTAMPTZ
                        NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )


            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS donations (
                    id BIGSERIAL PRIMARY KEY,

                    supporter_id BIGINT NOT NULL,

                    amount INTEGER NOT NULL,

                    razorpay_order_id TEXT UNIQUE,

                    razorpay_payment_id TEXT UNIQUE,

                    status TEXT NOT NULL
                        DEFAULT 'created',

                    created_at TIMESTAMPTZ
                        NOT NULL DEFAULT CURRENT_TIMESTAMP,

                    CONSTRAINT donations_supporter_fk
                        FOREIGN KEY (supporter_id)
                        REFERENCES supporters(id)
                        ON DELETE RESTRICT
                )
                """
            )


            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS webhook_events (
                    event_id TEXT PRIMARY KEY,

                    event_name TEXT NOT NULL,

                    created_at TIMESTAMPTZ
                        NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )


            # ---------------------------------------------
            # MIGRATION FOR EXISTING SUPPORTERS TABLE
            # ---------------------------------------------

            connection.execute(
                """
                ALTER TABLE supporters
                ADD COLUMN IF NOT EXISTS
                    is_visible
                    INTEGER NOT NULL DEFAULT 1
                """
            )


            # ---------------------------------------------
            # INDEXES
            # ---------------------------------------------

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_supporters_total_amount
                ON supporters(total_amount DESC)
                """
            )


            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_donations_supporter_id
                ON donations(supporter_id)
                """
            )


            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_donations_status
                ON donations(status)
                """
            )


            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_webhook_events_event_name
                ON webhook_events(event_name)
                """
            )


        else:

            # =============================================
            # SQLITE / LOCAL DEVELOPMENT
            # =============================================

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS supporters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    display_name TEXT NOT NULL,

                    normalized_name TEXT NOT NULL UNIQUE,

                    total_amount INTEGER NOT NULL DEFAULT 0,

                    is_visible INTEGER NOT NULL DEFAULT 1,

                    created_at TEXT
                        NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )


            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS donations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    supporter_id INTEGER NOT NULL,

                    amount INTEGER NOT NULL,

                    razorpay_order_id TEXT UNIQUE,

                    razorpay_payment_id TEXT UNIQUE,

                    status TEXT NOT NULL
                        DEFAULT 'created',

                    created_at TEXT
                        NOT NULL DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY (supporter_id)
                        REFERENCES supporters(id)
                        ON DELETE RESTRICT
                )
                """
            )


            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS webhook_events (
                    event_id TEXT PRIMARY KEY,

                    event_name TEXT NOT NULL,

                    created_at TEXT
                        NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )


            # ---------------------------------------------
            # SQLITE MIGRATION
            # ---------------------------------------------

            columns = connection.execute(
                """
                PRAGMA table_info(supporters)
                """
            ).fetchall()


            column_names = {
                row["name"]
                for row in columns
            }


            if "is_visible" not in column_names:

                connection.execute(
                    """
                    ALTER TABLE supporters
                    ADD COLUMN is_visible
                    INTEGER NOT NULL DEFAULT 1
                    """
                )


        connection.commit()


    finally:

        connection.close()