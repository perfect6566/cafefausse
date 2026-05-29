# Café Fausse

Full-stack web application for the fine-dining restaurant **Café Fausse**, built with React, Flask, and PostgreSQL.

## Project Structure

```
cafe/
├── backend/          # Flask API + PostgreSQL integration
├── frontend/         # React (Vite) single-page application
└── MSEE_Web_Application_and_Interface_Design_Cafe_Fausse_Images/
```

## Features

- Five pages: Home, Menu, Reservations, Newsletter, About Us, Gallery
- Newsletter signup with email validation and database storage
- Reservation system with 30-table capacity per time slot
- Random table assignment for available slots
- Gallery lightbox, awards, and customer reviews
- Responsive layout using CSS Grid and Flexbox

## Prerequisites

- Node.js 18+
- Python 3.10+
- PostgreSQL running on `localhost`

## Database Setup

1. Ensure PostgreSQL is running locally.
2. Update credentials in `backend/.env` if needed:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/cafe_fausse
FLASK_PORT=5000
```

3. Initialize the database:

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
```

Alternatively, run `backend/init_db.sql` manually with `psql`.

## Run Backend

```bash
cd backend
venv\Scripts\activate
python app.py
```

API base URL: `http://localhost:5000`

## Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend URL: `http://localhost:5173` (also reachable externally via `http://<your-server-ip>:5173`)

The Vite dev server proxies `/api/*` requests to Flask.

## API Endpoints

- `GET /api/health`
- `POST /api/newsletter`
- `GET /api/reservations/availability?time_slot=YYYY-MM-DDTHH:MM:SS`
- `POST /api/reservations`

## Verify Database Changes

After submitting a newsletter signup or reservation in the UI, inspect PostgreSQL:

```sql
SELECT * FROM customers;
SELECT * FROM reservations;
```

## Build Frontend for Production

```bash
cd frontend
npm run build
npm run preview
```
