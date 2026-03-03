from config.database import get_connection

class Booking:
    """Model layer – all SQL for the bookings table lives here."""

    @staticmethod
    def get_all():
        conn = get_connection()
        rows = conn.execute("""
            SELECT b.*,
                   f.name     AS facility_name,
                   f.location AS facility_location,
                   u.name     AS user_name,
                   u.email    AS user_email
            FROM bookings b
            JOIN facilities f ON f.id = b.facility_id
            JOIN users      u ON u.id = b.user_id
            ORDER BY b.date DESC, b.start_time
        """).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_by_id(booking_id):
        conn = get_connection()
        row = conn.execute("""
            SELECT b.*,
                   f.name     AS facility_name,
                   f.location AS facility_location,
                   u.name     AS user_name,
                   u.email    AS user_email
            FROM bookings b
            JOIN facilities f ON f.id = b.facility_id
            JOIN users      u ON u.id = b.user_id
            WHERE b.id = ?
        """, (booking_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_conflicts(facility_id, date, start_time, end_time, exclude_id=None):
        """Return active bookings that overlap with the given slot."""
        conn = get_connection()
        query = """
            SELECT * FROM bookings
            WHERE facility_id = ?
              AND date = ?
              AND status != 'cancelled'
              AND start_time < ?
              AND end_time   > ?
        """
        params = [facility_id, date, end_time, start_time]
        if exclude_id:
            query += " AND id != ?"
            params.append(exclude_id)
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_booked_slots(facility_id, date):
        """Return all non-cancelled bookings for a facility on a specific date."""
        conn = get_connection()
        rows = conn.execute("""
            SELECT start_time, end_time, status
            FROM bookings
            WHERE facility_id = ? AND date = ? AND status != 'cancelled'
            ORDER BY start_time
        """, (facility_id, date)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def create(facility_id, user_id, date, start_time, end_time, status="confirmed"):
        conn = get_connection()
        cursor = conn.execute("""
            INSERT INTO bookings (facility_id, user_id, date, start_time, end_time, status)
            VALUES (?,?,?,?,?,?)
        """, (facility_id, user_id, date, start_time, end_time, status))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return Booking.get_by_id(new_id)

    @staticmethod
    def update(booking_id, **fields):
        allowed = {"facility_id", "user_id", "date", "start_time", "end_time", "status"}
        updates = {k: v for k, v in fields.items() if k in allowed and v is not None}
        if not updates:
            return Booking.get_by_id(booking_id)
        set_clause = ", ".join(f"{k}=?" for k in updates)
        conn = get_connection()
        conn.execute(
            f"UPDATE bookings SET {set_clause} WHERE id=?",
            (*updates.values(), booking_id)
        )
        conn.commit()
        conn.close()
        return Booking.get_by_id(booking_id)

    @staticmethod
    def delete(booking_id):
        conn = get_connection()
        affected = conn.execute(
            "DELETE FROM bookings WHERE id=?", (booking_id,)
        ).rowcount
        conn.commit()
        conn.close()
        return affected > 0

    @staticmethod
    def cancel(booking_id):
        conn = get_connection()
        conn.execute(
            "UPDATE bookings SET status='cancelled' WHERE id=?", (booking_id,)
        )
        conn.commit()
        conn.close()
        return Booking.get_by_id(booking_id)
