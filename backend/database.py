import psycopg2
from psycopg2.extras import RealDictCursor

from config import DATABASE_URL


def get_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def init_db():
    ddl = """
    CREATE TABLE IF NOT EXISTS customers (
        customer_id SERIAL PRIMARY KEY,
        customer_name VARCHAR(255) NOT NULL,
        email_address VARCHAR(255) NOT NULL UNIQUE,
        phone_number VARCHAR(50),
        newsletter_signup BOOLEAN NOT NULL DEFAULT FALSE,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS reservations (
        reservation_id SERIAL PRIMARY KEY,
        customer_id INTEGER NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
        time_slot TIMESTAMP NOT NULL,
        table_number INTEGER NOT NULL CHECK (table_number >= 1 AND table_number <= 30),
        num_guests INTEGER NOT NULL CHECK (num_guests > 0),
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (time_slot, table_number)
    );

    CREATE INDEX IF NOT EXISTS idx_reservations_time_slot ON reservations(time_slot);
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(ddl)
        conn.commit()
