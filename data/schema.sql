-- ============================================================================
-- CƠ SỞ DỮ LIỆU BÁN HÀNG ĐIỆN MÁY TƯƠNG THÍCH KIOTVIET (SQLITE DDL)
-- Phân loại: Kimball Star Schema / Snowflake Schema (Dimensions & Facts)
-- Đặc thù ngành: Quản lý Serial/IMEI, Bảo hành, Kỹ thuật lắp đặt, Kênh trả góp
-- ============================================================================

PRAGMA foreign_keys = ON;

-- ----------------------------------------------------------------------------
-- 1. BẢNG DANH MỤC KHÁCH HÀNG (DIM_CUSTOMERS)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS DIM_CUSTOMERS (
    customer_code       TEXT PRIMARY KEY,                             -- Mã khách hàng (VD: KH00001)
    customer_type       TEXT DEFAULT 'Cá nhân' CHECK(customer_type IN ('Cá nhân', 'Doanh nghiệp')),
    customer_name       TEXT NOT NULL,                                -- Tên khách hàng
    phone               TEXT,                                         -- Số điện thoại liên hệ
    email               TEXT,                                         -- Email nhận hóa đơn/bảo hành điện tử
    address             TEXT,                                         -- Địa chỉ giao hàng & thi công lắp đặt
    area                TEXT,                                         -- Tỉnh/Thành phố - Quận/Huyện
    ward                TEXT,                                         -- Phường/Xã
    company             TEXT,                                         -- Tên công ty (đối với khách B2B)
    tax_code            TEXT,                                         -- Mã số thuế xuất hóa đơn GTGT
    identity_card       TEXT,                                         -- CMND/CCCD (làm thủ tục trả góp)
    total_sales         REAL DEFAULT 0.0 CHECK(total_sales >= 0),    -- Cột phái sinh: Tổng chi tiêu tích lũy
    current_debt        REAL DEFAULT 0.0,                             -- Nợ cần thu hiện tại
    is_active           INTEGER DEFAULT 1 CHECK(is_active IN (0, 1)), -- 1: Đang kích hoạt, 0: Khóa
    created_at          TEXT DEFAULT (DATETIME('now', 'localtime'))
);

CREATE INDEX IF NOT EXISTS idx_customers_phone ON DIM_CUSTOMERS(phone);
CREATE INDEX IF NOT EXISTS idx_customers_area ON DIM_CUSTOMERS(area);

-- ----------------------------------------------------------------------------
-- 2. BẢNG DANH MỤC NHÂN VIÊN (DIM_EMPLOYEES)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS DIM_EMPLOYEES (
    employee_code       TEXT PRIMARY KEY,                             -- Mã nhân viên (VD: NV0001)
    employee_name       TEXT NOT NULL,                                -- Tên nhân viên
    phone               TEXT NOT NULL,                                -- Số điện thoại
    department          TEXT,                                         -- Phòng ban: Kinh doanh, Kỹ thuật, Kho
    title               TEXT,                                         -- Chức danh: NV Bán hàng, Thợ kỹ thuật, Trưởng ca
    login               TEXT UNIQUE,                                  -- Tài khoản đăng nhập hệ thống
    branch_working      TEXT DEFAULT 'Chi nhánh chính',               -- Chi nhánh làm việc
    salary_base         REAL DEFAULT 0.0,                             -- Lương cơ bản
    is_active           INTEGER DEFAULT 1 CHECK(is_active IN (0, 1))
);

CREATE INDEX IF NOT EXISTS idx_employees_department ON DIM_EMPLOYEES(department);

-- ----------------------------------------------------------------------------
-- 3. BẢNG DANH MỤC HÀNG HÓA ĐIỆN MÁY (DIM_PRODUCTS)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS DIM_PRODUCTS (
    product_code        TEXT PRIMARY KEY,                             -- Mã SKU (VD: SP_DIENMAY_001)
    barcode             TEXT UNIQUE,                                  -- Mã vạch sản phẩm
    product_type        TEXT DEFAULT 'Hàng hóa' CHECK(product_type IN ('Hàng hóa', 'Dịch vụ')),
    category_path       TEXT NOT NULL,                                -- Nhóm hàng 3 cấp (VD: Điện lạnh > Máy lạnh > Inverter)
    product_name        TEXT NOT NULL,                                -- Tên sản phẩm
    brand               TEXT NOT NULL,                                -- Thương hiệu (Panasonic, Daikin, Sony, LG...)
    model               TEXT,                                         -- Model kỹ thuật
    uom                 TEXT DEFAULT 'Cái',                           -- Đơn vị tính (Cái, Bộ, Chiếc)
    cost_price          REAL DEFAULT 0.0 CHECK(cost_price >= 0),     -- Giá vốn nhập kho
    sale_price          REAL DEFAULT 0.0 CHECK(sale_price >= 0),     -- Giá bán niêm yết
    stock_on_hand       INTEGER DEFAULT 0 CHECK(stock_on_hand >= 0),  -- Tồn kho khả dụng
    warranty_months     INTEGER DEFAULT 12 CHECK(warranty_months >= 0), -- Thời hạn bảo hành (tháng)
    has_serial_tracking INTEGER DEFAULT 1 CHECK(has_serial_tracking IN (0, 1)), -- 1: Quản lý theo Serial/IMEI, 0: Phụ kiện
    is_active           INTEGER DEFAULT 1 CHECK(is_active IN (0, 1)),
    is_direct_sale      INTEGER DEFAULT 1 CHECK(is_direct_sale IN (0, 1))
);

CREATE INDEX IF NOT EXISTS idx_products_brand ON DIM_PRODUCTS(brand);
CREATE INDEX IF NOT EXISTS idx_products_category ON DIM_PRODUCTS(category_path);
CREATE INDEX IF NOT EXISTS idx_products_barcode ON DIM_PRODUCTS(barcode);

-- ----------------------------------------------------------------------------
-- 4. BẢNG QUẢN LÝ SERIAL / IMEI THIẾT BỊ ĐIỆN MÁY (DIM_PRODUCT_SERIALS)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS DIM_PRODUCT_SERIALS (
    serial_number       TEXT PRIMARY KEY,                             -- Số Serial/IMEI duy nhất của từng cá thể máy
    product_code        TEXT NOT NULL,                                -- Mã sản phẩm SKU
    status              TEXT DEFAULT 'IN_STOCK' CHECK(status IN ('IN_STOCK', 'SOLD', 'DEFECTIVE', 'RETURNED')),
    import_date         TEXT DEFAULT (DATETIME('now', 'localtime')),
    FOREIGN KEY (product_code) REFERENCES DIM_PRODUCTS(product_code) ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_serials_product ON DIM_PRODUCT_SERIALS(product_code);
CREATE INDEX IF NOT EXISTS idx_serials_status ON DIM_PRODUCT_SERIALS(status);

-- ----------------------------------------------------------------------------
-- 5. BẢNG GIAO DỊCH ĐƠN ĐẶT HÀNG (FACT_ORDERS)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS FACT_ORDERS (
    order_code          TEXT PRIMARY KEY,                             -- Mã đơn đặt hàng (VD: DH00001)
    order_time          TEXT NOT NULL,                                -- Thời gian lập đơn đặt
    customer_code       TEXT,                                         -- Mã khách hàng
    seller_code         TEXT,                                         -- Nhân viên tiếp nhận đơn
    total_amount        REAL DEFAULT 0.0 CHECK(total_amount >= 0),    -- Tổng tiền đơn đặt hàng
    deposit_amount      REAL DEFAULT 0.0 CHECK(deposit_amount >= 0),  -- Tiền đặt cọc trước
    amount_due          REAL DEFAULT 0.0,                             -- Số tiền còn lại cần thanh toán
    status              TEXT DEFAULT 'Chờ xử lý' CHECK(status IN ('Chờ xử lý', 'Đang giao hàng', 'Hoàn thành', 'Đã hủy')),
    note                TEXT,
    FOREIGN KEY (customer_code) REFERENCES DIM_CUSTOMERS(customer_code) ON UPDATE CASCADE,
    FOREIGN KEY (seller_code) REFERENCES DIM_EMPLOYEES(employee_code) ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_orders_customer ON FACT_ORDERS(customer_code);
CREATE INDEX IF NOT EXISTS idx_orders_time ON FACT_ORDERS(order_time);

-- ----------------------------------------------------------------------------
-- 6. BẢNG CHI TIẾT ĐƠN ĐẶT HÀNG (FACT_ORDER_LINES)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS FACT_ORDER_LINES (
    order_line_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    order_code          TEXT NOT NULL,
    product_code        TEXT NOT NULL,
    quantity            INTEGER NOT NULL CHECK(quantity > 0),
    unit_price          REAL NOT NULL CHECK(unit_price >= 0),
    discount_amount     REAL DEFAULT 0.0 CHECK(discount_amount >= 0),
    line_total          REAL NOT NULL CHECK(line_total >= 0),
    FOREIGN KEY (order_code) REFERENCES FACT_ORDERS(order_code) ON DELETE CASCADE,
    FOREIGN KEY (product_code) REFERENCES DIM_PRODUCTS(product_code) ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_order_lines_order ON FACT_ORDER_LINES(order_code);
CREATE INDEX IF NOT EXISTS idx_order_lines_product ON FACT_ORDER_LINES(product_code);

-- ----------------------------------------------------------------------------
-- 7. BẢNG GIAO DỊCH HÓA ĐƠN BÁN HÀNG (FACT_INVOICES)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS FACT_INVOICES (
    invoice_code            TEXT PRIMARY KEY,                         -- Mã hóa đơn (Prefix HDIPxxxx theo chuẩn KiotViet)
    invoice_time            TEXT NOT NULL,                            -- Thời gian xuất hóa đơn
    order_code              TEXT,                                     -- Tham chiếu từ đơn đặt trước (nếu có)
    customer_code           TEXT NOT NULL,                            -- Mã khách hàng
    seller_code             TEXT NOT NULL,                            -- Nhân viên bán hàng
    technician_code         TEXT,                                     -- Kỹ thuật viên giao hàng & lắp đặt (nếu có)
    sales_channel           TEXT DEFAULT 'Bán trực tiếp',             -- Kênh bán: Trực tiếp, Online, Showroom
    total_gross_amount      REAL DEFAULT 0.0 CHECK(total_gross_amount >= 0), -- Tổng tiền hàng trước chiết khấu
    invoice_discount_amount REAL DEFAULT 0.0 CHECK(invoice_discount_amount >= 0), -- Giảm giá hóa đơn
    total_net_amount        REAL DEFAULT 0.0 CHECK(total_net_amount >= 0), -- Tiền khách phải trả thực tế
    
    -- Đối soát các kênh thanh toán
    pay_cash                REAL DEFAULT 0.0 CHECK(pay_cash >= 0),
    pay_card                REAL DEFAULT 0.0 CHECK(pay_card >= 0),
    pay_transfer            REAL DEFAULT 0.0 CHECK(pay_transfer >= 0),
    pay_installment         REAL DEFAULT 0.0 CHECK(pay_installment >= 0), -- Trả góp qua đối tác tài chính
    
    note                    TEXT,
    created_at              TEXT DEFAULT (DATETIME('now', 'localtime')),
    FOREIGN KEY (customer_code) REFERENCES DIM_CUSTOMERS(customer_code) ON UPDATE CASCADE,
    FOREIGN KEY (seller_code) REFERENCES DIM_EMPLOYEES(employee_code) ON UPDATE CASCADE,
    FOREIGN KEY (technician_code) REFERENCES DIM_EMPLOYEES(employee_code) ON UPDATE CASCADE,
    FOREIGN KEY (order_code) REFERENCES FACT_ORDERS(order_code) ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_invoices_time ON FACT_INVOICES(invoice_time);
CREATE INDEX IF NOT EXISTS idx_invoices_customer ON FACT_INVOICES(customer_code);
CREATE INDEX IF NOT EXISTS idx_invoices_seller ON FACT_INVOICES(seller_code);

-- ----------------------------------------------------------------------------
-- 8. BẢNG CHI TIẾT HÓA ĐƠN BÁN HÀNG (FACT_INVOICE_LINES)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS FACT_INVOICE_LINES (
    invoice_line_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_code            TEXT NOT NULL,
    product_code            TEXT NOT NULL,
    serial_number           TEXT,                                     -- Serial/IMEI gắn với máy bán ra (nếu có)
    quantity                INTEGER NOT NULL CHECK(quantity > 0),
    unit_price              REAL NOT NULL CHECK(unit_price >= 0),
    line_discount_amount    REAL DEFAULT 0.0 CHECK(line_discount_amount >= 0),
    line_total              REAL NOT NULL CHECK(line_total >= 0),
    warranty_expire_date    TEXT,                                     -- Ngày hết hạn bảo hành của sản phẩm
    FOREIGN KEY (invoice_code) REFERENCES FACT_INVOICES(invoice_code) ON DELETE CASCADE,
    FOREIGN KEY (product_code) REFERENCES DIM_PRODUCTS(product_code) ON UPDATE CASCADE,
    FOREIGN KEY (serial_number) REFERENCES DIM_PRODUCT_SERIALS(serial_number) ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_inv_lines_invoice ON FACT_INVOICE_LINES(invoice_code);
CREATE INDEX IF NOT EXISTS idx_inv_lines_product ON FACT_INVOICE_LINES(product_code);
CREATE INDEX IF NOT EXISTS idx_inv_lines_serial ON FACT_INVOICE_LINES(serial_number);

-- ============================================================================
-- 9. CÁC VIEWS PHÂN TÍCH KINH DOANH & KIỂM TOÁN DỮ LIỆU
-- ============================================================================

-- View 1: Phân tích hiệu quả kinh doanh & Biên lợi nhuận gộp theo Thương hiệu
CREATE VIEW IF NOT EXISTS VIEW_BRAND_PERFORMANCE AS
SELECT 
    p.brand,
    COUNT(DISTINCT il.invoice_code) AS total_invoices,
    COALESCE(SUM(il.quantity), 0) AS total_units_sold,
    ROUND(COALESCE(SUM(il.line_total), 0.0), 2) AS total_revenue,
    ROUND(COALESCE(SUM(il.quantity * p.cost_price), 0.0), 2) AS total_cogs,
    ROUND(COALESCE(SUM(il.line_total) - SUM(il.quantity * p.cost_price), 0.0), 2) AS gross_profit,
    SUM(p.stock_on_hand) AS current_stock_remaining
FROM DIM_PRODUCTS p
LEFT JOIN FACT_INVOICE_LINES il ON p.product_code = il.product_code
GROUP BY p.brand;

-- View 2: Tra cứu tình trạng bảo hành máy theo IMEI/Serial
CREATE VIEW IF NOT EXISTS VIEW_SERIAL_WARRANTY_TRACKING AS
SELECT 
    s.serial_number,
    p.product_code,
    p.product_name,
    p.brand,
    i.invoice_code,
    i.invoice_time AS purchase_date,
    c.customer_name,
    c.phone AS customer_phone,
    il.warranty_expire_date,
    CASE 
        WHEN DATE('now') <= DATE(il.warranty_expire_date) THEN 'Còn hạn bảo hành'
        ELSE 'Hết hạn bảo hành'
    END AS warranty_status
FROM DIM_PRODUCT_SERIALS s
JOIN DIM_PRODUCTS p ON s.product_code = p.product_code
JOIN FACT_INVOICE_LINES il ON s.serial_number = il.serial_number
JOIN FACT_INVOICES i ON il.invoice_code = i.invoice_code
JOIN DIM_CUSTOMERS c ON i.customer_code = c.customer_code;

-- View 3: Doanh số bán hàng theo ngày & cơ cấu thanh toán
CREATE VIEW IF NOT EXISTS VIEW_DAILY_SALES_REPORT AS
SELECT 
    DATE(invoice_time) AS sale_date,
    COUNT(invoice_code) AS total_invoices,
    ROUND(SUM(total_net_amount), 2) AS total_revenue,
    ROUND(SUM(pay_cash), 2) AS total_cash,
    ROUND(SUM(pay_card), 2) AS total_card,
    ROUND(SUM(pay_transfer), 2) AS total_transfer,
    ROUND(SUM(pay_installment), 2) AS total_installment
FROM FACT_INVOICES
GROUP BY DATE(invoice_time);

-- ============================================================================
-- 10. PHÂN HỆ TỔNG QUAN KHO (INVENTORY OVERVIEW & RESERVATION DDL - SRS MOD01)
-- ============================================================================

-- Bảng Danh mục Chi nhánh / Kho hàng
CREATE TABLE IF NOT EXISTS branches (
    branch_id           TEXT PRIMARY KEY,                             -- Mã chi nhánh (VD: BR_KHO_TONG, BR_CAU_GIAY, BR_HA_DONG)
    branch_name         TEXT NOT NULL,                                -- Tên kho / Showroom
    address             TEXT,                                         -- Địa chỉ vật lý
    is_active           INTEGER DEFAULT 1 CHECK(is_active IN (0, 1)), -- 1: Hoạt động, 0: Tạm đóng
    created_at          TEXT DEFAULT (DATETIME('now', 'localtime'))
);

-- Bảng Quản lý Tồn kho chi tiết theo Chi nhánh & SKU (INVENTORIES)
CREATE TABLE IF NOT EXISTS inventories (
    inventory_id        TEXT PRIMARY KEY,                             -- UUID định danh
    branch_id           TEXT NOT NULL,                                -- FK -> branches
    product_code        TEXT NOT NULL,                                -- FK -> DIM_PRODUCTS
    on_hand_qty         INTEGER NOT NULL DEFAULT 0 CHECK(on_hand_qty >= 0),    -- Tồn thực tế
    reserved_qty        INTEGER NOT NULL DEFAULT 0 CHECK(reserved_qty >= 0),   -- Hàng đang giữ chỗ
    in_transit_qty      INTEGER NOT NULL DEFAULT 0 CHECK(in_transit_qty >= 0), -- Hàng đang về từ PO
    atp_qty             INTEGER NOT NULL DEFAULT 0,                            -- Khả dụng = on_hand - reserved
    version             INTEGER NOT NULL DEFAULT 1,                            -- Optimistic Locking version
    last_updated        TEXT DEFAULT (DATETIME('now', 'localtime')),
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id) ON UPDATE CASCADE,
    FOREIGN KEY (product_code) REFERENCES DIM_PRODUCTS(product_code) ON UPDATE CASCADE,
    UNIQUE(branch_id, product_code)
);

CREATE INDEX IF NOT EXISTS idx_inv_branch_product ON inventories(branch_id, product_code);

-- Bảng Chi tiết Giữ chỗ Đơn hàng (INVENTORY_RESERVATIONS - Hỗ trợ Soft Reserve Trả góp 48h)
CREATE TABLE IF NOT EXISTS inventory_reservations (
    reservation_id      TEXT PRIMARY KEY,                             -- UUID mã giữ chỗ
    order_code          TEXT NOT NULL,                                -- FK -> FACT_ORDERS
    branch_id           TEXT NOT NULL,                                -- FK -> branches
    product_code        TEXT NOT NULL,                                -- FK -> DIM_PRODUCTS
    reserved_qty        INTEGER NOT NULL DEFAULT 1 CHECK(reserved_qty > 0),
    reservation_type    TEXT NOT NULL DEFAULT 'FULL_HOLD' CHECK(reservation_type IN ('FULL_HOLD', 'INSTALLMENT_HOLD')),
    status              TEXT NOT NULL DEFAULT 'ACTIVE' CHECK(status IN ('ACTIVE', 'RELEASED', 'FULFILLED')),
    expires_at          TEXT,                                         -- Hạn chót giữ (đối với trả góp là created_at + 48h)
    created_at          TEXT DEFAULT (DATETIME('now', 'localtime')),
    updated_at          TEXT DEFAULT (DATETIME('now', 'localtime')),
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id) ON UPDATE CASCADE,
    FOREIGN KEY (product_code) REFERENCES DIM_PRODUCTS(product_code) ON UPDATE CASCADE,
    FOREIGN KEY (order_code) REFERENCES FACT_ORDERS(order_code) ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_res_status_expires ON inventory_reservations(status, expires_at);
CREATE INDEX IF NOT EXISTS idx_res_branch_product ON inventory_reservations(branch_id, product_code);

-- Bảng Đơn đặt hàng Nhà cung cấp (PURCHASE_ORDERS - Quản lý Hàng đang về In-Transit)
CREATE TABLE IF NOT EXISTS purchase_orders (
    po_id               TEXT PRIMARY KEY,                             -- Mã đơn nhập (VD: PO-2026-001)
    branch_id           TEXT NOT NULL,                                -- FK -> branches nhận hàng
    vendor_name         TEXT NOT NULL,                                -- Nhà cung cấp (Sony, Daikin, LG, Samsung...)
    status              TEXT NOT NULL DEFAULT 'CONFIRMED_IN_TRANSIT' CHECK(status IN ('DRAFT', 'CONFIRMED_IN_TRANSIT', 'COMPLETED', 'CANCELLED')),
    expected_delivery_date TEXT,                                      -- Ngày dự kiến về (EDD)
    note                TEXT,
    created_at          TEXT DEFAULT (DATETIME('now', 'localtime')),
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id) ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_po_branch_status ON purchase_orders(branch_id, status);

-- Bảng Chi tiết Đơn nhập hàng (PO_ITEMS)
CREATE TABLE IF NOT EXISTS po_items (
    po_item_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    po_id               TEXT NOT NULL,
    product_code        TEXT NOT NULL,
    ordered_qty         INTEGER NOT NULL CHECK(ordered_qty > 0),
    unit_cost           REAL NOT NULL CHECK(unit_cost >= 0),
    received_qty        INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (po_id) REFERENCES purchase_orders(po_id) ON DELETE CASCADE,
    FOREIGN KEY (product_code) REFERENCES DIM_PRODUCTS(product_code) ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_po_items_po ON po_items(po_id);

