"""Initialize PostgreSQL database and tables for Café Fausse."""

import os
import sys

import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/cafe_fausse",
)


def parse_database_url(url):
    # postgresql://user:password@host:port/dbname
    if not url.startswith("postgresql://"):
        raise ValueError("DATABASE_URL must use postgresql:// scheme")

    without_scheme = url[len("postgresql://") :]
    credentials, host_part = without_scheme.split("@", 1)
    user, password = credentials.split(":", 1)
    host_port, dbname = host_part.split("/", 1)
    host, port = host_port.split(":", 1)
    return {
        "user": user,
        "password": password,
        "host": host,
        "port": port,
        "dbname": dbname,
    }


def create_database_if_needed(config):
    admin_config = config.copy()
    target_db = admin_config.pop("dbname")
    admin_config["dbname"] = "postgres"

    with psycopg2.connect(**admin_config) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (target_db,))
            exists = cur.fetchone()
            if not exists:
                cur.execute(f'CREATE DATABASE "{target_db}"')
                print(f"Created database: {target_db}")
            else:
                print(f"Database already exists: {target_db}")


def create_tables(config):
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
    with psycopg2.connect(**config) as conn:
        with conn.cursor() as cur:
            cur.execute(ddl)
        conn.commit()
    print("Tables initialized successfully.")


def main():
    try:
        config = parse_database_url(DATABASE_URL)
        create_database_if_needed(config)
        create_tables(config)
    except Exception as exc:
        print(f"Database initialization failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
