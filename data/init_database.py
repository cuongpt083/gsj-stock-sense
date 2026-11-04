"""
Khởi tạo cơ sở dữ liệu SQLite bán hàng điện máy tương thích KiotViet & Stock Sense.
Thực thi schema DDL và nạp dữ liệu kiểm thử (synthetic seed data) quy mô 60+ SP, 3 chi nhánh.
"""
import sqlite3
import os
import sys
import uuid
from datetime import datetime, timedelta

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(DATA_DIR, "schema.sql")
DB_PATH = os.path.join(DATA_DIR, "kiotviet_electronics.db")


def init_database():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)

    cursor = conn.cursor()

    # 1. BẢNG BRANCHES (3 Chi nhánh)
    branches = [
        ('BR_KHO_TONG', 'Kho Tổng Hà Nội - KCN Đài Tư', 'KCN Đài Tư, Long Biên, Hà Nội', 1),
        ('BR_CAU_GIAY', 'Showroom Cầu Giấy', '122 Xuân Thủy, Cầu Giấy, Hà Nội', 1),
        ('BR_HA_DONG', 'Showroom Hà Đông', '88 Quang Trung, Hà Đông, Hà Nội', 1),
    ]
    cursor.executemany("""
        INSERT INTO branches (branch_id, branch_name, address, is_active)
        VALUES (?, ?, ?, ?)
    """, branches)

    # 2. BẢNG DIM_CUSTOMERS (Khách hàng)
    customers = [
        ('KH00001', 'Cá nhân', 'Nguyễn Văn An', '0901234567', 'an.nguyen@email.com', '123 Hoàng Diệu', 'Đà Nẵng - Hải Châu', 'Phước Ninh', None, None, '048098001234', 28500000.0, 0.0, 1),
        ('KH00002', 'Cá nhân', 'Trần Thị Bích', '0912345678', 'bich.tran@email.com', '45 Lê Duẩn', 'Đà Nẵng - Thanh Khê', 'Tân Chính', None, None, '048195002345', 18900000.0, 0.0, 1),
        ('KH00003', 'Doanh nghiệp', 'Công ty Cổ phần Công nghệ Alpha', '02363888999', 'account@alpha-tech.vn', '88 Nguyễn Văn Linh', 'Đà Nẵng - Hải Châu', 'Nam Dương', 'Công ty Cổ phần Công nghệ Alpha', '0401889977', None, 45000000.0, 0.0, 1),
        ('KH00004', 'Cá nhân', 'Lê Hoàng Nam', '0988776655', 'nam.le@email.com', '210 Điện Biên Phủ', 'Hà Nội - Cầu Giấy', 'Dịch Vọng', None, None, '048092003456', 0.0, 0.0, 1),
        ('KH00005', 'Cá nhân', 'Phạm Quỳnh Như', '0977665544', 'nhu.pham@email.com', '15 Trần Phú', 'Hà Nội - Hà Đông', 'Văn Quán', None, None, '048197004567', 0.0, 0.0, 1)
    ]
    cursor.executemany("""
        INSERT INTO DIM_CUSTOMERS (customer_code, customer_type, customer_name, phone, email, address, area, ward, company, tax_code, identity_card, total_sales, current_debt, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, customers)

    # 3. BẢNG DIM_EMPLOYEES (Nhân viên)
    employees = [
        ('NV0001', 'Võ Quốc Huy', '0905111222', 'Kinh doanh', 'Chuyên viên Bán hàng Điện máy', 'huy.vq', 'Showroom Cầu Giấy', 9000000.0, 1),
        ('NV0002', 'Lê Thanh Mai', '0905222333', 'Kinh doanh', 'Chuyên viên Bán hàng Điện tử', 'mai.lt', 'Showroom Hà Đông', 8500000.0, 1),
        ('NV0003', 'Nguyễn Đức Thắng', '0905333444', 'Kỹ thuật', 'Kỹ thuật viên Lắp đặt & Bảo hành', 'thang.nd', 'Kho Tổng Hà Nội', 10500000.0, 1),
        ('NV0004', 'Đặng Tuấn Khang', '0905444555', 'Kho', 'Thủ kho Điện máy', 'khang.dt', 'Kho Tổng Hà Nội', 8000000.0, 1)
    ]
    cursor.executemany("""
        INSERT INTO DIM_EMPLOYEES (employee_code, employee_name, phone, department, title, login, branch_working, salary_base, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, employees)

    # 4. BẢNG DIM_PRODUCTS (60 Sản phẩm điện máy đa dạng phân khúc)
    base_products = [
        # (code, barcode, cat, name, brand, model, uom, cost, sale, stock, warranty)
        ('SP_DK_FTKC', '8936001001', 'Điện lạnh > Máy lạnh > Inverter', 'Máy lạnh Daikin Inverter 1.5 HP FTKC35UVMV', 'Daikin', 'FTKC35UVMV', 'Bộ', 9200000.0, 12500000.0, 35, 24),
        ('SP_DK_FTKZ', '8936001002', 'Điện lạnh > Máy lạnh > Inverter', 'Máy lạnh Daikin Inverter 1.0 HP FTKZ25VVMV Cao Cấp', 'Daikin', 'FTKZ25VVMV', 'Bộ', 11500000.0, 14900000.0, 20, 24),
        ('SP_PA_XPU9', '8936001003', 'Điện lạnh > Máy lạnh > Inverter', 'Máy lạnh Panasonic Inverter 1.0 HP CU/CS-XPU9XKH-8', 'Panasonic', 'XPU9XKH-8', 'Bộ', 8100000.0, 10800000.0, 40, 12),
        ('SP_PA_XPU12', '8936001004', 'Điện lạnh > Máy lạnh > Inverter', 'Máy lạnh Panasonic Inverter 1.5 HP CU/CS-XPU12XKH-8', 'Panasonic', 'XPU12XKH-8', 'Bộ', 10200000.0, 13200000.0, 25, 12),
        ('SP_LG_V10', '8936001005', 'Điện lạnh > Máy lạnh > Inverter', 'Máy lạnh LG Inverter 1.0 HP V10WIN1', 'LG', 'V10WIN1', 'Bộ', 6500000.0, 8490000.0, 50, 24),
        ('SP_LG_V13', '8936001006', 'Điện lạnh > Máy lạnh > Inverter', 'Máy lạnh LG Inverter 1.5 HP V13WIN1', 'LG', 'V13WIN1', 'Bộ', 7900000.0, 10290000.0, 30, 24),
        ('SP_PA_CW53', '8936001007', 'Điện lạnh > Tủ lạnh > 2 Cánh Inverter', 'Tủ lạnh Panasonic Inverter 495 lít NR-CW530XMMV', 'Panasonic', 'NR-CW530XMMV', 'Chiếc', 26000000.0, 31900000.0, 15, 36),
        ('SP_PA_BV32', '8936001008', 'Điện lạnh > Tủ lạnh > 2 Cánh Inverter', 'Tủ lạnh Panasonic Inverter 290 lít NR-BV320GKVN', 'Panasonic', 'NR-BV320GKVN', 'Chiếc', 9500000.0, 12490000.0, 28, 24),
        ('SP_SS_RS64', '8936001009', 'Điện lạnh > Tủ lạnh > Side by Side', 'Tủ lạnh Samsung Side By Side Inverter 617 lít RS64R5301B4', 'Samsung', 'RS64R5301B4', 'Chiếc', 13500000.0, 17990000.0, 18, 24),
        ('SP_SS_RB30', '8936001010', 'Điện lạnh > Tủ lạnh > 2 Cánh Inverter', 'Tủ lạnh Samsung Inverter 305 lít RB30N4170S8', 'Samsung', 'RB30N4170S8', 'Chiếc', 8200000.0, 10690000.0, 22, 24),
        ('SP_LG_GR60', '8936001011', 'Điện lạnh > Tủ lạnh > Side by Side', 'Tủ lạnh LG InstaView Door-in-Door 601 lít GR-X247JS', 'LG', 'GR-X247JS', 'Chiếc', 31000000.0, 39900000.0, 8, 24),
        ('SP_TS_GR41', '8936001012', 'Điện lạnh > Tủ lạnh > 2 Cánh Inverter', 'Tủ lạnh Toshiba Inverter 322 lít GR-RB410WE-PMV(37)-SG', 'Toshiba', 'GR-RB410WE', 'Chiếc', 7100000.0, 9290000.0, 32, 24),
        
        ('SP_SN_XR65', '8936002001', 'Điện tử > Tivi > Smart Tivi 4K', 'Smart Tivi Sony Bravia OLED 4K 65 inch XR-65A80L', 'Sony', 'XR-65A80L', 'Chiếc', 24000000.0, 28500000.0, 18, 24),
        ('SP_SN_KD55', '8936002002', 'Điện tử > Tivi > Smart Tivi 4K', 'Smart Tivi Sony 4K 55 inch KD-55X77L', 'Sony', 'KD-55X77L', 'Chiếc', 10500000.0, 13490000.0, 26, 24),
        ('SP_SN_KD75', '8936002003', 'Điện tử > Tivi > Smart Tivi 4K', 'Smart Tivi Sony 4K 75 inch KD-75X80L', 'Sony', 'KD-75X80L', 'Chiếc', 20500000.0, 25900000.0, 12, 24),
        ('SP_SS_QA65', '8936002004', 'Điện tử > Tivi > Smart Tivi 4K', 'Smart Tivi QLED Samsung 4K 65 inch QA65Q60B', 'Samsung', 'QA65Q60B', 'Chiếc', 12800000.0, 16900000.0, 24, 24),
        ('SP_SS_UA55', '8936002005', 'Điện tử > Tivi > Smart Tivi 4K', 'Smart Tivi Samsung Crystal UHD 4K 55 inch UA55AU7002', 'Samsung', 'UA55AU7002', 'Chiếc', 7200000.0, 9490000.0, 45, 24),
        ('SP_SS_QA75', '8936002006', 'Điện tử > Tivi > Smart Tivi 4K', 'Smart Tivi Neo QLED Samsung 4K 75 inch QA75QN85C', 'Samsung', 'QA75QN85C', 'Chiếc', 38000000.0, 49900000.0, 6, 24),
        ('SP_LG_OLED55', '8936002007', 'Điện tử > Tivi > Smart Tivi 4K', 'Smart Tivi OLED LG 4K 55 inch 55C3PSA', 'LG', '55C3PSA', 'Chiếc', 22500000.0, 27900000.0, 14, 24),
        ('SP_LG_UQ75', '8936002008', 'Điện tử > Tivi > Smart Tivi 4K', 'Smart Tivi LG 4K 50 inch 50UQ7550PSF', 'LG', '50UQ7550PSF', 'Chiếc', 6800000.0, 8900000.0, 35, 24),
        ('SP_TCL_55Q', '8936002009', 'Điện tử > Tivi > Smart Tivi 4K', 'Google Tivi TCL QLED 4K 55 inch 55Q646', 'TCL', '55Q646', 'Chiếc', 6200000.0, 7990000.0, 40, 24),
        ('SP_TCL_65C', '8936002010', 'Điện tử > Tivi > Smart Tivi 4K', 'Google Tivi Mini QD-OLED TCL 4K 65 inch 65C745', 'TCL', '65C745', 'Chiếc', 13200000.0, 16900000.0, 16, 24),

        ('SP_LG_FV14', '8936003001', 'Điện gia dụng > Máy giặt > Cửa trước', 'Máy giặt LG AI DD Inverter 10 kg FV1410S4P', 'LG', 'FV1410S4P', 'Chiếc', 7800000.0, 10200000.0, 30, 24),
        ('SP_LG_FV12', '8936003002', 'Điện gia dụng > Máy giặt > Cửa trước', 'Máy giặt LG AI DD Inverter 9 kg FV1409S4W', 'LG', 'FV1409S4W', 'Chiếc', 6700000.0, 8790000.0, 35, 24),
        ('SP_EL_EWF10', '8936003003', 'Điện gia dụng > Máy giặt > Cửa trước', 'Máy giặt Electrolux UltimateCare 500 10 kg EWF1024P5WB', 'Electrolux', 'EWF1024P5WB', 'Chiếc', 8900000.0, 11490000.0, 22, 24),
        ('SP_EL_EWF09', '8936003004', 'Điện gia dụng > Máy giặt > Cửa trước', 'Máy giặt Electrolux UltimateCare 300 9 kg EWF9024D3WB', 'Electrolux', 'EWF9024D3WB', 'Chiếc', 7400000.0, 9690000.0, 28, 24),
        ('SP_SS_WW95', '8936003005', 'Điện gia dụng > Máy giặt > Cửa trước', 'Máy giặt Samsung Inverter 9.5 kg WW95TA046AX/SV', 'Samsung', 'WW95TA046AX', 'Chiếc', 6200000.0, 8190000.0, 36, 24),
        ('SP_PA_F95', '8936003006', 'Điện gia dụng > Máy giặt > Cửa trên', 'Máy giặt Panasonic Inverter 9.5 kg NA-FD95V1BRV', 'Panasonic', 'NA-FD95V1BRV', 'Chiếc', 5500000.0, 7190000.0, 25, 24),
        ('SP_TS_WK10', '8936003007', 'Điện gia dụng > Máy giặt > Cửa trên', 'Máy giặt Toshiba 9 kg AW-M1000FV(MK)', 'Toshiba', 'AW-M1000FV', 'Chiếc', 3800000.0, 4990000.0, 42, 24),

        ('SP_SS_S24U', '8936004001', 'Công nghệ > Điện thoại > Smartphone', 'Samsung Galaxy S24 Ultra 256GB Titanium Gray', 'Samsung', 'SM-S928B', 'Chiếc', 22500000.0, 27990000.0, 45, 12),
        ('SP_IP_16PM', '8936004002', 'Công nghệ > Điện thoại > Smartphone', 'iPhone 16 Pro Max 256GB Desert Titanium', 'Apple', 'A3297', 'Chiếc', 28500000.0, 34490000.0, 30, 12),
        ('SP_IP_15', '8936004003', 'Công nghệ > Điện thoại > Smartphone', 'iPhone 15 128GB Black', 'Apple', 'A3090', 'Chiếc', 16200000.0, 19490000.0, 50, 12),
        ('SP_SS_A55', '8936004004', 'Công nghệ > Điện thoại > Smartphone', 'Samsung Galaxy A55 5G 128GB Awesome Navy', 'Samsung', 'SM-A556B', 'Chiếc', 7100000.0, 8990000.0, 60, 12),
        ('SP_XM_14T', '8936004005', 'Công nghệ > Điện thoại > Smartphone', 'Xiaomi 14T 5G 12GB/512GB Titan Black', 'Xiaomi', '2406APNFAG', 'Chiếc', 10500000.0, 13490000.0, 25, 18),
        ('SP_OP_RENO', '8936004006', 'Công nghệ > Điện thoại > Smartphone', 'OPPO Reno12 5G 12GB/256GB Bạc Vũ Trụ', 'OPPO', 'CPH2625', 'Chiếc', 9800000.0, 12490000.0, 35, 12),

        ('SP_SH_KS18', '8936005001', 'Gia dụng nhà bếp > Nồi cơm điện', 'Nồi cơm điện tử Sharp 1.8L KS-COM18V', 'Sharp', 'KS-COM18V', 'Cái', 850000.0, 1290000.0, 60, 12),
        ('SP_CP_CR06', '8936005002', 'Gia dụng nhà bếp > Nồi cơm điện', 'Nồi cơm điện cao tần Cuckoo 1.08L CRP-FHR0610FG', 'Cuckoo', 'CRP-FHR0610FG', 'Cái', 4800000.0, 6490000.0, 20, 24),
        ('SP_PH_HD92', '8936005003', 'Gia dụng nhà bếp > Nồi chiên không dầu', 'Nồi chiên không dầu Philips 6.2 lít HD9270/90', 'Philips', 'HD9270/90', 'Cái', 1850000.0, 2590000.0, 45, 24),
        ('SP_TE_EY50', '8936005004', 'Gia dụng nhà bếp > Nồi chiên không dầu', 'Nồi chiên không dầu Tefal 5.0 lít EY505D15', 'Tefal', 'EY505D15', 'Cái', 1450000.0, 2090000.0, 30, 24),
        ('SP_PA_NNST', '8936005005', 'Gia dụng nhà bếp > Lò vi sóng', 'Lò vi sóng Panasonic Inverter 27 lít NN-ST34HMYUE', 'Panasonic', 'NN-ST34HMYUE', 'Cái', 2200000.0, 2990000.0, 25, 12),
        ('SP_SH_R205', '8936005006', 'Gia dụng nhà bếp > Lò vi sóng', 'Lò vi sóng cơ Sharp 20 lít R-205VN(S)', 'Sharp', 'R-205VN(S)', 'Cái', 950000.0, 1390000.0, 50, 12),
    ]

    # Mở rộng thêm cho đủ 55+ sản phẩm
    extended_products = []
    for idx in range(1, 16):
        sku = f"SP_EXT_ACC_{idx:02d}"
        barcode = f"89360099{idx:02d}"
        cat = "Phụ kiện & Tiện ích > Thiết bị thông minh"
        name = f"Thiết bị điện máy thông minh cao cấp Model SS-2026-{idx:02d}"
        brand = "Philips" if idx % 2 == 0 else "Xiaomi"
        model = f"SS-M{idx}"
        uom = "Cái"
        cost = 350000.0 + idx * 50000.0
        sale = cost * 1.35
        stock = 25 + idx * 2
        warranty = 12
        extended_products.append((sku, barcode, cat, name, brand, model, uom, cost, sale, stock, warranty))

    all_products = base_products + extended_products

    product_rows = []
    for p in all_products:
        sku, barcode, cat, name, brand, model, uom, cost, sale, stock, warranty = p
        product_rows.append((sku, barcode, 'Hàng hóa', cat, name, brand, model, uom, cost, sale, stock, warranty, 1, 1, 1))

    cursor.executemany("""
        INSERT INTO DIM_PRODUCTS (product_code, barcode, product_type, category_path, product_name, brand, model, uom, cost_price, sale_price, stock_on_hand, warranty_months, has_serial_tracking, is_active, is_direct_sale)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, product_rows)

    # 5. BẢNG INVENTORIES (Phân bổ tồn kho trên 3 chi nhánh)
    # Tồn tại Kho Tổng lớn nhất, Cầu Giấy và Hà Đông vừa phải
    inventory_rows = []
    branch_ids = ['BR_KHO_TONG', 'BR_CAU_GIAY', 'BR_HA_DONG']

    for p in all_products:
        sku = p[0]
        base_stock = p[9]

        # Kho Tổng
        oh_tong = int(base_stock * 0.6)
        res_tong = int(oh_tong * 0.15)
        it_tong = 10 if "Tivi" in p[2] or "Máy lạnh" in p[2] else 0
        atp_tong = oh_tong - res_tong
        inventory_rows.append((str(uuid.uuid4()), 'BR_KHO_TONG', sku, oh_tong, res_tong, it_tong, atp_tong, 1))

        # Showroom Cầu Giấy
        oh_cg = int(base_stock * 0.25)
        res_cg = int(oh_cg * 0.3)
        it_cg = 5 if "Smartphone" in p[2] else 0
        atp_cg = oh_cg - res_cg
        inventory_rows.append((str(uuid.uuid4()), 'BR_CAU_GIAY', sku, oh_cg, res_cg, it_cg, atp_cg, 1))

        # Showroom Hà Đông
        oh_hd = base_stock - oh_tong - oh_cg
        if oh_hd < 0:
            oh_hd = 5
        res_hd = int(oh_hd * 0.2)
        it_hd = 0
        atp_hd = oh_hd - res_hd
        inventory_rows.append((str(uuid.uuid4()), 'BR_HA_DONG', sku, oh_hd, res_hd, it_hd, atp_hd, 1))

    cursor.executemany("""
        INSERT INTO inventories (inventory_id, branch_id, product_code, on_hand_qty, reserved_qty, in_transit_qty, atp_qty, version)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, inventory_rows)

    # 6. BẢNG FACT_ORDERS & INVENTORY_RESERVATIONS (Đơn hàng & Giữ chỗ thực tế)
    now = datetime.now()
    two_days_ago = now - timedelta(hours=50)   # Đã quá hạn 48h!
    three_days_ago = now - timedelta(hours=72) # Đã quá hạn 72h!
    yesterday = now - timedelta(hours=15)      # Vẫn còn hạn (< 48h)

    # Tạo các đơn hàng
    order_data = [
        ('ORD_EXP_01', three_days_ago.strftime('%Y-%m-%d %H:%M:%S'), 'KH00001', 'NV0001', 28500000.0, 0.0, 28500000.0, 'Chờ xử lý', 'Đơn trả góp FE Credit chờ thẩm định'),
        ('ORD_EXP_02', two_days_ago.strftime('%Y-%m-%d %H:%M:%S'), 'KH00002', 'NV0001', 34490000.0, 0.0, 34490000.0, 'Chờ xử lý', 'Đơn trả góp HD Saison duyệt lâu'),
        ('ORD_EXP_03', two_days_ago.strftime('%Y-%m-%d %H:%M:%S'), 'KH00004', 'NV0002', 27990000.0, 0.0, 27990000.0, 'Chờ xử lý', 'Khách hẹn bổ sung CCCD'),
        ('ORD_ACT_01', yesterday.strftime('%Y-%m-%d %H:%M:%S'), 'KH00005', 'NV0001', 12500000.0, 0.0, 12500000.0, 'Chờ xử lý', 'Đơn trả góp mới nộp sáng nay'),
        ('ORD_FULL_01', now.strftime('%Y-%m-%d %H:%M:%S'), 'KH00003', 'NV0002', 31900000.0, 31900000.0, 0.0, 'Chờ xử lý', 'Đơn thanh toán 100% chuẩn bị giao chiều'),
    ]
    cursor.executemany("""
        INSERT INTO FACT_ORDERS (order_code, order_time, customer_code, seller_code, total_amount, deposit_amount, amount_due, status, note)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, order_data)

    # Tạo reservations tương ứng
    reservations = [
        # Quá hạn 48h (cần auto-release)
        (str(uuid.uuid4()), 'ORD_EXP_01', 'BR_KHO_TONG', 'SP_SN_XR65', 1, 'INSTALLMENT_HOLD', 'ACTIVE', (three_days_ago + timedelta(hours=48)).strftime('%Y-%m-%d %H:%M:%S'), three_days_ago.strftime('%Y-%m-%d %H:%M:%S')),
        (str(uuid.uuid4()), 'ORD_EXP_02', 'BR_CAU_GIAY', 'SP_IP_16PM', 1, 'INSTALLMENT_HOLD', 'ACTIVE', (two_days_ago + timedelta(hours=48)).strftime('%Y-%m-%d %H:%M:%S'), two_days_ago.strftime('%Y-%m-%d %H:%M:%S')),
        (str(uuid.uuid4()), 'ORD_EXP_03', 'BR_HA_DONG', 'SP_SS_S24U', 1, 'INSTALLMENT_HOLD', 'ACTIVE', (two_days_ago + timedelta(hours=48)).strftime('%Y-%m-%d %H:%M:%S'), two_days_ago.strftime('%Y-%m-%d %H:%M:%S')),
        # Còn hạn
        (str(uuid.uuid4()), 'ORD_ACT_01', 'BR_CAU_GIAY', 'SP_DK_FTKC', 1, 'INSTALLMENT_HOLD', 'ACTIVE', (yesterday + timedelta(hours=48)).strftime('%Y-%m-%d %H:%M:%S'), yesterday.strftime('%Y-%m-%d %H:%M:%S')),
        # Trả thẳng
        (str(uuid.uuid4()), 'ORD_FULL_01', 'BR_KHO_TONG', 'SP_PA_CW53', 1, 'FULL_HOLD', 'ACTIVE', (now + timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S'), now.strftime('%Y-%m-%d %H:%M:%S')),
    ]
    cursor.executemany("""
        INSERT INTO inventory_reservations (reservation_id, order_code, branch_id, product_code, reserved_qty, reservation_type, status, expires_at, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, reservations)

    # 7. BẢNG PURCHASE_ORDERS & PO_ITEMS (Hàng đang về In-Transit)
    next_week = now + timedelta(days=3)
    po_data = [
        ('PO-2026-001', 'BR_KHO_TONG', 'Sony Electronics Việt Nam', 'CONFIRMED_IN_TRANSIT', next_week.strftime('%Y-%m-%d %H:%M:%S'), 'Đơn nhập Tivi OLED lô mới'),
        ('PO-2026-002', 'BR_CAU_GIAY', 'Samsung Vina', 'CONFIRMED_IN_TRANSIT', next_week.strftime('%Y-%m-%d %H:%M:%S'), 'Đơn bổ sung Galaxy S24 Ultra'),
    ]
    cursor.executemany("""
        INSERT INTO purchase_orders (po_id, branch_id, vendor_name, status, expected_delivery_date, note)
        VALUES (?, ?, ?, ?, ?, ?)
    """, po_data)

    po_items_data = [
        ('PO-2026-001', 'SP_SN_XR65', 10, 24000000.0, 0),
        ('PO-2026-002', 'SP_SS_S24U', 5, 22500000.0, 0),
    ]
    cursor.executemany("""
        INSERT INTO po_items (po_id, product_code, ordered_qty, unit_cost, received_qty)
        VALUES (?, ?, ?, ?, ?)
    """, po_items_data)

    conn.commit()

    # Kiểm tra ràng buộc khóa ngoại
    fk_errors = list(conn.execute("PRAGMA foreign_key_check;"))
    if fk_errors:
        print("[!] Phát hiện lỗi khóa ngoại:", fk_errors)
        conn.close()
        raise RuntimeError(f"Foreign key integrity failure: {fk_errors}")

    print(f"[+] Đã tạo thành công cơ sở dữ liệu Stock Sense tại: {DB_PATH}")
    print(f"    - Số chi nhánh: {len(branches)}")
    print(f"    - Số sản phẩm: {len(all_products)}")
    print(f"    - Số bản ghi tồn kho: {len(inventory_rows)}")
    conn.close()


if __name__ == "__main__":
    init_database()
