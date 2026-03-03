# 🏛️ Campus Facility Booking System
**CPEN 412 – Web Software Architecture | University of Ghana**

A full-stack web application built with **MVC architecture** using Python/Flask (backend), SQLite (database), and Vanilla JS (frontend).

---

## MVC Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│  VIEW              │  CONTROLLER               │  MODEL              │
│  (Frontend)        │  (Flask Routes+Logic)     │  (SQLite Classes)   │
│                    │                           │                     │
│  public/           │  routes/                  │  models/            │
│  └─ index.html     │  ├─ facility_routes.py    │  ├─ facility.py     │
│                    │  ├─ booking_routes.py     │  ├─ booking.py      │
│  Vanilla JS        │  ├─ availability_routes   │  └─ user.py         │
│  (fetch API)       │  └─ user_routes.py        │                     │
│                    │                           │  config/            │
│                    │  controllers/             │  └─ database.py     │
│                    │  ├─ facility_controller   │                     │
│                    │  ├─ booking_controller    │                     │
│                    │  └─ availability_ctrl     │                     │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Quick Start (Local)

### Requirements
- Python 3.8+

### Install & Run
```bash
pip install -r requirements.txt
python app.py
# → http://localhost:5000
```

The SQLite database (`campus_booking.db`) is auto-created on first run with seed data:
- 6 facilities (Great Hall, Seminar Room, Computer Lab, etc.)
- 5 users (students, staff, admin)
- 3 initial bookings

---

## Project Structure

```
campus-booking/
├── app.py                        # Entry point – Flask app factory + CORS
├── requirements.txt              # flask, gunicorn
├── Procfile                      # For Render/Railway/Heroku
├── render.yaml                   # Render deploy config
├── config/
│   └── database.py               # SQLite connection + schema + seed data
├── models/                       # M – Data access layer (SQL)
│   ├── facility.py
│   ├── booking.py
│   └── user.py
├── controllers/                  # C – Business logic + validation
│   ├── facility_controller.py
│   ├── booking_controller.py
│   └── availability_controller.py
├── routes/                       # C – URL routing (Flask Blueprints)
│   ├── facility_routes.py
│   ├── booking_routes.py
│   ├── availability_routes.py
│   └── user_routes.py
└── public/                       # V – Frontend SPA
    └── index.html
```

---

## API Documentation

**Base URL:** `http://localhost:5000/api`

All responses: `{ "success": true/false, "data": ..., "error": "..." }`

---

### Facilities

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/facilities` | Get all facilities |
| GET | `/api/facilities/{id}` | Get facility by ID |
| POST | `/api/facilities` | Create a facility |
| PUT | `/api/facilities/{id}` | Update a facility |
| DELETE | `/api/facilities/{id}` | Delete a facility |

**POST/PUT body:**
```json
{ "name": "Lab C", "location": "Block C, 2nd Floor", "capacity": 45 }
```

**GET /api/facilities response:**
```json
{
  "success": true,
  "count": 6,
  "data": [
    { "id": 1, "name": "Great Hall", "location": "Main Campus, Block A", "capacity": 500 }
  ]
}
```

---

### Bookings

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/bookings` | Get all bookings (with facility + user info) |
| GET | `/api/bookings/{id}` | Get booking by ID |
| POST | `/api/bookings` | Create a booking (conflict-checked) |
| PUT | `/api/bookings/{id}` | Update a booking |
| DELETE | `/api/bookings/{id}` | Cancel a booking (soft delete) |
| DELETE | `/api/bookings/{id}/hard` | Permanently delete a booking |

**POST body:**
```json
{
  "facility_id": 2,
  "user_id": 1,
  "date": "2026-03-15",
  "start_time": "10:00",
  "end_time": "12:00",
  "status": "confirmed"
}
```

- Times are **automatically rounded** to nearest 30-minute slot.
- Returns `409 Conflict` if the slot overlaps an existing booking.

---

### Availability

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/availability?facility_id=1&date=2026-03-15` | Get 30-min slots |

**Response:**
```json
{
  "success": true,
  "facility": { "id": 1, "name": "Great Hall", ... },
  "date": "2026-03-15",
  "summary": { "total": 30, "available": 28, "booked": 2 },
  "slots": [
    { "start_time": "07:00", "end_time": "07:30", "available": true },
    { "start_time": "09:00", "end_time": "09:30", "available": false }
  ]
}
```

Slots span **07:00–22:00** in **30-minute increments** (30 slots/day).

---

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users` | Get all users |
| GET | `/api/users/{id}` | Get user by ID |
| POST | `/api/users` | Create user |

**POST body:**
```json
{ "name": "Ama Asante", "email": "ama@ug.edu.gh", "role": "student" }
```
Roles: `student | staff | admin`

---

## Database Schema

```sql
CREATE TABLE facilities (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT    NOT NULL,
    location TEXT    NOT NULL,
    capacity INTEGER NOT NULL
);

CREATE TABLE users (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name  TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    role  TEXT NOT NULL CHECK(role IN ('student','staff','admin'))
);

CREATE TABLE bookings (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    facility_id INTEGER NOT NULL REFERENCES facilities(id) ON DELETE CASCADE,
    user_id     INTEGER NOT NULL REFERENCES users(id)     ON DELETE CASCADE,
    date        TEXT    NOT NULL,
    start_time  TEXT    NOT NULL,
    end_time    TEXT    NOT NULL,
    status      TEXT    NOT NULL DEFAULT 'confirmed'
                        CHECK(status IN ('confirmed','cancelled','pending')),
    created_at  TEXT    DEFAULT (datetime('now'))
);
```

---

## Deployment Guide

### Option 1 – Render (Recommended, Free Tier)

1. Push this project to a GitHub repository.
2. Go to [render.com](https://render.com) → **New Web Service**.
3. Connect your GitHub repo.
4. Render will auto-detect the `render.yaml` and configure:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn app:app`
5. Click **Deploy**. Your app will be live at `https://campus-booking.onrender.com`.

> ⚠️ **SQLite note:** Render's free tier has an ephemeral filesystem — the database resets on each deploy. For persistent data, add a PostgreSQL database on Render (free tier available) and update `config/database.py` to use `psycopg2`.

---

### Option 2 – Railway (Free Tier)

1. Go to [railway.app](https://railway.app) → **New Project → Deploy from GitHub**.
2. Select your repo. Railway detects Python automatically.
3. Set the start command to `gunicorn app:app` in Settings.
4. Done — Railway provides a public URL.

---

### ⚠️ Why Vercel Does NOT Work for This Project

Vercel is a **serverless/static** platform optimised for Node.js and frontend frameworks. It does **not** support:
- Long-running Python WSGI servers (gunicorn)
- Persistent file storage (SQLite writes)
- Flask server-side rendering in the traditional sense

**Use Render or Railway instead** — both have free tiers and are designed for full-stack Python apps.

If you insist on Vercel, you would need to:
1. Replace SQLite with an external DB (e.g. PlanetScale, Supabase, or Neon — all free tiers).
2. Rewrite the backend as Vercel Serverless Functions (`api/` folder).
3. Host the frontend separately or as a static site.
This is a significant rewrite and not recommended for this project.

---

*Group: [Your Group Number] | CPEN 412, 2026*
