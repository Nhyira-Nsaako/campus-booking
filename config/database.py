import sqlite3, os, hashlib

DB_PATH = os.environ.get(
    "DATABASE_PATH",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "campus_booking.db")
)

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def _hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16).hex()
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{hashed}"

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS facilities (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            location    TEXT    NOT NULL,
            capacity    INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            email         TEXT    NOT NULL UNIQUE,
            role          TEXT    NOT NULL CHECK(role IN ('student','staff','admin')),
            password_hash TEXT
        );

        CREATE TABLE IF NOT EXISTS bookings (
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
    """)

    # Add password_hash column if upgrading from old schema
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
        conn.commit()
    except Exception:
        pass  # column already exists

    cursor.execute("SELECT COUNT(*) FROM facilities")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO facilities (name, location, capacity) VALUES (?,?,?)",
            [
                ("Great Hall",         "Main Campus, Block A",        500),
                ("Seminar Room 101",   "Engineering Block, 1st Floor", 40),
                ("Computer Lab 3",     "ICT Centre, 2nd Floor",        60),
                ("Conference Room B",  "Admin Block, Ground Floor",    20),
                ("Sports Pavilion",    "Sports Complex",              200),
                ("Library Study Hall", "Central Library, 3rd Floor",   80),
            ]
        )

    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        seed_users = [
            ("Kwame Mensah",  "kwame.mensah@ug.edu.gh",  "student", "student123"),
            ("Ama Asante",    "ama.asante@ug.edu.gh",    "staff",   "staff123"),
            ("Kofi Boateng",  "kofi.boateng@ug.edu.gh",  "admin",   "admin123"),
            ("Abena Ofori",   "abena.ofori@ug.edu.gh",   "student", "student123"),
            ("Yaw Darko",     "yaw.darko@ug.edu.gh",     "student", "student123"),
        ]
        cursor.executemany(
            "INSERT INTO users (name, email, role, password_hash) VALUES (?,?,?,?)",
            [(n, e, r, _hash_password(p)) for n, e, r, p in seed_users]
        )

    cursor.execute("SELECT COUNT(*) FROM bookings")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO bookings (facility_id, user_id, date, start_time, end_time, status) VALUES (?,?,?,?,?,?)",
            [
                (1, 1, "2026-02-25", "09:00", "11:00", "confirmed"),
                (2, 2, "2026-02-25", "13:00", "14:30", "confirmed"),
                (3, 3, "2026-02-26", "08:00", "10:00", "pending"),
            ]
        )

    conn.commit()
    conn.close()
    print("[DB] Database initialised successfully.")
