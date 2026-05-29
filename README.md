# Café Fausse

Full-stack web application for the fine-dining restaurant **Café Fausse**, built with React, Flask, and PostgreSQL.

## Project Structure

```
cafe/
├── backend/                 # Flask API + PostgreSQL integration
├── frontend/                # React (Vite) single-page application
│   └── public/images/menu/  # Dedicated image per menu item
├── scripts/                 # Utility scripts (menu image download)
└── MSEE_Web_Application_and_Interface_Design_Cafe_Fausse_Images/
```

## Features

- Six pages: Home, Menu, Reservations, Newsletter, About Us, Gallery
- Each menu item has its own food/beverage image
- Newsletter signup with email validation and database storage
- Reservation system with 30-table capacity per time slot
- Random table assignment for available slots
- Gallery lightbox, awards, and customer reviews
- Responsive layout using CSS Grid and Flexbox

## Prerequisites

- Node.js 18+
- Python 3.10+
- PostgreSQL 13+ running on `localhost`

## Environment Configuration

Copy and edit the backend environment file:

```bash
cp backend/.env.example backend/.env
```

Default values:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/cafe_fausse
FLASK_PORT=5000
```

Update `DATABASE_URL` if your PostgreSQL username, password, host, or database name differs.

---

## Deployment

### Windows

**1. Install PostgreSQL** and ensure the service is running on port `5432`.

**2. Backend setup**

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
python app.py
```

**3. Frontend setup** (new terminal)

```powershell
cd frontend
npm install
npm run dev
```

**Access**

- Local: `http://localhost:5173`
- External: `http://<server-ip>:5173`
- API: `http://<server-ip>:5000/api/health`

---

### Linux (Ubuntu / Debian)

**1. Install dependencies**

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nodejs npm postgresql postgresql-contrib
```

**2. Start PostgreSQL**

```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**3. Create database user (optional)**

If not using the default `postgres` user:

```bash
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"
```

**4. Backend setup**

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python init_db.py
python app.py
```

**5. Frontend setup** (new terminal)

```bash
cd frontend
npm install
npm run dev
```

**6. Open firewall ports (if needed)**

```bash
sudo ufw allow 5173/tcp
sudo ufw allow 5000/tcp
```

**Access**

- Local: `http://localhost:5173`
- External: `http://<server-ip>:5173`

---

### macOS

**1. Install dependencies with Homebrew**

```bash
brew install python node postgresql@16
brew services start postgresql@16
```

**2. Backend setup**

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python init_db.py
python app.py
```

**3. Frontend setup** (new terminal)

```bash
cd frontend
npm install
npm run dev
```

**Access**

- Local: `http://localhost:5173`
- External: `http://<server-ip>:5173`

---

## Production Build (All Platforms)

**Build frontend**

```bash
cd frontend
npm install
npm run build
npm run preview
```

Preview also binds to `0.0.0.0:5173` and proxies `/api` to Flask.

**Run backend for external access**

Both frontend (Vite) and backend (Flask) listen on `0.0.0.0` by default in this project.

```bash
cd backend
source venv/bin/activate   # Linux/macOS
# .\venv\Scripts\activate  # Windows
python app.py
```

---

## Menu Images

Each dish has a dedicated image under `frontend/public/images/menu/`:

| Image | Dish |
|-------|------|
| `bruschetta.jpg` | Bruschetta |
| `caesar-salad.jpg` | Caesar Salad |
| `grilled-salmon.jpg` | Grilled Salmon |
| `ribeye-steak.webp` | Ribeye Steak (project asset) |
| `vegetable-risotto.jpg` | Vegetable Risotto |
| `tiramisu.jpg` | Tiramisu |
| `cheesecake.jpg` | Cheesecake |
| `red-wine.jpg` | Red Wine |
| `white-wine.jpg` | White Wine |
| `craft-beer.jpg` | Craft Beer |
| `espresso.jpg` | Espresso |

Most images are AI-generated fine dining photography. To replace them with royalty-free Pexels photos:

```bash
python scripts/download_menu_images.py
```

See `frontend/public/images/menu/README.md` for details.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/newsletter` | Newsletter signup |
| `GET` | `/api/reservations/availability?time_slot=...` | Check table availability |
| `POST` | `/api/reservations` | Create reservation |

---

## Verify Database Changes

After submitting a newsletter signup or reservation in the UI:

```sql
SELECT * FROM customers;
SELECT * FROM reservations;
```

Or initialize manually with SQL:

```bash
psql -U postgres -f backend/init_db.sql
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Connection refused` on port 5432 | Start PostgreSQL service |
| External users cannot access site | Open firewall ports 5173 and 5000 |
| API calls fail from external browser | Ensure Flask is running on `0.0.0.0:5000` |
| `init_db.py` fails | Check `DATABASE_URL` credentials in `backend/.env` |
