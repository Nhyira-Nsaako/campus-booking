from config.database import get_connection

class Facility:
    """Model layer – all SQL for the facilities table lives here."""

    @staticmethod
    def get_all():
        conn = get_connection()
        rows = conn.execute("SELECT * FROM facilities ORDER BY id").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_id(facility_id):
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM facilities WHERE id = ?", (facility_id,)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def create(name, location, capacity):
        conn = get_connection()
        cursor = conn.execute(
            "INSERT INTO facilities (name, location, capacity) VALUES (?,?,?)",
            (name, location, capacity)
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return Facility.get_by_id(new_id)

    @staticmethod
    def update(facility_id, name, location, capacity):
        conn = get_connection()
        conn.execute(
            "UPDATE facilities SET name=?, location=?, capacity=? WHERE id=?",
            (name, location, capacity, facility_id)
        )
        conn.commit()
        conn.close()
        return Facility.get_by_id(facility_id)

    @staticmethod
    def delete(facility_id):
        conn = get_connection()
        affected = conn.execute(
            "DELETE FROM facilities WHERE id=?", (facility_id,)
        ).rowcount
        conn.commit()
        conn.close()
        return affected > 0
