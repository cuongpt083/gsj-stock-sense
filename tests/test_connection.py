"""
Kiểm thử Database Connection Manager (Phase 0).
"""
import sqlite3
import pytest
from src.database.connection import get_db_connection, transaction_scope


def test_get_db_connection():
    conn = get_db_connection()
    assert isinstance(conn, sqlite3.Connection)
    # Check foreign keys enabled
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys;")
    assert cursor.fetchone()[0] == 1
    conn.close()


def test_transaction_scope_commit():
    with transaction_scope() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM branches;")
        count = cursor.fetchone()[0]
        assert count >= 3


def test_transaction_scope_rollback_on_error():
    with pytest.raises(ValueError):
        with transaction_scope() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO branches (branch_id, branch_name) VALUES ('BR_TEST_TEMP', 'Test');")
            raise ValueError("Cố tình kích hoạt rollback")

    # Kiểm tra xem bản ghi đã bị rollback chưa
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM branches WHERE branch_id = 'BR_TEST_TEMP';")
    assert cursor.fetchone()[0] == 0
    conn.close()
