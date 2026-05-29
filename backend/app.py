import random
import re
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS
from psycopg2 import IntegrityError

from config import TOTAL_TABLES
from database import get_connection, init_db

app = Flask(__name__)
CORS(app)

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def validate_email(email):
    return bool(email and EMAIL_PATTERN.match(email.strip()))


def parse_time_slot(value):
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError as exc:
        raise ValueError("Invalid time slot format. Use ISO format.") from exc


def is_valid_business_hour(slot):
    weekday = slot.weekday()
    hour = slot.hour
    minute = slot.minute

    if minute not in (0, 30):
        return False

    if weekday == 6:
        return 17 <= hour < 21 or (hour == 21 and minute == 0)

    return 17 <= hour < 23 or (hour == 23 and minute == 0)


def get_taken_tables(cur, time_slot):
    cur.execute(
        "SELECT table_number FROM reservations WHERE time_slot = %s",
        (time_slot,),
    )
    return {row["table_number"] for row in cur.fetchall()}


def upsert_customer(cur, name, email, phone=None, newsletter=False):
    cur.execute(
        """
        INSERT INTO customers (customer_name, email_address, phone_number, newsletter_signup)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (email_address)
        DO UPDATE SET
            customer_name = EXCLUDED.customer_name,
            phone_number = COALESCE(EXCLUDED.phone_number, customers.phone_number),
            newsletter_signup = customers.newsletter_signup OR EXCLUDED.newsletter_signup
        RETURNING customer_id, customer_name, email_address, phone_number, newsletter_signup
        """,
        (name.strip(), email.strip().lower(), phone.strip() if phone else None, newsletter),
    )
    return cur.fetchone()


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/api/newsletter")
def newsletter_signup():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    name = (data.get("name") or "Newsletter Subscriber").strip()

    if not validate_email(email):
        return jsonify({"success": False, "message": "Please enter a valid email address."}), 400

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                customer = upsert_customer(cur, name, email, newsletter=True)
            conn.commit()

        return jsonify(
            {
                "success": True,
                "message": "Thank you for subscribing to our newsletter!",
                "customer": customer,
            }
        )
    except Exception:
        return jsonify({"success": False, "message": "Unable to save subscription. Please try again."}), 500


@app.get("/api/reservations/availability")
def reservation_availability():
    time_slot_raw = request.args.get("time_slot")
    if not time_slot_raw:
        return jsonify({"success": False, "message": "time_slot is required."}), 400

    try:
        time_slot = parse_time_slot(time_slot_raw)
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400

    if not is_valid_business_hour(time_slot):
        return jsonify({"success": False, "message": "Selected time is outside business hours."}), 400

    with get_connection() as conn:
        with conn.cursor() as cur:
            taken = get_taken_tables(cur, time_slot)

    available = TOTAL_TABLES - len(taken)
    return jsonify(
        {
            "success": True,
            "time_slot": time_slot.isoformat(),
            "available_tables": available,
            "is_available": available > 0,
        }
    )


@app.post("/api/reservations")
def create_reservation():
    data = request.get_json(silent=True) or {}

    name = (data.get("customer_name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    phone = (data.get("phone_number") or "").strip()
    time_slot_raw = data.get("time_slot")
    num_guests = data.get("num_guests")

    if not name:
        return jsonify({"success": False, "message": "Customer name is required."}), 400
    if not validate_email(email):
        return jsonify({"success": False, "message": "Please enter a valid email address."}), 400
    if not time_slot_raw:
        return jsonify({"success": False, "message": "Please select a time slot."}), 400

    try:
        num_guests = int(num_guests)
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Number of guests must be a valid number."}), 400

    if num_guests < 1 or num_guests > 12:
        return jsonify({"success": False, "message": "Number of guests must be between 1 and 12."}), 400

    try:
        time_slot = parse_time_slot(time_slot_raw)
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400

    if not is_valid_business_hour(time_slot):
        return jsonify({"success": False, "message": "Selected time is outside business hours."}), 400

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                taken = get_taken_tables(cur, time_slot)
                if len(taken) >= TOTAL_TABLES:
                    return jsonify(
                        {
                            "success": False,
                            "message": "This time slot is fully booked. Please choose another time.",
                        }
                    ), 409

                available_tables = [table for table in range(1, TOTAL_TABLES + 1) if table not in taken]
                table_number = random.choice(available_tables)

                customer = upsert_customer(cur, name, email, phone=phone or None, newsletter=False)
                cur.execute(
                    """
                    INSERT INTO reservations (customer_id, time_slot, table_number, num_guests)
                    VALUES (%s, %s, %s, %s)
                    RETURNING reservation_id, time_slot, table_number, num_guests
                    """,
                    (customer["customer_id"], time_slot, table_number, num_guests),
                )
                reservation = cur.fetchone()
            conn.commit()

        return jsonify(
            {
                "success": True,
                "message": (
                    f"Reservation confirmed for {name} on "
                    f"{time_slot.strftime('%A, %B %d, %Y at %I:%M %p')}. "
                    f"Table {table_number} has been assigned."
                ),
                "reservation": {
                    "reservation_id": reservation["reservation_id"],
                    "customer_name": customer["customer_name"],
                    "email": customer["email_address"],
                    "phone_number": customer["phone_number"],
                    "time_slot": reservation["time_slot"].isoformat(),
                    "table_number": reservation["table_number"],
                    "num_guests": reservation["num_guests"],
                },
            }
        )
    except IntegrityError:
        return jsonify(
            {
                "success": False,
                "message": "This time slot is fully booked. Please choose another time.",
            }
        ), 409
    except Exception:
        return jsonify({"success": False, "message": "Unable to create reservation. Please try again."}), 500


if __name__ == "__main__":
    init_db()
    from config import FLASK_PORT

    app.run(debug=True, port=FLASK_PORT)
