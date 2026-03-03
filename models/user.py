import hashlib, os
from config.database import get_connection

def _hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16).hex()
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{hashed}"

def _verify_password(password, stored):
    try:
        salt, hashed = stored.split(":", 1)
        return hashlib.sha256((salt + password).encode()).hexdigest() == hashed
    except Exception:
        return False

class User:
    """Model layer – all SQL for the users table lives here."""

    @staticmethod
    def get_all():
        conn = get_connection()
        rows = conn.execute("SELECT id, name, email, role FROM users ORDER BY id").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_id(user_id):
        conn = get_connection()
        row = conn.execute(
            "SELECT id, name, email, role FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_by_email(email):
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def create(name, email, role, password=None):
        conn = get_connection()
        password_hash = _hash_password(password) if password else None
        cursor = conn.execute(
            "INSERT INTO users (name, email, role, password_hash) VALUES (?,?,?,?)",
            (name, email, role, password_hash)
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return User.get_by_id(new_id)

    @staticmethod
    def verify_login(email, password):
        """Returns user dict (without password_hash) if credentials valid, else None."""
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        conn.close()
        if not row:
            return None
        row = dict(row)
        stored = row.get("password_hash") or ""
        if not stored or not _verify_password(password, stored):
            return None
        return {k: v for k, v in row.items() if k != "password_hash"}
