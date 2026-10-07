"""
KIOTVIET FASHION RETAIL SYNTHETIC DATA GENERATOR (SDV & PYTHON)
================================================================
Mô phỏng dữ liệu bán lẻ thời trang theo chuẩn KiotViet PoS và tuân thủ:
- Rule R1: Tiền tố HDIP cho hóa đơn
- Rule R2: Tồn kho đủ (stock_on_hand >= sold + reserve)
- Rule R3: Cân đối thanh toán, số lượng > 0, unit_price = sale_price
- Rule R4: Toàn vẹn khóa ngoại (Referential Integrity)
Lưu trực tiếp vào CSDL SQLite: data/retail_synthetic.db
"""

import os
import sys

# Ensure UTF-8 output on Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

import random
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from faker import Faker

# Cố định random seed để có thể tái lặp kết quả (Reproducibility)
random.seed(42)
np.random.seed(42)
fake = Faker('vi_VN')

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'retail_synthetic.db'))
SCHEMA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'schema.sql'))

print(f"[*] Target SQLite DB: {DB_PATH}")


def ensure_database():
    """Đảm bảo bảng và cấu trúc schema đã được tạo trong SQLite"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    if os.path.exists(SCHEMA_PATH):
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
    conn.commit()
    conn.close()


def generate_categories():
    """Tạo danh mục ngành hàng thời trang 3 cấp KiotViet"""
    raw_cats = [
        ("Thời trang Nam > Áo Nam > Áo Sơ mi", "Thời trang Nam", "Áo Nam", "Áo Sơ mi"),
        ("Thời trang Nam > Áo Nam > Áo Polo", "Thời trang Nam", "Áo Nam", "Áo Polo"),
        ("Thời trang Nam > Áo Nam > Áo Thun Basic", "Thời trang Nam", "Áo Nam", "Áo Thun Basic"),
        ("Thời trang Nam > Quần Nam > Quần Jeans", "Thời trang Nam", "Quần Nam", "Quần Jeans"),
        ("Thời trang Nam > Quần Nam > Quần Kaki", "Thời trang Nam", "Quần Nam", "Quần Kaki"),
        ("Thời trang Nữ > Đầm Váy > Đầm Công sở", "Thời trang Nữ", "Đầm Váy", "Đầm Công sở"),
        ("Thời trang Nữ > Đầm Váy > Đầm Maxi", "Thời trang Nữ", "Đầm Váy", "Đầm Maxi"),
        ("Thời trang Nữ > Áo Nữ > Áo Kiểu Voan", "Thời trang Nữ", "Áo Nữ", "Áo Kiểu Voan"),
        ("Thời trang Nữ > Quần & Chân váy > Chân váy Chữ A", "Thời trang Nữ", "Quần & Chân váy", "Chân váy Chữ A"),
        ("Phụ kiện > Đồ da > Thắt lưng Da", "Phụ kiện", "Đồ da", "Thắt lưng Da"),
        ("Phụ kiện > Ví & Túi > Ví Da Cầm tay", "Phụ kiện", "Ví & Túi", "Ví Da Cầm tay"),
    ]
    records = []
    for idx, (path, l1, l2, l3) in enumerate(raw_cats, start=1):
        records.append({
            "category_id": idx,
            "category_path": path,
            "category_level1": l1,
            "category_level2": l2,
            "category_level3": l3
        })
    return pd.DataFrame(records)


def generate_employees(n=10):
    """Tạo danh sách nhân viên tư vấn bán hàng & thu ngân"""
    departments = ["Bán hàng", "Bán hàng", "Bán hàng", "Thu ngân", "Kho vận", "Quản lý cửa hàng"]
    branches = ["Chi nhánh Ba Đình", "Chi nhánh Cầu Giấy", "Chi nhánh Hoàn Kiếm"]
    
    records = []
    # Admin mặc định đã có trong seed (NV000)
    for i in range(1, n + 1):
        emp_code = f"NV{i:03d}"
        role = random.choice(departments)
        title = "Chuyên viên tư vấn" if role == "Bán hàng" else ("Thu ngân chính" if role == "Thu ngân" else "Cửa hàng trưởng")
        records.append({
            "employee_code": emp_code,
            "employee_name": fake.name(),
            "phone": fake.phone_number(),
            "department": role,
            "title": title,
            "login_account": f"nv_{emp_code.lower()}",
            "branch_working": random.choice(branches),
            "salary": random.choice([7000000, 8500000, 10000000, 12000000, 15000000]),
            "dob": fake.date_of_birth(minimum_age=20, maximum_age=40).strftime('%Y-%m-%d'),
            "start_date": (datetime.now() - timedelta(days=random.randint(60, 800))).strftime('%Y-%m-%d'),
            "is_active": 1
        })
    return pd.DataFrame(records)


def generate_customers(n=120):
    """Tạo danh sách khách hàng chuẩn KiotViet"""
    areas = ["Hà Nội", "Hồ Chí Minh", "Đà Nẵng", "Hải Phòng", "Cần Thơ"]
    records = []
    
    for i in range(1, n + 1):
        cust_code = f"KH{i:05d}"
        gender = random.choice(["Nam", "Nữ"])
        name = fake.name_male() if gender == "Nam" else fake.name_female()
        area = random.choice(areas)
        records.append({
            "customer_code": cust_code,
            "customer_name": name,
            "customer_type": "Cá nhân" if random.random() > 0.05 else "Doanh nghiệp",
            "phone": fake.phone_number(),
            "gender": gender,
            "dob": fake.date_of_birth(minimum_age=18, maximum_age=60).strftime('%Y-%m-%d'),
            "address": fake.street_address(),
            "area": area,
            "ward": fake.city_prefix() + " " + fake.city(),
            "company": fake.company() if random.random() < 0.1 else None,
            "tax_code": fake.numerify("##########") if random.random() < 0.1 else None,
            "is_active": 1
        })
    return pd.DataFrame(records)


import re

def slugify(text):
    text = str(text).lower()
    text = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', text)
    text = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', text)
    text = re.sub(r'[ìíịỉĩ]', 'i', text)
    text = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', text)
    text = re.sub(r'[ùúụủũưừứựửữ]', 'u', text)
    text = re.sub(r'[ỳýỵỷỹ]', 'y', text)
    text = re.sub(r'[đ]', 'd', text)
    text = re.sub(r'[^a-z0-9]', '', text)
    return text.upper()


def generate_products(df_cats):
    """Tạo ma trận sản phẩm thời trang biến thể (Style -> Size + Color)"""
    styles = [
        {"parent": "AT01", "name": "Áo Thun Cotton Compact", "cat_id": 3, "cat_path": "Thời trang Nam > Áo Nam > Áo Thun Basic", "cost": 110000, "price": 249000, "sizes": ["S", "M", "L", "XL"], "colors": ["Trắng", "Đen", "Xanh Navy", "Be"], "mat": "100% Cotton", "season": "Xuân Hè"},
        {"parent": "AP02", "name": "Áo Polo Pique Phối Bo Cổ", "cat_id": 2, "cat_path": "Thời trang Nam > Áo Nam > Áo Polo", "cost": 160000, "price": 389000, "sizes": ["M", "L", "XL", "XXL"], "colors": ["Trắng", "Xanh Rêu", "Xám Tiêu"], "mat": "CVC Cá sấu", "season": "All-Season"},
        {"parent": "SM03", "name": "Áo Sơ Mi Dài Tay Chống Nhăn", "cat_id": 1, "cat_path": "Thời trang Nam > Áo Nam > Áo Sơ mi", "cost": 210000, "price": 499000, "sizes": ["38", "39", "40", "41", "42"], "colors": ["Trắng", "Xanh Nhạt", "Hồng Phấn"], "mat": "Bamboo Rayon", "season": "Thu Đông"},
        {"parent": "QJ04", "name": "Quần Jeans Slimfit Co Giãn", "cat_id": 4, "cat_path": "Thời trang Nam > Quần Nam > Quần Jeans", "cost": 240000, "price": 550000, "sizes": ["29", "30", "31", "32", "33"], "colors": ["Xanh Đậm", "Xanh Nhạt", "Đen"], "mat": "Denim 98% Cotton 2% Spandex", "season": "All-Season"},
        {"parent": "QK05", "name": "Quần Kaki Dáng Đứng Kháng Nhăn", "cat_id": 5, "cat_path": "Thời trang Nam > Quần Nam > Quần Kaki", "cost": 190000, "price": 460000, "sizes": ["29", "30", "31", "32"], "colors": ["Be", "Xanh Rêu", "Đen"], "mat": "Kaki Cotton", "season": "All-Season"},
        {"parent": "DV06", "name": "Đầm Chữ A Thắt Nơ Eo", "cat_id": 6, "cat_path": "Thời trang Nữ > Đầm Váy > Đầm Công sở", "cost": 270000, "price": 680000, "sizes": ["S", "M", "L"], "colors": ["Đỏ Rượu", "Be Nhạt", "Xanh Pastel"], "mat": "Lụa Chiffon", "season": "Xuân Hè"},
        {"parent": "DM07", "name": "Đầm Maxi Họa Tiết Hoa Nhí", "cat_id": 7, "cat_path": "Thời trang Nữ > Đầm Váy > Đầm Maxi", "cost": 310000, "price": 790000, "sizes": ["S", "M", "L"], "colors": ["Vàng Mù Tạt", "Xanh Biển"], "mat": "Voan Tơ Hàn", "season": "Xuân Hè"},
        {"parent": "AK08", "name": "Áo Kiểu Nữ Cổ Buộc Nơ", "cat_id": 8, "cat_path": "Thời trang Nữ > Áo Nữ > Áo Kiểu Voan", "cost": 140000, "price": 320000, "sizes": ["S", "M", "L"], "colors": ["Trắng Kem", "Hồng Đỗ"], "mat": "Tơ Lụa", "season": "Thu Đông"},
        {"parent": "CV09", "name": "Chân Váy Xếp Ly Công Sở", "cat_id": 9, "cat_path": "Thời trang Nữ > Quần & Chân váy > Chân váy Chữ A", "cost": 150000, "price": 350000, "sizes": ["S", "M", "L"], "colors": ["Đen", "Nâu Tây", "Xám"], "mat": "Tuyết Mưa", "season": "All-Season"},
        {"parent": "TL10", "name": "Thắt Lưng Nam Khóa Tự Động", "cat_id": 10, "cat_path": "Phụ kiện > Đồ da > Thắt lưng Da", "cost": 120000, "price": 290000, "sizes": ["FreeSize"], "colors": ["Đen", "Nâu Đậm"], "mat": "Da Bò Thật", "season": "All-Season"},
        {"parent": "VD11", "name": "Ví Cầm Tay Da Bò Dập Vân", "cat_id": 11, "cat_path": "Phụ kiện > Ví & Túi > Ví Da Cầm tay", "cost": 180000, "price": 420000, "sizes": ["FreeSize"], "colors": ["Đen", "Nâu Bò"], "mat": "Da Sáp", "season": "All-Season"},
    ]
    
    records = []
    for s in styles:
        for sz in s["sizes"]:
            for col in s["colors"]:
                col_code = slugify(col)
                sku = f"{s['parent']}-{col_code}-{sz}"
                barcode = f"893{random.randint(1000000000, 9999999999)}"
                full_name = f"{s['name']} - {col} - Size {sz}"
                records.append({
                    "product_code": sku,
                    "barcode": barcode,
                    "product_name": full_name,
                    "product_type": "Hàng hóa",
                    "parent_code": s["parent"],
                    "category_path": s["cat_path"],
                    "category_id": s["cat_id"],
                    "brand": "GSJ Fashion",
                    "size": sz,
                    "color": col,
                    "material": s["mat"],
                    "season": s["season"],
                    "sale_price": float(s["price"]),
                    "cost_price": float(s["cost"]),
                    "stock_on_hand": 0,  # Sẽ được cập nhật lại theo Rule R2 sau khi sinh giao dịch
                    "min_stock": 5,
                    "max_stock": 200,
                    "uom": "Cái",
                    "is_active": 1,
                    "is_direct_sale": 1
                })
    return pd.DataFrame(records)


def generate_transactions(df_cust, df_emp, df_prod, n_invoices=400, n_orders=200):
    """
    Sinh các bảng Fact (Hóa đơn & Đơn đặt hàng) đáp ứng Rule R1, R2, R3, R4:
    - R1: Tiền tố HDIP cho hóa đơn
    - R3: unit_price = sale_price, cân đối thanh toán, số lượng > 0
    - R4: Khóa ngoại trỏ đúng vào Dimension
    """
    start_date = datetime.now() - timedelta(days=90)
    channels = ["Trực tiếp tại quầy", "Website", "Shopee Mall", "TikTok Shop", "Hotline"]
    channel_weights = [0.55, 0.20, 0.15, 0.07, 0.03]
    
    cust_codes = list(df_cust["customer_code"].values)
    # Khách vãng lai chiếm 20%
    cust_pool = cust_codes + ['KH_BANLE'] * int(len(cust_codes) * 0.25)
    
    emp_codes = list(df_emp["employee_code"].values)
    prod_dict = df_prod.set_index("product_code").to_dict(orient="index")
    prod_keys = list(prod_dict.keys())
    
    # ----------------------------------------------------
    # 1. SINH HÓA ĐƠN (FACT_INVOICES & FACT_INVOICE_LINES)
    # ----------------------------------------------------
    invoices = []
    invoice_lines = []
    line_id = 1
    
    # Tracking số lượng đã bán từng SKU để giải quyết Rule R2
    sku_sold_counter = {sku: 0 for sku in prod_keys}
    
    for i in range(1, n_invoices + 1):
        inv_code = f"HDIP{i:05d}"  # Rule R1
        inv_delta_days = random.randint(0, 89)
        # Mô phỏng phân phối giờ mua sắm (Đỉnh lúc 11-13h và 19-21h)
        hour = random.choices(
            population=list(range(8, 23)),
            weights=[2, 3, 5, 12, 14, 8, 5, 6, 8, 12, 18, 16, 10, 6, 3]
        )[0]
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        inv_time = (start_date + timedelta(days=inv_delta_days)).replace(hour=hour, minute=minute, second=second)
        
        cust_code = random.choice(cust_pool)
        emp_code = random.choice(emp_codes)
        channel = random.choices(channels, weights=channel_weights)[0]
        emp_branch = df_emp.loc[df_emp["employee_code"] == emp_code, "branch_working"].values[0] if emp_code in emp_codes else "Chi nhánh chính"
        
        # Số dòng hàng trong 1 hóa đơn (1 đến 4 món)
        n_items = random.choices([1, 2, 3, 4], weights=[0.55, 0.30, 0.10, 0.05])[0]
        chosen_skus = random.sample(prod_keys, k=n_items)
        
        subtotal = 0.0
        current_lines = []
        for sku in chosen_skus:
            p_info = prod_dict[sku]
            qty = random.choices([1, 2, 3], weights=[0.82, 0.15, 0.03])[0]  # Rule R3: qty > 0
            u_price = float(p_info["sale_price"])                          # Khuyến nghị: unit_price = sale_price
            cost_snap = float(p_info["cost_price"])                        # Snapshot giá vốn
            
            # Khuyến mãi từng món (10% cơ hội giảm 5-15%)
            disc_rate = random.choice([0.0, 0.05, 0.1, 0.15]) if random.random() < 0.2 else 0.0
            disc_amt = round(qty * u_price * disc_rate, -3)
            l_total = (qty * u_price) - disc_amt
            
            subtotal += l_total
            sku_sold_counter[sku] += qty
            
            current_lines.append({
                "invoice_line_id": line_id,
                "invoice_code": inv_code,
                "product_code": sku,
                "quantity": qty,
                "unit_price": u_price,
                "discount_amount": disc_amt,
                "discount_percent": disc_rate * 100.0,
                "line_total": l_total,
                "cost_price_snapshot": cost_snap
            })
            line_id += 1
            
        # Giảm giá hóa đơn (voucher 5-10% nếu tổng trên 1 triệu)
        inv_disc_amt = 0.0
        inv_disc_pct = 0.0
        if subtotal > 1000000 and random.random() < 0.25:
            inv_disc_pct = 5.0
            inv_disc_amt = round(subtotal * 0.05, -3)
            
        net_payable = subtotal - inv_disc_amt
        
        # Cân đối thanh toán (Rule R3)
        pay_type = random.choice(["cash_only", "card_only", "transfer_only", "split"])
        if pay_type == "cash_only":
            p_cash, p_card, p_trans = net_payable, 0.0, 0.0
        elif pay_type == "card_only":
            p_cash, p_card, p_trans = 0.0, net_payable, 0.0
        elif pay_type == "transfer_only":
            p_cash, p_card, p_trans = 0.0, 0.0, net_payable
        else:
            split_cash = round(net_payable * 0.5, -3)
            p_cash = split_cash
            p_card = net_payable - split_cash
            p_trans = 0.0
            
        invoices.append({
            "invoice_code": inv_code,
            "invoice_time": inv_time.strftime('%Y-%m-%d %H:%M:%S'),
            "customer_code": cust_code,
            "employee_code": emp_code,
            "order_code": None,
            "sales_channel": channel,
            "branch_name": emp_branch,
            "pricebook": "Bảng giá chung",
            "total_amount": subtotal,
            "discount_amount": inv_disc_amt,
            "discount_percent": inv_disc_pct,
            "final_amount": net_payable,
            "pay_cash": p_cash,
            "pay_card": p_card,
            "pay_transfer": p_trans,
            "note": "Khách mua tại quầy" if channel == "Trực tiếp tại quầy" else f"Đơn từ kênh {channel}"
        })
        invoice_lines.extend(current_lines)

    # ----------------------------------------------------
    # 2. SINH ĐƠN ĐẶT HÀNG (FACT_ORDERS & FACT_ORDERS_LINES)
    # ----------------------------------------------------
    orders = []
    order_lines = []
    o_line_id = 1
    
    for j in range(1, n_orders + 1):
        ord_code = f"DH{j:05d}"
        ord_delta = random.randint(0, 89)
        ord_time = (start_date + timedelta(days=ord_delta, hours=random.randint(9, 21), minutes=random.randint(0, 59)))
        
        c_code = random.choice(cust_codes) # Đặt hàng luôn có thông tin KH
        e_code = random.choice(emp_codes)
        chan = random.choice(channels)
        
        stt = random.choices(["Hoan_thanh", "Cho_xu_ly", "Dang_giu_hang", "Da_huy"], weights=[0.60, 0.15, 0.15, 0.10])[0]
        
        n_items = random.randint(1, 3)
        chosen_skus = random.sample(prod_keys, k=n_items)
        ord_subtotal = 0.0
        
        for sku in chosen_skus:
            p_info = prod_dict[sku]
            qty = random.randint(1, 2)
            u_price = float(p_info["sale_price"])
            l_total = qty * u_price
            ord_subtotal += l_total
            
            order_lines.append({
                "order_line_id": o_line_id,
                "order_code": ord_code,
                "product_code": sku,
                "quantity": qty,
                "unit_price": u_price,
                "discount_amount": 0.0,
                "discount_percent": 0.0,
                "line_total": l_total
            })
            o_line_id += 1
            
        # Cọc tiền
        if stt == "Hoan_thanh":
            paid = ord_subtotal
        elif stt in ["Cho_xu_ly", "Dang_giu_hang"]:
            paid = round(ord_subtotal * random.choice([0.0, 0.2, 0.5, 1.0]), -3)
        else: # Da_huy
            paid = 0.0
            
        orders.append({
            "order_code": ord_code,
            "order_time": ord_time.strftime('%Y-%m-%d %H:%M:%S'),
            "customer_code": c_code,
            "employee_code": e_code,
            "sales_channel": chan,
            "branch_name": "Chi nhánh Ba Đình",
            "amount_due": ord_subtotal,
            "amount_paid": paid,
            "discount_amount": 0.0,
            "order_status": stt,
            "converted_invoice_code": None,
            "expected_delivery_date": (ord_time + timedelta(days=3)).strftime('%Y-%m-%d'),
            "cancel_reason": "Khách đổi ý muốn lấy màu khác" if stt == "Da_huy" else None,
            "note": "Hẹn lấy tại shop"
        })

    # ----------------------------------------------------
    # 3. HẬU XỬ LÝ QUY TẮC RULE R2 (TỒN KHO ĐỦ)
    # stock_on_hand = Tổng số lượng đã bán + Số lượng dự trữ an toàn (Safety Stock: 20-80 cái)
    # ----------------------------------------------------
    for prod_idx, row in df_prod.iterrows():
        sku = row["product_code"]
        total_sold = sku_sold_counter.get(sku, 0)
        safety_stock = random.randint(20, 60)
        df_prod.at[prod_idx, "stock_on_hand"] = total_sold + safety_stock

    return (
        pd.DataFrame(invoices),
        pd.DataFrame(invoice_lines),
        pd.DataFrame(orders),
        pd.DataFrame(order_lines),
        df_prod
    )


def save_to_sqlite(df_cats, df_cust, df_emp, df_prod, df_inv, df_inv_lines, df_ord, df_ord_lines):
    """Lưu toàn bộ các DataFrame vào CSDL SQLite theo thứ tự cha trước con sau"""
    print(f"[*] Đang ghi dữ liệu vào SQLite ({DB_PATH})...")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Tắt tạm FK khi truncate/insert để tránh lock
    cur.execute("PRAGMA foreign_keys = OFF;")
    
    # Làm sạch bảng trước khi ghi
    tables = [
        "FACT_ORDERS_LINES", "FACT_ORDERS",
        "FACT_INVOICE_LINES", "FACT_INVOICES",
        "DIM_PRODUCTS", "DIM_EMPLOYEES", "DIM_CUSTOMERS", "DIM_CATEGORIES"
    ]
    for tbl in tables:
        cur.execute(f"DELETE FROM {tbl};")
        
    conn.commit()
    
    # 1. Dimensions
    df_cats.to_sql("DIM_CATEGORIES", conn, if_exists="append", index=False)
    df_cust.to_sql("DIM_CUSTOMERS", conn, if_exists="append", index=False)
    # Bổ sung khách bán lẻ nếu chưa có
    cur.execute("INSERT OR IGNORE INTO DIM_CUSTOMERS (customer_code, customer_name, customer_type, is_active) VALUES ('KH_BANLE', 'Khách bán lẻ / Vãng lai', 'Cá nhân', 1);")
    
    df_emp.to_sql("DIM_EMPLOYEES", conn, if_exists="append", index=False)
    cur.execute("INSERT OR IGNORE INTO DIM_EMPLOYEES (employee_code, employee_name, department, title, branch_working, is_active) VALUES ('NV000', 'Quản trị viên', 'Quản trị', 'Admin', 'Chi nhánh chính', 1);")
    
    df_prod.to_sql("DIM_PRODUCTS", conn, if_exists="append", index=False)
    
    # 2. Facts
    df_inv.to_sql("FACT_INVOICES", conn, if_exists="append", index=False)
    df_inv_lines.to_sql("FACT_INVOICE_LINES", conn, if_exists="append", index=False)
    
    df_ord.to_sql("FACT_ORDERS", conn, if_exists="append", index=False)
    df_ord_lines.to_sql("FACT_ORDERS_LINES", conn, if_exists="append", index=False)
    
    cur.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
    conn.close()
    print("[+] Hoàn tất ghi dữ liệu vào SQLite!")


def main():
    print("=== KHỞI TẠO BỘ DỮ LIỆU GIẢ LẬP FASHION RETAIL THEO CHUẨN KIOTVIET ===")
    ensure_database()
    
    print("[1/5] Sinh danh mục phân cấp 3 cấp...")
    df_cats = generate_categories()
    print(f"      -> {len(df_cats)} danh mục.")
    
    print("[2/5] Sinh nhân viên và khách hàng...")
    df_emp = generate_employees(n=12)
    df_cust = generate_customers(n=150)
    print(f"      -> {len(df_emp)} nhân viên, {len(df_cust)} khách hàng.")
    
    print("[3/5] Sinh ma trận sản phẩm thời trang biến thể...")
    df_prod = generate_products(df_cats)
    print(f"      -> {len(df_prod)} SKU biến thể (Size/Color).")
    
    print("[4/5] Sinh hóa đơn, đơn hàng và áp dụng Rules R1 - R4...")
    df_inv, df_inv_lines, df_ord, df_ord_lines, df_prod = generate_transactions(
        df_cust, df_emp, df_prod, n_invoices=500, n_orders=250
    )
    print(f"      -> {len(df_inv)} hóa đơn ({len(df_inv_lines)} dòng chi tiết).")
    print(f"      -> {len(df_ord)} đơn đặt hàng ({len(df_ord_lines)} dòng chi tiết).")
    print(f"      -> Đã hậu xử lý cập nhật tồn kho đủ cho {len(df_prod)} SKU.")
    
    print("[5/5] Lưu trữ dữ liệu vào cơ sở dữ liệu SQLite...")
    save_to_sqlite(df_cats, df_cust, df_emp, df_prod, df_inv, df_inv_lines, df_ord, df_ord_lines)
    
    # Kiểm tra tính toàn vẹn
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM FACT_INVOICES WHERE invoice_code LIKE 'HDIP%';")
    r1_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM VW_CUSTOMER_RFM_RAW;")
    rfm_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM VW_COMMITTED_STOCK_BY_VARIANT;")
    stock_count = cur.fetchone()[0]
    conn.close()
    
    print(f"\n[OK] KIỂM TRA TÍNH TOÀN VẸN:")
    print(f"  - R1 (Tiền tố HDIP): {r1_count}/{len(df_inv)} hóa đơn hợp lệ.")
    print(f"  - View RFM: {rfm_count} khách hàng có lịch sử giao dịch.")
    print(f"  - View Committed Stock: {stock_count} SKU đã tính toán tồn khả dụng.")
    print("\n>>> QUÁ TRÌNH TẠO DỮ LIỆU GIẢ LẬP HOÀN TẤT THÀNH CÔNG! <<<")


if __name__ == '__main__':
    main()
