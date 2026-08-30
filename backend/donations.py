import os
import re
from pathlib import Path

import razorpay
from dotenv import load_dotenv

from backend.database import (
    USE_POSTGRES,
    get_connection,
)


# =========================================================
# BASE DIRECTORY / ENVIRONMENT
# =========================================================

BASE_DIR = (
    Path(__file__)
    .resolve()
    .parents[1]
)


load_dotenv(
    BASE_DIR / ".env"
)


RAZORPAY_KEY_ID = os.getenv(
    "RAZORPAY_KEY_ID",
    ""
)


RAZORPAY_KEY_SECRET = os.getenv(
    "RAZORPAY_KEY_SECRET",
    ""
)


RAZORPAY_WEBHOOK_SECRET = os.getenv(
    "RAZORPAY_WEBHOOK_SECRET",
    ""
)


ADMIN_TOKEN = os.getenv(
    "ADMIN_TOKEN",
    ""
)


# =========================================================
# SUPPORTER TIERS
# =========================================================

SUPPORTER_TIERS = [
    {
        "amount": 1000,
        "title": "Maa's Main Character",
        "icon": "👑",
    },
    {
        "amount": 500,
        "title": "Maha Bhakt",
        "icon": "🪷",
    },
    {
        "amount": 250,
        "title": "Maa's Inner Circle",
        "icon": "🌼",
    },
    {
        "amount": 200,
        "title": "Pujo Pro",
        "icon": "✨",
    },
    {
        "amount": 150,
        "title": "Dhak Crew",
        "icon": "🕺",
    },
    {
        "amount": 100,
        "title": "Pujo Squad",
        "icon": "🎉",
    },
    {
        "amount": 50,
        "title": "Dhak Dost",
        "icon": "🪔",
    },
    {
        "amount": 1,
        "title": "Pujo Bestie",
        "icon": "🌺",
    },
]


def get_supporter_tier(
    amount: int,
):
    amount = int(amount)

    for tier in SUPPORTER_TIERS:

        if amount >= tier["amount"]:
            return tier

    return SUPPORTER_TIERS[-1]


# =========================================================
# SQL HELPER
# =========================================================

def db_query(
    query: str,
):
    """
    Convert SQLite-style placeholders to PostgreSQL
    placeholders when running against Supabase.

    SQLite:
        ?

    PostgreSQL:
        %s
    """

    if USE_POSTGRES:

        return query.replace(
            "?",
            "%s",
        )

    return query


# =========================================================
# VISIBILITY MIGRATION
# =========================================================

def ensure_supporter_visibility_column():

    connection = get_connection()

    try:

        if USE_POSTGRES:

            connection.execute(
                """
                ALTER TABLE supporters
                ADD COLUMN IF NOT EXISTS
                    is_visible
                    INTEGER NOT NULL
                    DEFAULT 1
                """
            )

        else:

            columns = connection.execute(
                """
                PRAGMA table_info(supporters)
                """
            ).fetchall()


            column_names = {
                row["name"]
                for row in columns
            }


            if (
                "is_visible"
                not in column_names
            ):

                connection.execute(
                    """
                    ALTER TABLE supporters
                    ADD COLUMN is_visible
                    INTEGER NOT NULL
                    DEFAULT 1
                    """
                )


        connection.commit()

    finally:

        connection.close()


# =========================================================
# RAZORPAY CLIENT
# =========================================================

def get_razorpay_client():

    if (
        not RAZORPAY_KEY_ID
        or not RAZORPAY_KEY_SECRET
    ):

        raise ValueError(
            "Razorpay test keys are not configured."
        )


    return razorpay.Client(
        auth=(
            RAZORPAY_KEY_ID,
            RAZORPAY_KEY_SECRET,
        )
    )


# =========================================================
# NAME NORMALIZATION
# =========================================================

def normalize_name(
    name: str,
):

    name = name.strip().lower()


    name = re.sub(
        r"\s+",
        " ",
        name,
    )


    return name


# =========================================================
# CHECK SUPPORTER NAME
# =========================================================

def check_name(
    name: str,
):

    normalized = normalize_name(
        name
    )


    connection = get_connection()


    try:

        row = connection.execute(
            db_query(
                """
                SELECT id
                FROM supporters
                WHERE normalized_name = ?
                """
            ),
            (
                normalized,
            ),
        ).fetchone()


        return row is None

    finally:

        connection.close()


# =========================================================
# CREATE DONATION ORDER
# =========================================================

def create_donation_order(
    display_name: str,
    amount_rupees: int,
):

    normalized_name = normalize_name(
        display_name
    )


    connection = get_connection()


    try:

        existing = connection.execute(
            db_query(
                """
                SELECT id
                FROM supporters
                WHERE normalized_name = ?
                """
            ),
            (
                normalized_name,
            ),
        ).fetchone()


        if existing:

            raise ValueError(
                "Supporter name is already taken."
            )


        # -------------------------------------------------
        # CREATE SUPPORTER
        # -------------------------------------------------

        if USE_POSTGRES:

            cursor = connection.execute(
                """
                INSERT INTO supporters (
                    display_name,
                    normalized_name
                )
                VALUES (%s, %s)
                RETURNING id
                """,
                (
                    display_name.strip(),
                    normalized_name,
                ),
            )

            supporter_row = (
                cursor.fetchone()
            )

            supporter_id = (
                supporter_row["id"]
            )

        else:

            cursor = connection.execute(
                """
                INSERT INTO supporters (
                    display_name,
                    normalized_name
                )
                VALUES (?, ?)
                """,
                (
                    display_name.strip(),
                    normalized_name,
                ),
            )

            supporter_id = (
                cursor.lastrowid
            )


        # -------------------------------------------------
        # CREATE RAZORPAY ORDER
        # -------------------------------------------------

        try:

            client = (
                get_razorpay_client()
            )


            order = (
                client.order.create(
                    {
                        "amount":
                            amount_rupees * 100,

                        "currency":
                            "INR",

                        "receipt":
                            f"donation_{supporter_id}",

                        "payment_capture":
                            1,
                    }
                )
            )


        except Exception:

            connection.execute(
                db_query(
                    """
                    DELETE FROM supporters
                    WHERE id = ?
                    """
                ),
                (
                    supporter_id,
                ),
            )


            connection.commit()

            raise


        # -------------------------------------------------
        # CREATE DONATION RECORD
        # -------------------------------------------------

        connection.execute(
            db_query(
                """
                INSERT INTO donations (
                    supporter_id,
                    amount,
                    razorpay_order_id
                )
                VALUES (?, ?, ?)
                """
            ),
            (
                supporter_id,
                amount_rupees,
                order["id"],
            ),
        )


        connection.commit()


        return {
            "order_id":
                order["id"],

            "amount":
                amount_rupees,

            "currency":
                "INR",

            "key_id":
                RAZORPAY_KEY_ID,

            "display_name":
                display_name.strip(),
        }


    finally:

        connection.close()


# =========================================================
# VERIFY DONATION
# =========================================================

def verify_donation(
    order_id: str,
    payment_id: str,
    signature: str,
):

    client = (
        get_razorpay_client()
    )


    connection = get_connection()


    try:

        donation = connection.execute(
            db_query(
                """
                SELECT *
                FROM donations
                WHERE razorpay_order_id = ?
                """
            ),
            (
                order_id,
            ),
        ).fetchone()


        if donation is None:

            raise ValueError(
                "Donation order not found."
            )


        # -------------------------------------------------
        # VERIFY RAZORPAY SIGNATURE
        # -------------------------------------------------

        try:

            client.utility.verify_payment_signature(
                {
                    "razorpay_order_id":
                        order_id,

                    "razorpay_payment_id":
                        payment_id,

                    "razorpay_signature":
                        signature,
                }
            )

        except Exception:

            raise ValueError(
                "Payment signature verification failed."
            )


        # -------------------------------------------------
        # CREDIT SUPPORTER ONCE
        # -------------------------------------------------

        if donation["status"] != "paid":

            connection.execute(
                db_query(
                    """
                    UPDATE donations
                    SET
                        razorpay_payment_id = ?,
                        status = 'paid'
                    WHERE id = ?
                    """
                ),
                (
                    payment_id,
                    donation["id"],
                ),
            )


            connection.execute(
                db_query(
                    """
                    UPDATE supporters
                    SET total_amount =
                        total_amount + ?
                    WHERE id = ?
                    """
                ),
                (
                    donation["amount"],
                    donation["supporter_id"],
                ),
            )


            connection.commit()


        return {
            "success":
                True,

            "amount":
                donation["amount"],
        }


    finally:

        connection.close()


# =========================================================
# RAZORPAY WEBHOOK
# =========================================================

def process_razorpay_webhook(
    event_name: str,
    payload: dict,
    event_id: str,
):

    if not RAZORPAY_WEBHOOK_SECRET:

        raise ValueError(
            "Razorpay webhook secret is not configured."
        )


    if event_name not in {
        "payment.captured",
        "order.paid",
    }:

        return {
            "processed":
                False,

            "message":
                "Event ignored.",
        }


    connection = get_connection()


    try:

        # -------------------------------------------------
        # IDEMPOTENCY
        # -------------------------------------------------

        already_processed = connection.execute(
            db_query(
                """
                SELECT event_id
                FROM webhook_events
                WHERE event_id = ?
                """
            ),
            (
                event_id,
            ),
        ).fetchone()


        if already_processed:

            return {
                "processed":
                    False,

                "duplicate":
                    True,
            }


        # -------------------------------------------------
        # EXTRACT PAYMENT
        # -------------------------------------------------

        payment_entity = (
            payload
            .get("payload", {})
            .get("payment", {})
            .get("entity", {})
        )


        order_entity = (
            payload
            .get("payload", {})
            .get("order", {})
            .get("entity", {})
        )


        payment_id = (
            payment_entity.get(
                "id"
            )
        )


        order_id = (
            payment_entity.get(
                "order_id"
            )
        )


        if not order_id:

            order_id = (
                order_entity.get(
                    "id"
                )
            )


        if not payment_id:

            return {
                "processed":
                    False,

                "message":
                    "Payment ID missing.",
            }


        if not order_id:

            return {
                "processed":
                    False,

                "message":
                    "Order ID missing.",
            }


        # -------------------------------------------------
        # FIND DONATION
        # -------------------------------------------------

        donation = connection.execute(
            db_query(
                """
                SELECT *
                FROM donations
                WHERE razorpay_order_id = ?
                """
            ),
            (
                order_id,
            ),
        ).fetchone()


        if donation is None:

            raise ValueError(
                "Unknown Razorpay order."
            )


        # -------------------------------------------------
        # VERIFY AMOUNT
        # -------------------------------------------------

        razorpay_amount_paise = (
            payment_entity.get(
                "amount"
            )
        )


        if (
            razorpay_amount_paise
            is None
        ):

            raise ValueError(
                "Payment amount missing."
            )


        expected_amount_paise = (
            donation["amount"]
            * 100
        )


        if (
            int(
                razorpay_amount_paise
            )
            != expected_amount_paise
        ):

            raise ValueError(
                "Payment amount does not match donation."
            )


        # -------------------------------------------------
        # RECORD EVENT
        # -------------------------------------------------

        connection.execute(
            db_query(
                """
                INSERT INTO webhook_events (
                    event_id,
                    event_name
                )
                VALUES (?, ?)
                """
            ),
            (
                event_id,
                event_name,
            ),
        )


        # -------------------------------------------------
        # UPDATE DONATION ONCE
        # -------------------------------------------------

        if donation["status"] != "paid":

            connection.execute(
                db_query(
                    """
                    UPDATE donations
                    SET
                        razorpay_payment_id = ?,
                        status = 'paid'
                    WHERE id = ?
                    """
                ),
                (
                    payment_id,
                    donation["id"],
                ),
            )


            connection.execute(
                db_query(
                    """
                    UPDATE supporters
                    SET total_amount =
                        total_amount + ?
                    WHERE id = ?
                    """
                ),
                (
                    donation["amount"],
                    donation["supporter_id"],
                ),
            )


        connection.commit()


        return {
            "processed":
                True,

            "duplicate":
                False,
        }


    finally:

        connection.close()


# =========================================================
# PUBLIC SUPPORTER LEADERBOARD
# =========================================================

def get_leaderboard():

    ensure_supporter_visibility_column()


    connection = get_connection()


    try:

        rows = connection.execute(
            db_query(
                """
                SELECT
                    id,
                    display_name,
                    total_amount
                FROM supporters
                WHERE total_amount > 0
                AND is_visible = 1
                ORDER BY
                    total_amount DESC,
                    id ASC
                LIMIT 20
                """
            )
        ).fetchall()


        leaderboard = []


        for index, row in enumerate(
            rows
        ):

            amount = int(
                row["total_amount"]
            )


            tier = (
                get_supporter_tier(
                    amount
                )
            )


            leaderboard.append(
                {
                    "rank":
                        index + 1,

                    "display_name":
                        row["display_name"],

                    "amount":
                        amount,

                    "title":
                        tier["title"],

                    "icon":
                        tier["icon"],
                }
            )


        return leaderboard


    finally:

        connection.close()


# =========================================================
# ADMIN - ALL SUPPORTERS
# =========================================================

def get_admin_supporters():

    ensure_supporter_visibility_column()


    connection = get_connection()


    try:

        rows = connection.execute(
            db_query(
                """
                SELECT
                    id,
                    display_name,
                    total_amount,
                    is_visible
                FROM supporters
                ORDER BY
                    total_amount DESC,
                    id ASC
                """
            )
        ).fetchall()


        supporters = []


        for row in rows:

            amount = int(
                row["total_amount"]
            )


            tier = (
                get_supporter_tier(
                    amount
                )
            )


            supporters.append(
                {
                    "id":
                        row["id"],

                    "display_name":
                        row["display_name"],

                    "amount":
                        amount,

                    "title":
                        tier["title"],

                    "icon":
                        tier["icon"],

                    "is_visible":
                        bool(
                            row["is_visible"]
                        ),
                }
            )


        return supporters


    finally:

        connection.close()


# =========================================================
# ADMIN - SET SUPPORTER VISIBILITY
# =========================================================

def set_supporter_visibility(
    supporter_id: int,
    visible: bool,
):

    ensure_supporter_visibility_column()


    connection = get_connection()


    try:

        supporter = connection.execute(
            db_query(
                """
                SELECT id
                FROM supporters
                WHERE id = ?
                """
            ),
            (
                supporter_id,
            ),
        ).fetchone()


        if supporter is None:

            raise ValueError(
                "Supporter not found."
            )


        connection.execute(
            db_query(
                """
                UPDATE supporters
                SET is_visible = ?
                WHERE id = ?
                """
            ),
            (
                1 if visible else 0,
                supporter_id,
            ),
        )


        connection.commit()


        return {
            "success":
                True,

            "supporter_id":
                supporter_id,

            "is_visible":
                bool(visible),
        }


    finally:

        connection.close()