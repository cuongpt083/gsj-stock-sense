"""
Kiểm thử cấu trúc cơ sở dữ liệu và dữ liệu giả lập (Phase 0 TDD).
"""
import os
import sqlite3
import pytest

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
DB_PATH = os.path.join(DATA_DIR, "kiotviet_electronics.db")


@pytest.fixture(scope="function")
def db_connection():
    assert os.path.exists(DB_PATH), f"Database file not found at {DB_PATH}"
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    yield conn
    conn.close()


def test_required_tables_exist(db_connection):
    """Kiểm tra sự tồn tại của tất cả các bảng cốt lõi theo đặc tả SRS."""
    required_tables = [
        "branches",
        "inventories",
        "inventory_reservations",
        "purchase_orders",
        "po_items",
        "DIM_PRODUCTS",
        "DIM_CUSTOMERS",
        "FACT_ORDERS",
    ]
    cursor = db_connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    existing_tables = {row[0] for row in cursor.fetchall()}

    for table in required_tables:
        assert table in existing_tables, f"Bảng '{table}' chưa tồn tại trong database!"


def test_foreign_key_integrity(db_connection):
    """Kiểm tra tính toàn vẹn của các khóa ngoại (Foreign Keys)."""
    cursor = db_connection.cursor()
    cursor.execute("PRAGMA foreign_key_check;")
    errors = cursor.fetchall()
    assert len(errors) == 0, f"Phát hiện lỗi khóa ngoại trong DB: {errors}"


def test_atp_consistency_in_inventories(db_connection):
    """Kiểm tra tính nhất quán của cột ATP: atp_qty = on_hand_qty - reserved_qty."""
    cursor = db_connection.cursor()
    cursor.execute("""
        SELECT inventory_id, on_hand_qty, reserved_qty, atp_qty 
        FROM inventories 
        WHERE atp_qty != (on_hand_qty - reserved_qty)
    """)
    inconsistent_rows = cursor.fetchall()
    assert len(inconsistent_rows) == 0, f"Có bản ghi tồn kho bị sai lệch ATP: {inconsistent_rows}"


def test_synthetic_data_scale_and_scenarios(db_connection):
    """Kiểm tra quy mô dữ liệu giả lập và các kịch bản thực tế (3 chi nhánh, >=50 SP, đơn trả góp treo > 48h)."""
    cursor = db_connection.cursor()

    # 1. Tối thiểu 3 chi nhánh
    cursor.execute("SELECT COUNT(*) FROM branches WHERE is_active = 1;")
    branch_count = cursor.fetchone()[0]
    assert branch_count >= 3, f"Số lượng chi nhánh cần >= 3, thực tế có {branch_count}"

    # 2. Tối thiểu 50 sản phẩm điện máy
    cursor.execute("SELECT COUNT(*) FROM DIM_PRODUCTS WHERE is_active = 1;")
    product_count = cursor.fetchone()[0]
    assert product_count >= 50, f"Số lượng sản phẩm cần >= 50, thực tế có {product_count}"

    # 3. Có bản ghi giữ hàng cho đơn trả góp bị quá hạn (> 48 giờ)
    cursor.execute("""
        SELECT COUNT(*) FROM inventory_reservations 
        WHERE reservation_type = 'INSTALLMENT_HOLD' 
        AND status = 'ACTIVE' 
        AND expires_at < DATETIME('now', 'localtime')
    """)
    expired_reservations = cursor.fetchone()[0]
    assert expired_reservations > 0, "Cần có ít nhất 1 bản ghi đơn trả góp quá hạn 48h để phục vụ kiểm thử Auto-Release!"
