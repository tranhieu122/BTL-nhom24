"""SQLite-backed booking repository."""
from __future__ import annotations
import sqlite3
from models.booking import Booking
from database.sqlite_db import get_connection


def _row_to_booking(row: sqlite3.Row) -> Booking:
    return Booking(
        booking_id=row["id"],
        user_id=row["user_id"],
        user_name=row["user_name"],
        room_id=row["room_id"],
        booking_date=row["booking_date"],
        slot=row["slot"],
        purpose=row["purpose"],
        status=row["status"],
    )


class BookingDAO:
    def list_all(self) -> list[Booking]:
        conn = get_connection()
        rows = conn.execute("SELECT * FROM bookings ORDER BY booking_date DESC, id").fetchall()
        return [_row_to_booking(r) for r in rows]

    def find_by_id(self, booking_id: str) -> Booking | None:
        conn = get_connection()
        row = conn.execute("SELECT * FROM bookings WHERE id=?", (booking_id,)).fetchone()
        return _row_to_booking(row) if row else None

    def find_by_user(self, user_id: str) -> list[Booking]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM bookings WHERE user_id=? ORDER BY booking_date DESC",
            (user_id,),
        ).fetchall()
        return [_row_to_booking(r) for r in rows]

    def save(self, booking: Booking) -> Booking:
        conn = get_connection()
        conn.execute(
            """
            INSERT INTO bookings (id,user_id,user_name,room_id,booking_date,slot,purpose,status)
            VALUES (?,?,?,?,?,?,?,?)
            ON CONFLICT(id) DO UPDATE SET
                user_id=excluded.user_id,
                user_name=excluded.user_name,
                room_id=excluded.room_id,
                booking_date=excluded.booking_date,
                slot=excluded.slot,
                purpose=excluded.purpose,
                status=excluded.status
            """,
            (booking.booking_id, booking.user_id, booking.user_name,
             booking.room_id, booking.booking_date, booking.slot,
             booking.purpose, booking.status),
        )
        conn.commit()
        return booking

    def delete(self, booking_id: str) -> None:
        conn = get_connection()
        conn.execute("DELETE FROM bookings WHERE id=?", (booking_id,))
        conn.commit()
