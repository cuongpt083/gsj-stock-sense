"""
Khởi tạo cơ sở dữ liệu SQLite bán hàng điện máy tương thích KiotViet.
Thực thi schema DDL và nạp dữ liệu kiểm thử (seed data).
"""
import sqlite3
import os
import sys

# Đảm bảo in unicode tiếng Việt an toàn trên console Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(DATA_DIR, "schema.sql")
DB_PATH = os.path.join(DATA_DIR, "kiotviet_electronics.db")

def init_database():
    # Xóa file db cũ nếu có để đảm bảo tính nhất quán khi khởi tạo lại
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    # Đọc và thực thi file DDL
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)

    cursor = conn.cursor()

    # 1. Nạp dữ liệu DIM_CUSTOMERS (Khách hàng)
    customers = [
        ('KH00001', 'Cá nhân', 'Nguyễn Văn An', '0901234567', 'an.nguyen@email.com', '123 Hoàng Diệu', 'Đà Nẵng - Hải Châu', 'Phước Ninh', None, None, '048098001234', 28500000.0, 0.0, 1),
        ('KH00002', 'Cá nhân', 'Trần Thị Bích', '0912345678', 'bich.tran@email.com', '45 Lê Duẩn', 'Đà Nẵng - Thanh Khê', 'Tân Chính', None, None, '048195002345', 18900000.0, 0.0, 1),
        ('KH00003', 'Doanh nghiệp', 'Công ty Cổ phần Công nghệ Alpha', '02363888999', 'account@alpha-tech.vn', '88 Nguyễn Văn Linh', 'Đà Nẵng - Hải Châu', 'Nam Dương', 'Công ty Cổ phần Công nghệ Alpha', '0401889977', None, 45000000.0, 0.0, 1),
        ('KH00004', 'Cá nhân', 'Lê Hoàng Nam', '0988776655', 'nam.le@email.com', '210 Điện Biên Phủ', 'Đà Nẵng - Thanh Khê', 'Chính Gián', None, None, '048092003456', 0.0, 0.0, 1),
        ('KH00005', 'Cá nhân', 'Phạm Quỳnh Như', '0977665544', 'nhu.pham@email.com', '15 Trần Phú', 'Đà Nẵng - Hải Châu', 'Thạch Thang', None, None, '048197004567', 0.0, 0.0, 1)
    ]
    cursor.executemany("""
        INSERT INTO DIM_CUSTOMERS (customer_code, customer_type, customer_name, phone, email, address, area, ward, company, tax_code, identity_card, total_sales, current_debt, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, customers)

    # 2. Nạp dữ liệu DIM_EMPLOYEES (Nhân viên)
    employees = [
        ('NV0001', 'Võ Quốc Huy', '0905111222', 'Kinh doanh', 'Chuyên viên Bán hàng Điện máy', 'huy.vq', 'Showroom Đà Nẵng', 9000000.0, 1),
        ('NV0002', 'Lê Thanh Mai', '0905222333', 'Kinh doanh', 'Chuyên viên Bán hàng Điện tử', 'mai.lt', 'Showroom Đà Nẵng', 8500000.0, 1),
        ('NV0003', 'Nguyễn Đức Thắng', '0905333444', 'Kỹ thuật', 'Kỹ thuật viên Lắp đặt & Bảo hành', 'thang.nd', 'Showroom Đà Nẵng', 10500000.0, 1),
        ('NV0004', 'Đặng Tuấn Khang', '0905444555', 'Kho', 'Thủ kho Điện máy', 'khang.dt', 'Showroom Đà Nẵng', 8000000.0, 1)
    ]
    cursor.executemany("""
        INSERT INTO DIM_EMPLOYEES (employee_code, employee_name, phone, department, title, login, branch_working, salary_base, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, employees)

    # 3. Nạp dữ liệu DIM_PRODUCTS (Hàng hóa điện máy)
    products = [
        ('SP_DK_FTKC', '8936001001', 'Hàng hóa', 'Điện lạnh > Máy lạnh > Inverter', 'Máy lạnh Daikin Inverter 1.5 HP FTKC35UVMV', 'Daikin', 'FTKC35UVMV', 'Bộ', 9200000.0, 12500000.0, 24, 24, 1, 1, 1),
        ('SP_SN_XR65', '8936001002', 'Hàng hóa', 'Điện tử > Tivi > Smart Tivi 4K', 'Smart Tivi Sony Bravia OLED 4K 65 inch XR-65A80L', 'Sony', 'XR-65A80L', 'Chiếc', 24000000.0, 28500000.0, 14, 24, 1, 1, 1),
        ('SP_LG_FV14', '8936001003', 'Hàng hóa', 'Điện gia dụng > Máy giặt > Cửa trước', 'Máy giặt LG AI DD Inverter 10 kg FV1410S4P', 'LG', 'FV1410S4P', 'Chiếc', 7800000.0, 10200000.0, 20, 24, 1, 1, 1),
        ('SP_PA_CW53', '8936001004', 'Hàng hóa', 'Điện lạnh > Tủ lạnh > 2 Cánh Inverter', 'Tủ lạnh Panasonic Inverter 495 lít NR-CW530XMMV', 'Panasonic', 'NR-CW530XMMV', 'Chiếc', 26000000.0, 31900000.0, 9, 36, 1, 1, 1),
        ('SP_SS_S24U', '8936001005', 'Hàng hóa', 'Công nghệ > Điện thoại > Smartphone', 'Samsung Galaxy S24 Ultra 256GB Titanium Gray', 'Samsung', 'SM-S928B', 'Chiếc', 22500000.0, 27990000.0, 30, 12, 1, 1, 1),
        ('SP_SH_KS18', '8936001006', 'Hàng hóa', 'Gia dụng nhà bếp > Nồi cơm điện', 'Nồi cơm điện tử Sharp 1.8L KS-COM18V', 'Sharp', 'KS-COM18V', 'Cái', 850000.0, 1290000.0, 50, 12, 0, 1, 1)
    ]
    cursor.executemany("""
        INSERT INTO DIM_PRODUCTS (product_code, barcode, product_type, category_path, product_name, brand, model, uom, cost_price, sale_price, stock_on_hand, warranty_months, has_serial_tracking, is_active, is_direct_sale)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, products)

    # 4. Nạp dữ liệu DIM_PRODUCT_SERIALS (Serial/IMEI từng máy)
    serials = [
        ('SN_DK_2026_001', 'SP_DK_FTKC', 'SOLD', '2026-09-01 08:30:00'),
        ('SN_DK_2026_002', 'SP_DK_FTKC', 'IN_STOCK', '2026-09-01 08:30:00'),
        ('SN_DK_2026_003', 'SP_DK_FTKC', 'IN_STOCK', '2026-09-01 08:30:00'),
        ('SN_SN_2026_001', 'SP_SN_XR65', 'SOLD', '2026-09-05 09:15:00'),
        ('SN_SN_2026_002', 'SP_SN_XR65', 'IN_STOCK', '2026-09-05 09:15:00'),
        ('SN_LG_2026_001', 'SP_LG_FV14', 'IN_STOCK', '2026-09-10 10:00:00'),
        ('SN_LG_2026_002', 'SP_LG_FV14', 'IN_STOCK', '2026-09-10 10:00:00'),
        ('SN_PA_2026_001', 'SP_PA_CW53', 'SOLD', '2026-09-12 14:20:00'),
        ('SN_PA_2026_002', 'SP_PA_CW53', 'IN_STOCK', '2026-09-12 14:20:00'),
        ('SN_SS_2026_001', 'SP_SS_S24U', 'IN_STOCK', '2026-09-15 11:00:00')
    ]
    cursor.executemany("""
        INSERT INTO DIM_PRODUCT_SERIALS (serial_number, product_code, status, import_date)
        VALUES (?, ?, ?, ?)
    """, serials)

    # 5. Nạp dữ liệu FACT_ORDERS & FACT_ORDER_LINES (Đơn đặt hàng)
    orders = [
        ('DH00001', '2026-10-01 10:15:00', 'KH00001', 'NV0001', 28500000.0, 5000000.0, 23500000.0, 'Hoàn thành', 'Khách hẹn giao buổi chiều'),
        ('DH00002', '2026-10-05 14:30:00', 'KH00002', 'NV0002', 12500000.0, 2000000.0, 10500000.0, 'Hoàn thành', 'Giao kèm vật tư lắp đặt')
    ]
    cursor.executemany("""
        INSERT INTO FACT_ORDERS (order_code, order_time, customer_code, seller_code, total_amount, deposit_amount, amount_due, status, note)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, orders)

    order_lines = [
        (1, 'DH00001', 'SP_SN_XR65', 1, 28500000.0, 0.0, 28500000.0),
        (2, 'DH00002', 'SP_DK_FTKC', 1, 12500000.0, 0.0, 12500000.0)
    ]
    cursor.executemany("""
        INSERT INTO FACT_ORDER_LINES (order_line_id, order_code, product_code, quantity, unit_price, discount_amount, line_total)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, order_lines)

    # 6. Nạp dữ liệu FACT_INVOICES & FACT_INVOICE_LINES (Hóa đơn bán hàng chuẩn tiền tố HDIP)
    invoices = [
        ('HDIP00001', '2026-10-01 16:30:00', 'DH00001', 'KH00001', 'NV0001', 'NV0003', 'Showroom Đà Nẵng', 28500000.0, 0.0, 28500000.0, 5000000.0, 0.0, 23500000.0, 0.0, 'Đã lắp đặt nghiệm thu Tivi OLED'),
        ('HDIP00002', '2026-10-05 17:00:00', 'DH00002', 'KH00002', 'NV0002', 'NV0003', 'Showroom Đà Nẵng', 12500000.0, 500000.0, 12000000.0, 2000000.0, 10000000.0, 0.0, 0.0, 'Khuyến mãi giảm 500k máy lạnh'),
        ('HDIP00003', '2026-10-08 11:20:00', None, 'KH00003', 'NV0001', 'NV0003', 'Bán trực tiếp', 31900000.0, 0.0, 31900000.0, 0.0, 0.0, 31900000.0, 0.0, 'Xuất VAT công ty tủ lạnh cao cấp')
    ]
    cursor.executemany("""
        INSERT INTO FACT_INVOICES (invoice_code, invoice_time, order_code, customer_code, seller_code, technician_code, sales_channel, total_gross_amount, invoice_discount_amount, total_net_amount, pay_cash, pay_card, pay_transfer, pay_installment, note)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, invoices)

    invoice_lines = [
        (1, 'HDIP00001', 'SP_SN_XR65', 'SN_SN_2026_001', 1, 28500000.0, 0.0, 28500000.0, '2028-10-01'),
        (2, 'HDIP00002', 'SP_DK_FTKC', 'SN_DK_2026_001', 1, 12500000.0, 500000.0, 12000000.0, '2028-10-05'),
        (3, 'HDIP00003', 'SP_PA_CW53', 'SN_PA_2026_001', 1, 31900000.0, 0.0, 31900000.0, '2029-10-08')
    ]
    cursor.executemany("""
        INSERT INTO FACT_INVOICE_LINES (invoice_line_id, invoice_code, product_code, serial_number, quantity, unit_price, line_discount_amount, line_total, warranty_expire_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, invoice_lines)

    conn.commit()

    # Kiểm tra ràng buộc khóa ngoại (Foreign Key integrity)
    fk_errors = list(conn.execute("PRAGMA foreign_key_check;"))
    if fk_errors:
        print("[!] Phát hiện lỗi khóa ngoại:", fk_errors)
    else:
        print("[+] Kiểm tra ràng buộc khóa ngoại (Foreign Keys): HỢP LỆ 100%")

    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';").fetchall()]
    views = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='view';").fetchall()]

    print(f"[+] Đã tạo thành công cơ sở dữ liệu tại: {DB_PATH}")
    print(f"    - Danh sách bảng ({len(tables)}): {', '.join(tables)}")
    print(f"    - Danh sách views ({len(views)}): {', '.join(views)}")

    # In thử kết quả từ VIEW_BRAND_PERFORMANCE
    print("\n--- DỮ LIỆU KIỂM THỬ: VIEW_BRAND_PERFORMANCE ---")
    rows = conn.execute("SELECT brand, total_invoices, total_units_sold, total_revenue, gross_profit FROM VIEW_BRAND_PERFORMANCE;").fetchall()
    for row in rows:
        print(f"Thương hiệu: {row[0]:<12} | Số HĐ: {row[1]} | SL bán: {row[2]} | Doanh thu: {row[3]:>12,.0f} VND | Lợi nhuận gộp: {row[4]:>12,.0f} VND")

    conn.close()

if __name__ == "__main__":
    init_database()
