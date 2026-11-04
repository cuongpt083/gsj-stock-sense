"""
Module quản lý kết nối và transaction cho cơ sở dữ liệu SQLite Stock Sense.
"""
import os
import sqlite3
from contextlib import contextmanager

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
DB_PATH = os.path.join(DATA_DIR, "kiotviet_electronics.db")


def get_db_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Khởi tạo kết nối SQLite với cấu hình Row Factory và Foreign Keys."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


@contextmanager
def transaction_scope(db_path: str = DB_PATH):
    """Context manager hỗ trợ transaction tự động commit/rollback."""
    conn = get_db_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
