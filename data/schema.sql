-- ============================================================================
-- KIOTVIET FASHION RETAIL DATA WAREHOUSE & ANALYTICS SCHEMA (SQLite)
-- Schema Definition: DDL, Constraints, Indexes, Views & Seed Data
-- Tương thích hoàn toàn với PoS KiotViet ngành Thời trang
-- ============================================================================

PRAGMA foreign_keys = ON;

-- ============================================================================
-- 1. BẢNG DANH MỤC PHÂN CẤP (DIM_CATEGORIES)
-- Phục vụ bóc tách cột 'Nhóm hàng(3 Cấp)' từ file Excel của KiotViet
-- ============================================================================
CREATE TABLE IF NOT EXISTS DIM_CATEGORIES (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_path TEXT NOT NULL UNIQUE, -- vd: 'Thời trang Nam > Áo Nam > Áo Polo'
    category_level1 TEXT,               -- Cấp 1: 'Thời trang Nam'
    category_level2 TEXT,               -- Cấp 2: 'Áo Nam'
    category_level3 TEXT,               -- Cấp 3: 'Áo Polo'
    created_at TEXT DEFAULT (DATETIME('now', 'localtime'))
);

-- ============================================================================
-- 2. BẢNG KHÁCH HÀNG (DIM_CUSTOMERS)
-- Master data quản lý khách hàng theo mẫu Customer Template của KiotViet
-- ============================================================================
CREATE TABLE IF NOT EXISTS DIM_CUSTOMERS (
    customer_code TEXT PRIMARY KEY,     -- Mã KH (vd: KH00001, KH_BANLE)
    customer_name TEXT NOT NULL,         -- Tên khách hàng
    customer_type TEXT DEFAULT 'Cá nhân',-- Loại khách (Cá nhân/Doanh nghiệp)
    phone TEXT,                          -- Số điện thoại định danh tại quầy
    gender TEXT CHECK (gender IN ('Nam', 'Nữ', 'Khác', NULL)),
    dob TEXT,                            -- Ngày sinh (YYYY-MM-DD)
    address TEXT,                        -- Địa chỉ chi tiết
    area TEXT,                           -- Tỉnh / Thành phố
    ward TEXT,                           -- Quận / Huyện / Phường
    company TEXT,                        -- Tên công ty (nếu là khách doanh nghiệp)
    tax_code TEXT,                       -- Mã số thuế
    is_active INTEGER DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at TEXT DEFAULT (DATETIME('now', 'localtime'))
);

CREATE INDEX IF NOT EXISTS idx_customers_phone ON DIM_CUSTOMERS(phone);
CREATE INDEX IF NOT EXISTS idx_customers_area ON DIM_CUSTOMERS(area);

-- ============================================================================
-- 3. BẢNG NHÂN VIÊN (DIM_EMPLOYEES)
-- Master data quản lý nhân sự & chi nhánh theo mẫu Employee Template KiotViet
-- ============================================================================
CREATE TABLE IF NOT EXISTS DIM_EMPLOYEES (
    employee_code TEXT PRIMARY KEY,     -- Mã NV (vd: NV001)
    employee_name TEXT NOT NULL,         -- Tên nhân viên
    phone TEXT,                          -- Số điện thoại
    department TEXT,                     -- Phòng ban (Bán hàng, Kho, Thu ngân...)
    title TEXT,                          -- Chức danh (Nhân viên tư vấn, Thu ngân...)
    login_account TEXT,                  -- Tài khoản đăng nhập hệ thống
    branch_working TEXT DEFAULT 'Chi nhánh chính', -- Chi nhánh làm việc
    salary REAL DEFAULT 0,               -- Lương cơ bản
    dob TEXT,                            -- Ngày sinh
    start_date TEXT,                     -- Ngày bắt đầu làm việc
    is_active INTEGER DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at TEXT DEFAULT (DATETIME('now', 'localtime'))
);

CREATE INDEX IF NOT EXISTS idx_employees_branch ON DIM_EMPLOYEES(branch_working);

-- ============================================================================
-- 4. BẢNG HÀNG HÓA THỜI TRANG (DIM_PRODUCTS)
-- Master data sản phẩm: Ma trận biến thể Size/Màu/Style + KiotViet Product Fields
-- ============================================================================
CREATE TABLE IF NOT EXISTS DIM_PRODUCTS (
    product_code TEXT PRIMARY KEY,      -- Mã SKU biến thể duy nhất (vd: AT001-DEN-L)
    barcode TEXT UNIQUE,                 -- Mã vạch sản phẩm
    product_name TEXT NOT NULL,          -- Tên sản phẩm đầy đủ kèm thuộc tính
    product_type TEXT DEFAULT 'Hàng hóa',-- Phân loại: Hàng hóa, Combo, Dịch vụ
    parent_code TEXT,                    -- Mã thiết kế cha / Style Code (vd: AT001)
    category_path TEXT,                  -- Nhóm hàng 3 cấp theo KiotViet
    category_id INTEGER,                 -- FK tham chiếu bảng DIM_CATEGORIES chuẩn hóa
    brand TEXT DEFAULT 'Generic',        -- Thương hiệu thời trang
    
    -- Thuộc tính đặc thù ngành Thời trang:
    size TEXT,                           -- Kích cỡ: XS, S, M, L, XL, 29, 30, FreeSize...
    color TEXT,                          -- Màu sắc: Đen, Trắng, Xanh Navy, Be...
    material TEXT,                       -- Chất liệu vải: 100% Cotton, Linen, Kaki...
    season TEXT,                         -- Bộ sưu tập/Mùa: Xuân Hè, Thu Đông, All-Season
    
    -- Chỉ số giá & kho vận (Rule R2):
    sale_price REAL NOT NULL CHECK (sale_price >= 0),   -- Giá niêm yết bán lẻ
    cost_price REAL NOT NULL CHECK (cost_price >= 0),   -- Giá vốn hiện hành
    stock_on_hand INTEGER NOT NULL DEFAULT 0,          -- Tồn kho thực tế
    min_stock INTEGER DEFAULT 0,                        -- Định mức tồn nhỏ nhất
    max_stock INTEGER DEFAULT 1000,                     -- Định mức tồn lớn nhất
    uom TEXT DEFAULT 'Cái',              -- Đơn vị tính
    is_active INTEGER DEFAULT 1 CHECK (is_active IN (0, 1)),
    is_direct_sale INTEGER DEFAULT 1 CHECK (is_direct_sale IN (0, 1)),
    created_at TEXT DEFAULT (DATETIME('now', 'localtime')),
    
    FOREIGN KEY (category_id) REFERENCES DIM_CATEGORIES(category_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_products_parent ON DIM_PRODUCTS(parent_code);
CREATE INDEX IF NOT EXISTS idx_products_size_color ON DIM_PRODUCTS(size, color);
CREATE INDEX IF NOT EXISTS idx_products_category ON DIM_PRODUCTS(category_id);
CREATE INDEX IF NOT EXISTS idx_products_stock ON DIM_PRODUCTS(stock_on_hand);

-- ============================================================================
-- 5. BẢNG HÓA ĐƠN BÁN HÀNG (FACT_INVOICES) - HEADER
-- Giao dịch bán hàng thực tế: Ghi nhận doanh thu, thanh toán, kiểm soát Rule R1, R3
-- ============================================================================
CREATE TABLE IF NOT EXISTS FACT_INVOICES (
    invoice_code TEXT PRIMARY KEY,       -- Rule R1: Tiền tố HDIPxxxxx khi import
    invoice_time TEXT NOT NULL,          -- Thời gian phát sinh hóa đơn (YYYY-MM-DD HH:MM:SS)
    customer_code TEXT NOT NULL,         -- Rule R4: FK tham chiếu Khách hàng
    employee_code TEXT,                  -- FK tham chiếu Nhân viên bán
    order_code TEXT,                     -- FK tham chiếu Đơn đặt hàng gốc (nếu có)
    sales_channel TEXT DEFAULT 'Trực tiếp', -- Kênh bán: Trực tiếp, Website, Shopee, TikTok
    branch_name TEXT DEFAULT 'Chi nhánh chính',
    pricebook TEXT DEFAULT 'Bảng giá chung',
    
    -- Chỉ số tài chính hóa đơn (Rule R3):
    total_amount REAL NOT NULL CHECK (total_amount >= 0),           -- Tổng tiền hàng trước giảm
    discount_amount REAL DEFAULT 0 CHECK (discount_amount >= 0),    -- Giảm giá hóa đơn (VND)
    discount_percent REAL DEFAULT 0 CHECK (discount_percent >= 0 AND discount_percent <= 100),
    final_amount REAL NOT NULL CHECK (final_amount >= 0),          -- Khách cần trả (Net Amount)
    
    -- Phân bổ các hình thức thanh toán:
    pay_cash REAL DEFAULT 0 CHECK (pay_cash >= 0),
    pay_card REAL DEFAULT 0 CHECK (pay_card >= 0),
    pay_transfer REAL DEFAULT 0 CHECK (pay_transfer >= 0),
    
    note TEXT,
    created_at TEXT DEFAULT (DATETIME('now', 'localtime')),
    
    FOREIGN KEY (customer_code) REFERENCES DIM_CUSTOMERS(customer_code) ON UPDATE CASCADE,
    FOREIGN KEY (employee_code) REFERENCES DIM_EMPLOYEES(employee_code) ON UPDATE CASCADE,
    FOREIGN KEY (order_code) REFERENCES FACT_ORDERS(order_code) ON DELETE SET NULL,
    
    -- Ràng buộc Rule R3: Cân đối thanh toán
    CONSTRAINT chk_payment_balance CHECK (
        ABS(final_amount - (pay_cash + pay_card + pay_transfer)) <= 1.0
    ),
    -- Ràng buộc Rule R1: Mã hóa đơn tuân thủ định dạng HDIP
    CONSTRAINT chk_invoice_prefix CHECK (
        invoice_code LIKE 'HDIP%'
    )
);

CREATE INDEX IF NOT EXISTS idx_invoices_time ON FACT_INVOICES(invoice_time);
CREATE INDEX IF NOT EXISTS idx_invoices_customer ON FACT_INVOICES(customer_code);
CREATE INDEX IF NOT EXISTS idx_invoices_employee ON FACT_INVOICES(employee_code);

-- ============================================================================
-- 6. BẢNG CHI TIẾT HÓA ĐƠN (FACT_INVOICE_LINES) - LINE ITEMS
-- Ghi nhận SKU thời trang bán ra, số lượng, chiết khấu và snapshot giá vốn
-- ============================================================================
CREATE TABLE IF NOT EXISTS FACT_INVOICE_LINES (
    invoice_line_id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_code TEXT NOT NULL,
    product_code TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),             -- Rule R3: Số lượng > 0
    unit_price REAL NOT NULL CHECK (unit_price >= 0),           -- Đơn giá niêm yết
    discount_amount REAL DEFAULT 0 CHECK (discount_amount >= 0),
    discount_percent REAL DEFAULT 0 CHECK (discount_percent >= 0 AND discount_percent <= 100),
    line_total REAL NOT NULL CHECK (line_total >= 0),           -- Thành tiền dòng = (SL * Đơn giá) - Giảm giá
    cost_price_snapshot REAL NOT NULL DEFAULT 0,                -- Snapshot giá vốn phục vụ tính Gross Margin
    created_at TEXT DEFAULT (DATETIME('now', 'localtime')),
    
    FOREIGN KEY (invoice_code) REFERENCES FACT_INVOICES(invoice_code) ON DELETE CASCADE,
    FOREIGN KEY (product_code) REFERENCES DIM_PRODUCTS(product_code) ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_invoice_lines_invoice ON FACT_INVOICE_LINES(invoice_code);
CREATE INDEX IF NOT EXISTS idx_invoice_lines_product ON FACT_INVOICE_LINES(product_code);

-- ============================================================================
-- 7. BẢNG ĐƠN ĐẶT HÀNG (FACT_ORDERS) - HEADER
-- Quản lý giữ chỗ, đặt trước (Pre-order), tiền cọc và vòng đời đơn hàng
-- ============================================================================
CREATE TABLE IF NOT EXISTS FACT_ORDERS (
    order_code TEXT PRIMARY KEY,                 -- Mã đặt hàng KiotViet (vd: DH00001)
    order_time TEXT NOT NULL,                     -- Thời gian đặt hàng (YYYY-MM-DD HH:MM:SS)
    customer_code TEXT NOT NULL,                  -- FK Khách hàng đặt
    employee_code TEXT,                           -- FK Nhân viên tiếp nhận
    sales_channel TEXT DEFAULT 'Trực tiếp',       -- Kênh tiếp nhận: Quầy, Facebook, Shopee, Web...
    branch_name TEXT DEFAULT 'Chi nhánh chính',
    
    amount_due REAL NOT NULL CHECK (amount_due >= 0),            -- Giá trị đơn khách cần trả
    amount_paid REAL DEFAULT 0 CHECK (amount_paid >= 0),         -- Số tiền khách đã cọc trước
    discount_amount REAL DEFAULT 0 CHECK (discount_amount >= 0), -- Giảm giá đơn hàng
    
    order_status TEXT DEFAULT 'Cho_xu_ly' CHECK (
        order_status IN ('Cho_xu_ly', 'Dang_giu_hang', 'Hoan_thanh', 'Da_huy')
    ),
    
    converted_invoice_code TEXT,                  -- Liên kết sang hóa đơn khi chốt bán
    expected_delivery_date TEXT,                  -- Hẹn ngày nhận/giao hàng
    cancel_reason TEXT,                           -- Lý do hủy đơn (phục vụ DS phân tích drop-off)
    note TEXT,                                    -- Yêu cầu đặc biệt của khách
    created_at TEXT DEFAULT (DATETIME('now', 'localtime')),
    
    FOREIGN KEY (customer_code) REFERENCES DIM_CUSTOMERS(customer_code) ON UPDATE CASCADE,
    FOREIGN KEY (employee_code) REFERENCES DIM_EMPLOYEES(employee_code) ON UPDATE CASCADE,
    FOREIGN KEY (converted_invoice_code) REFERENCES FACT_INVOICES(invoice_code) ON DELETE SET NULL,
    
    CONSTRAINT chk_order_deposit CHECK (amount_paid <= amount_due + 1.0)
);

CREATE INDEX IF NOT EXISTS idx_orders_time ON FACT_ORDERS(order_time);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON FACT_ORDERS(customer_code);
CREATE INDEX IF NOT EXISTS idx_orders_status ON FACT_ORDERS(order_status);
CREATE INDEX IF NOT EXISTS idx_orders_converted ON FACT_ORDERS(converted_invoice_code);

-- ============================================================================
-- 8. BẢNG CHI TIẾT ĐƠN ĐẶT HÀNG (FACT_ORDERS_LINES) - LINE ITEMS
-- Ghi nhận danh sách biến thể sản phẩm khách đặt trước / giữ chỗ
-- ============================================================================
CREATE TABLE IF NOT EXISTS FACT_ORDERS_LINES (
    order_line_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_code TEXT NOT NULL,
    product_code TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),             -- Rule R3
    unit_price REAL NOT NULL CHECK (unit_price >= 0),
    discount_amount REAL DEFAULT 0 CHECK (discount_amount >= 0),
    discount_percent REAL DEFAULT 0 CHECK (discount_percent >= 0 AND discount_percent <= 100),
    line_total REAL NOT NULL CHECK (line_total >= 0),
    created_at TEXT DEFAULT (DATETIME('now', 'localtime')),
    
    FOREIGN KEY (order_code) REFERENCES FACT_ORDERS(order_code) ON DELETE CASCADE,
    FOREIGN KEY (product_code) REFERENCES DIM_PRODUCTS(product_code) ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_order_lines_order ON FACT_ORDERS_LINES(order_code);
CREATE INDEX IF NOT EXISTS idx_order_lines_product ON FACT_ORDERS_LINES(product_code);

-- ============================================================================
-- 9. CÁC ANALYTICAL VIEWS DÀNH CHO DATA SCIENCE & DASHBOARD BI
-- ============================================================================

-- View 1: Phân tích Khách hàng RFM (Recency, Frequency, Monetary)
CREATE VIEW IF NOT EXISTS VW_CUSTOMER_RFM_RAW AS
SELECT 
    c.customer_code,
    c.customer_name,
    c.phone,
    c.area,
    CAST(ROUND(JULIANDAY((SELECT MAX(invoice_time) FROM FACT_INVOICES)) - JULIANDAY(MAX(i.invoice_time))) AS INTEGER) AS recency_days,
    COUNT(DISTINCT i.invoice_code) AS frequency,
    COALESCE(SUM(i.final_amount), 0) AS monetary,
    MIN(i.invoice_time) AS first_purchase_date,
    MAX(i.invoice_time) AS last_purchase_date
FROM DIM_CUSTOMERS c
JOIN FACT_INVOICES i ON c.customer_code = i.customer_code
WHERE c.customer_code != 'KH_BANLE'
GROUP BY c.customer_code, c.customer_name, c.phone, c.area;

-- View 2: Phân tích Doanh thu & Biên Lợi nhuận gộp theo Biến thể Thời trang
CREATE VIEW IF NOT EXISTS VW_SALES_MARGIN_ANALYTICS AS
SELECT 
    DATE(i.invoice_time) AS sale_date,
    i.invoice_code,
    i.sales_channel,
    p.parent_code AS style_code,
    p.product_code,
    p.product_name,
    p.size,
    p.color,
    p.material,
    p.season,
    p.brand,
    cat.category_level1,
    cat.category_level2,
    l.quantity,
    l.unit_price,
    l.line_total AS revenue,
    (l.cost_price_snapshot * l.quantity) AS total_cogs,
    (l.line_total - (l.cost_price_snapshot * l.quantity)) AS gross_profit,
    ROUND(
        ((l.line_total - (l.cost_price_snapshot * l.quantity)) * 100.0) / NULLIF(l.line_total, 0), 2
    ) AS gross_margin_percent
FROM FACT_INVOICE_LINES l
JOIN FACT_INVOICES i ON l.invoice_code = i.invoice_code
JOIN DIM_PRODUCTS p ON l.product_code = p.product_code
LEFT JOIN DIM_CATEGORIES cat ON p.category_id = cat.category_id;

-- View 3: Cặp sản phẩm thường mua cùng (Market Basket Co-occurrence)
CREATE VIEW IF NOT EXISTS VW_MARKET_BASKET_PAIRS AS
SELECT 
    a.invoice_code,
    a.product_code AS product_a,
    b.product_code AS product_b,
    pa.product_name AS product_name_a,
    pb.product_name AS product_name_b
FROM FACT_INVOICE_LINES a
JOIN FACT_INVOICE_LINES b 
    ON a.invoice_code = b.invoice_code AND a.product_code < b.product_code
JOIN DIM_PRODUCTS pa ON a.product_code = pa.product_code
JOIN DIM_PRODUCTS pb ON b.product_code = pb.product_code;

-- View 4: Tồn kho đang giữ chỗ theo Biến thể (Committed Stock by Variant)
CREATE VIEW IF NOT EXISTS VW_COMMITTED_STOCK_BY_VARIANT AS
SELECT 
    p.product_code,
    p.parent_code AS style_code,
    p.product_name,
    p.size,
    p.color,
    p.stock_on_hand AS physical_stock,
    COALESCE(SUM(ol.quantity), 0) AS committed_quantity,
    (p.stock_on_hand - COALESCE(SUM(ol.quantity), 0)) AS available_to_sell
FROM DIM_PRODUCTS p
LEFT JOIN FACT_ORDERS_LINES ol ON p.product_code = ol.product_code
LEFT JOIN FACT_ORDERS o ON ol.order_code = o.order_code 
    AND o.order_status IN ('Cho_xu_ly', 'Dang_giu_hang')
GROUP BY p.product_code;

-- View 5: Phễu chuyển đổi Đơn hàng sang Hóa đơn (Order Conversion Funnel)
CREATE VIEW IF NOT EXISTS VW_ORDER_CONVERSION_METRICS AS
SELECT 
    DATE(order_time) AS order_date,
    sales_channel,
    employee_code,
    COUNT(order_code) AS total_orders,
    SUM(CASE WHEN order_status = 'Hoan_thanh' THEN 1 ELSE 0 END) AS completed_orders,
    SUM(CASE WHEN order_status = 'Da_huy' THEN 1 ELSE 0 END) AS cancelled_orders,
    ROUND(
        SUM(CASE WHEN order_status = 'Hoan_thanh' THEN 1 ELSE 0 END) * 100.0 / COUNT(order_code), 2
    ) AS conversion_rate_percent,
    SUM(amount_due) AS pipeline_value,
    SUM(CASE WHEN order_status = 'Hoan_thanh' THEN amount_due ELSE 0 END) AS realized_value
FROM FACT_ORDERS
GROUP BY DATE(order_time), sales_channel, employee_code;

-- ============================================================================
-- 10. SEED DATA KHỞI TẠO MẪU BẢO ĐẢM TOÀN VẸN DỮ LIỆU (RULE R4)
-- ============================================================================
INSERT OR IGNORE INTO DIM_CUSTOMERS (customer_code, customer_name, customer_type, is_active)
VALUES ('KH_BANLE', 'Khách bán lẻ / Vãng lai', 'Cá nhân', 1);

INSERT OR IGNORE INTO DIM_EMPLOYEES (employee_code, employee_name, department, title, branch_working, is_active)
VALUES ('NV000', 'Quản trị viên', 'Quản trị', 'Admin', 'Chi nhánh chính', 1);
