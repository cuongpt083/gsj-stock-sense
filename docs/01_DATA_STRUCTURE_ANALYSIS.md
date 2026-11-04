# 📊 Phân Tích Cấu Trúc Dữ Liệu Kiotviet - Data Structure Analysis

**Ngày phân tích**: 08-06-2026  
**Nguồn**: 10 file Excel export từ Kiotviet.vn  
**Mục đích**: Xây dựng Data Warehouse cho phân tích khách hàng và gợi ý sản phẩm

---

## 📑 Table of Contents
1. [Tổng quan](#tổng-quan)
2. [Các Entity Chính](#các-entity-chính)
3. [Mối Quan Hệ Giữa Entities](#mối-quan-hệ-giữa-entities)
4. [Entity-Relationship Diagram (ERD)](#entity-relationship-diagram)
5. [Data Mapping](#data-mapping)
6. [Các Cột Quan Trọng Cho RFM & Analytics](#các-cột-quan-trọng)

---

## 🎯 Tổng Quan

Cửa hàng tạp hóa sử dụng Kiotviet.vn để quản lý:
- ✅ **Sản phẩm** (30 loại)
- ✅ **Khách hàng** (5 cá nhân)
- ✅ **Hóa đơn bán hàng** (7 đơn)
- ✅ **Chi tiết hóa đơn** (14 items)
- ✅ **Nhà cung cấp** (5 công ty)
- ✅ **Đơn nhập hàng** (7 đơn)
- ✅ **Chi tiết nhập hàng** (12 items)

**Dữ liệu hiện tại**: 30-50 rows (mẫu nhỏ) → **Cần sinh dữ liệu giả lập** 100 KH, 300 HĐ, 100 SP

---

## 🏗️ Các Entity Chính

### 1️⃣ **PRODUCTS** (Sản Phẩm)
Danh sách tất cả sản phẩm mà cửa hàng bán

**File nguồn**: `DanhSachSanPham_KV*.xlsx` (30 rows, 27 columns)

| Cột | Kiểu | Ý nghĩa | VD |
|-----|------|---------|-----|
| **Mã hàng** | TEXT | 🔑 Định danh sản phẩm | `10225873544` |
| **Tên hàng** | TEXT | Tên sản phẩm | `Bánh mì Staff chà bông 55gr` |
| **Thương hiệu** | TEXT | Hãng sản xuất | `Staff` |
| **Loại hàng** | TEXT | Phân loại | `Hàng hóa` |
| **Nhóm hàng** | TEXT | Phân nhóm 3 cấp | `Bánh, kẹo, snack >> Bánh >> Bánh tươi` |
| **Giá bán** | FLOAT | Giá bán lẻ | `25000.0` |
| **Giá vốn** | FLOAT | Giá nhập (cost) | `15000.0` |
| **Tồn kho** | INT | Số lượng hiện tại | `100` |
| **Mã vạch** | TEXT | Barcode (optional) | `8936075008024` |
| **ĐVT** | TEXT | Đơn vị tính | `Cái`, `Hộp`, `Kg` |
| **Quy đổi** | INT | Tỷ lệ quy đổi ĐVT | `1` |
| **Trạng thái** | INT | 1=Đang bán, 0=Ngừng | `1` |
| **Thời gian tạo** | DATETIME | Khi sản phẩm được thêm | `2026-06-07 22:17:46` |

**Chú thích**:
- **Mã hàng** là **PRIMARY KEY** (định danh duy nhất)
- Giá bán = 0 trong sample (dữ liệu thiếu) → sẽ fill trong synthetic data
- Tồn kho cần cập nhật mỗi khi có hóa đơn mới

---

### 2️⃣ **CUSTOMERS** (Khách Hàng)
Danh sách khách hàng đã mua hàng

**File nguồn**: `DanhSachKhachHang_KV*.xlsx` (5 rows, 24 columns)

| Cột | Kiểu | Ý nghĩa | VD |
|-----|------|---------|-----|
| **Mã khách hàng** | TEXT | 🔑 Định danh khách | `KH000005` |
| **Tên khách hàng** | TEXT | Tên đầy đủ | `Anh Giang - Kim Mã` |
| **Loại khách** | TEXT | Cá nhân hay công ty | `Cá nhân` |
| **Điện thoại** | TEXT | SĐT liên hệ | `0912345678` |
| **Email** | TEXT | Email (RFM gợi ý) | `customer@gmail.com` |
| **Địa chỉ** | TEXT | Địa chỉ giao hàng | `Số 1 Trần Hưng Đạo, HN` |
| **Khu vực giao hàng** | TEXT | Vùng giao hàng | `Hà Nội` |
| **Phường/Xã** | TEXT | Chi tiết địa chỉ | `Hoàn Kiếm` |
| **Ngày sinh** | DATE | Để tính tuổi khách | `1990-05-15` |
| **Giới tính** | TEXT | M/F (segmentation) | `M` |
| **Tổng bán** | FLOAT | 💰 Tổng tiền mua (RFM) | `500000.0` |
| **Nợ cần thu** | FLOAT | Tiền còn nợ | `100000.0` |
| **Ngày tạo** | DATETIME | Khi khách được tạo | `2026-06-07 22:17:47` |
| **Ngày giao dịch cuối** | DATE | ⏰ Lần cuối mua (RFM) | `2026-06-07` |

**Chú thích**:
- **Mã khách hàng** là **PRIMARY KEY**
- Các cột **Tổng bán**, **Ngày giao dịch cuối** rất quan trọng cho **RFM Analysis**
- Email & Điện thoại dùng cho **Zalo integration** (gửi gợi ý sản phẩm)

---

### 3️⃣ **INVOICES** (Hóa Đơn Bán Hàng)
Ghi nhận từng giao dịch bán hàng

**File nguồn**: `DanhSachHoaDon_KV*.xlsx` (7 rows, 8 columns)

| Cột | Kiểu | Ý nghĩa | VD |
|-----|------|---------|-----|
| **Mã hóa đơn** | TEXT | 🔑 Định danh hóa đơn | `HD000046` |
| **Thời gian** | DATETIME | ⏰ Khi bán (RFM) | `2026-06-07 23:00:56` |
| **Mã khách hàng** | TEXT | 🔗 Link tới Customers | `KH000004` |
| **Khách hàng** | TEXT | Tên (denormalized) | `Anh Hoàng - Sài Gòn` |
| **Tổng tiền hàng** | FLOAT | Giá trước giảm | `250000.0` |
| **Giảm giá** | FLOAT | Tiền giảm | `25000.0` |
| **Khách đã trả** | FLOAT | 💵 Tiền khách thanh toán | `225000.0` |
| **Mã trả hàng** | TEXT | Link tới return (nếu có) | `NULL` |

**Chú thích**:
- **Mã hóa đơn** là PRIMARY KEY
- **Mã khách hàng** là FOREIGN KEY → link tới CUSTOMERS table
- **Thời gian** → tính **Recency** (R) trong RFM
- **Khách đã trả** → dùng tính **Monetary** (M) trong RFM

---

### 4️⃣ **INVOICE_ITEMS** (Chi Tiết Hóa Đơn)
Từng sản phẩm trong mỗi hóa đơn

**File nguồn**: `DanhSachChiTietHoaDon_KV*.xlsx` (14 rows, 61 columns)

**Cột Quan Trọng**:

| Cột | Kiểu | Ý nghĩa | VD |
|-----|------|---------|-----|
| **Mã hóa đơn** | TEXT | 🔑 Link tới Invoices | `HD000046` |
| **Mã hàng** | TEXT | 🔑 Link tới Products | `1021023976409` |
| **Tên hàng** | TEXT | Tên sản phẩm | `Sen đá trung` |
| **Số lượng** | INT | Bao nhiêu cái | `1` |
| **Đơn giá** | FLOAT | Giá 1 cái | `50000.0` |
| **Giảm giá %** | INT | % giảm | `0` |
| **Giảm giá** | FLOAT | $ giảm | `0.0` |
| **Giá bán** | FLOAT | Giá sau giảm | `50000.0` |
| **Thành tiền** | FLOAT | Số lượng × Giá bán | `50000.0` |
| **Thời gian** | DATETIME | Khi hóa đơn | `2026-06-07 23:00:56` |
| **Mã khách hàng** | TEXT | 🔗 Link tới Customers | `KH000004` |

**Chú thích**:
- **Composite Primary Key**: `(Mã hóa đơn, Mã hàng)` → một sản phẩm chỉ xuất hiện 1 lần trên hóa đơn
- 2 FOREIGN KEYs: `Mã hóa đơn` (→ INVOICES), `Mã hàng` (→ PRODUCTS)
- **Thành tiền** = Quantity × Unit Price → dùng tính **Market Basket** (Apriori)
- **Mã khách hàng** → dùng tìm khách nào mua những sản phẩm nào

---

### 5️⃣ **VENDORS** (Nhà Cung Cấp)
Các nhà cung cấp hàng hoá

**File nguồn**: `DanhSachNhaCungCap_KV*.xlsx` (5 rows, 18 columns)

| Cột | Kiểu | Ý nghĩa |
|-----|------|---------|
| **Mã nhà cung cấp** | TEXT | 🔑 Định danh NCC |
| **Tên nhà cung cấp** | TEXT | Tên công ty |
| **Điện thoại** | TEXT | SĐT liên hệ |
| **Địa chỉ** | TEXT | Địa chỉ |
| **Tổng mua** | FLOAT | Tổng chi phí mua hàng |
| **Nợ cần trả** | FLOAT | Tiền còn nợ NCC |

**Chú thích**:
- Ít quan trọng cho **customer analytics** (RFM, Apriori)
- Có thể dùng sau cho **supply chain analysis**

---

### 6️⃣ **PURCHASE_ORDERS** (Đơn Nhập Hàng)
Ghi nhận nhập hàng từ nhà cung cấp

**File nguồn**: `DanhSachNhapHang_KV*.xlsx` (7 rows, 6 columns)

| Cột | Kiểu | Ý nghĩa |
|-----|------|---------|
| **Mã nhập hàng** | TEXT | 🔑 Định danh PO |
| **Thời gian** | DATETIME | Khi nhập |
| **Mã nhà cung cấp** | TEXT | 🔗 Link tới Vendors |
| **Nhà cung cấp** | TEXT | Tên (denormalized) |
| **Cần trả NCC** | FLOAT | Tiền phải trả |
| **Trạng thái** | TEXT | `Đã nhập hàng`, `Nháp` |

---

### 7️⃣ **PO_ITEMS** (Chi Tiết Nhập Hàng)
Từng sản phẩm trong mỗi đơn nhập hàng

**File nguồn**: `DanhSachChiTietNhapHang_KV*.xlsx` (12 rows, 32 columns)

| Cột | Kiểu | Ý nghĩa |
|-----|------|---------|
| **Mã nhập hàng** | TEXT | 🔑 Link tới POs |
| **Mã hàng** | TEXT | 🔗 Link tới Products |
| **Số lượng** | INT | Bao nhiêu cái nhập |
| **Đơn giá** | FLOAT | Giá nhập 1 cái |
| **Thành tiền** | FLOAT | Số lượng × Giá nhập |

---

## 🔗 Mối Quan Hệ Giữa Entities

```
CUSTOMERS
    ↑
    | (1 khách hàng : n hóa đơn)
    ↓
INVOICES ← VENDORS (thông qua POs)
    ↑
    | (1 hóa đơn : n chi tiết)
    ↓
INVOICE_ITEMS
    ↑
    | (n chi tiết : 1 sản phẩm)
    ↓
PRODUCTS
    ↑
    | (1 sản phẩm : n chi tiết nhập)
    ↓
PO_ITEMS
    ↑
    | (n chi tiết : 1 đơn nhập)
    ↓
PURCHASE_ORDERS
    ↑
    | (1 đơn nhập : 1 NCC)
    ↓
VENDORS
```

---

## 📐 Entity-Relationship Diagram (ERD)

```
┌─────────────┐              ┌──────────────┐
│  CUSTOMERS  │──1─────┬──n──│   INVOICES   │
├─────────────┤        │     ├──────────────┤
│ Mã KH (PK)  │        │     │ Mã HĐ (PK)   │
│ Tên KH      │        │     │ Mã KH (FK)   │
│ Điện thoại  │        │     │ Thời gian    │
│ Email       │        │     │ Tổng tiền    │
│ Tổng bán    │        │     │ Khách đã trả │
│ Ngày GD cuối│        │     └──────────────┘
└─────────────┘        │              │
                       │         1────┼────n
                       │              │
                       │     ┌────────┴────────┐
                       │     │ INVOICE_ITEMS   │
                       │     ├─────────────────┤
                       │     │ Mã HĐ (PK/FK)   │
                       │     │ Mã hàng (PK/FK) │
                       │     │ Số lượng        │
                       │     │ Đơn giá         │
                       │     │ Thành tiền      │
                       │     └────────────────┬┘
                       │                    │
                       │                1───┤───n
                       │                    │
                       │          ┌─────────┴──────┐
                       │          │    PRODUCTS    │
                       │          ├────────────────┤
                       │          │ Mã hàng (PK)   │
                       │          │ Tên hàng       │
                       │          │ Thương hiệu    │
                       │          │ Giá bán        │
                       │          │ Giá vốn        │
                       │          │ Tồn kho        │
                       │          └────────────────┘

┌─────────────┐        ┌──────────────┐        ┌────────────┐
│   VENDORS   │─1──┬──n│PURCHASE_ORDERS│─1──┬──n│  PO_ITEMS  │
├─────────────┤    │   ├──────────────┤    │   ├────────────┤
│ Mã NCC (PK) │    │   │ Mã PO (PK)   │    │   │ Mã PO (FK) │
│ Tên NCC     │    │   │ Mã NCC (FK)  │    │   │ Mã hàng(FK)│
│ Điện thoại  │    │   │ Thời gian    │    │   │ Số lượng   │
│ Địa chỉ     │    │   │ Cần trả      │    │   │ Đơn giá    │
│ Tổng mua    │    │   └──────────────┘    │   └────────────┘
└─────────────┘    │                       │
                   │                    1──┼───n
                   │                       │
                   │              ┌────────┴──────┐
                   │              │    PRODUCTS   │
                   │              └────────────────┘
```

---

## 🗂️ Data Mapping

### Mapping: Kiotviet Columns → SQLite Tables

| Kiotviet File | Columns | → | SQLite Table | Notes |
|---------------|---------|---|--------------|-------|
| DanhSachSanPham | Mã hàng, Tên hàng, Giá bán, ... | → | PRODUCTS | Core product catalog |
| DanhSachKhachHang | Mã KH, Tên, Tổng bán, Ngày GD cuối | → | CUSTOMERS | RFM analysis foundation |
| DanhSachHoaDon | Mã HĐ, Mã KH, Tổng tiền, Khách trả | → | INVOICES | Transaction records |
| DanhSachChiTietHoaDon | Mã HĐ, Mã hàng, Số lượng, Thành tiền | → | INVOICE_ITEMS | Market basket analysis |
| DanhSachNhaCungCap | Mã NCC, Tên NCC, ... | → | VENDORS | Supplier management |
| DanhSachNhapHang | Mã PO, Mã NCC, Thời gian | → | PURCHASE_ORDERS | Inventory inbound |
| DanhSachChiTietNhapHang | Mã PO, Mã hàng, Số lượng | → | PO_ITEMS | Stock tracking |

---

## 💡 Các Cột Quan Trọng Cho RFM & Analytics

### **RFM Analysis** (Recency, Frequency, Monetary)
- **Recency (R)**: `INVOICES.Thời gian` → Lần gần nhất mua
- **Frequency (F)**: `COUNT(DISTINCT Mã HĐ)` per customer → Số lần mua
- **Monetary (M)**: `INVOICES.Khách đã trả` → Tổng tiền đã mua

### **Market Basket / Apriori**
- `INVOICE_ITEMS.Mã hàng` + `INVOICE_ITEMS.Mã hóa đơn` → Tìm sản phẩm thường mua cùng

### **Product Analytics**
- `INVOICE_ITEMS.Số lượng` × `INVOICE_ITEMS.Đơn giá` → Doanh thu từng sản phẩm
- `PRODUCTS.Giá bán` - `PRODUCTS.Giá vốn` → Lợi nhuận

### **Customer Segmentation**
- `CUSTOMERS.Tổng bán` → Khách hàng cao giá trị
- `CUSTOMERS.Ngày giao dịch cuối` → Khách hàng còn hoạt động?

---

## 📝 Tóm Tắt

| Aspect | Detail |
|--------|--------|
| **Entities** | 7 (Products, Customers, Invoices, Invoice_Items, Vendors, POs, PO_Items) |
| **Total Rows** | ~51 rows (sample data) |
| **Primary Keys** | 7 unique identifiers |
| **Foreign Keys** | 6 relationships |
| **For RFM** | ✅ Customers, Invoices |
| **For Apriori** | ✅ Invoice_Items |
| **For Dashboard** | ✅ All entities |

Tiếp theo → **Task 2: Tạo SQLite schema + Synthetic data pipeline**

