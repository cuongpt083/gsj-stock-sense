# Báo Cáo Triển Khai Prototype Toàn Chuỗi Màn Hình MVP Bằng Stitch MCP
**Hệ Thống**: GSJ Stock Sense - Smart Inventory Intelligence  
**Đặc thù ngành**: Kho vận & Bán lẻ Điện máy (Consumer Electronics & Retail Warehouse)  
**Thời gian hoàn thành**: 08/11/2026  
**Công cụ MCP sử dụng**: `stitch` (Stitch MCP Engine với model `GEMINI_3_8_FLASH`)

---

## 1. Thông Tin Dự Án Trên Stitch Cloud

- **Tên Dự Án (Project Title)**: `GSJ Stock Sense`
- **Project ID**: `4648531737199118477` (Tên tài nguyên: `projects/4648531737199118477`)
- **Design System Áp Dụng**: `assets/7b5f117fe92d41edb27860f6473c49c5`
  - *Tên Design System*: **Industrial Inventory Telemetry**
  - *Ngôn ngữ thiết kế*: Industrial Flat Design, khung viền kỹ thuật 1px sắc nét (`#E2E8F0` / `#334155`), bảng số liệu mono `JetBrains Mono`, hiển thị sắc thái telemetry (Stock Emerald, Logistics Blue, Warning Amber, Crimson Red).
  - *Phông chữ*: Header (`Inter`), Nội dung tiếng Việt (`Be Vietnam Pro`), Dữ liệu số & mã kho (`JetBrains Mono`).

---

## 2. Danh Sách Chuỗi Màn Hình MVP Đã Tạo

| STT | Tên Màn Hình & Phân Hệ | Thiết Bị | Screen ID | File HTML Tải Về | Đặc Tả Nghiệp Vụ Chính |
|---|---|---|---|---|---|
| **01** | **Tổng Quan Kho & ATP Telemetry** (Module 01 - Executive & Ops) | `DESKTOP` (2560x2048) | `99f739f2a64c4221a4ddaf8f9c624af4` | [`01_tong_quan_kho_executive.html`](file:///c:/Users/Admin/Workspaces/gsj-stock-sense/docs/stitch_prototypes/01_tong_quan_kho_executive.html) | Báo cáo 3 phút cho Giám Đốc Kho Vận; Phân tích mâu thuẫn Doanh thu vs Tồn ảo; Tồn thực tế vs Khả dụng ATP; Modal giải phóng đơn trả góp treo > 48h. |
| **02** | **Hàng Cần Xử Lý Hôm Nay** (Module 02 - Urgent Actions Hub) | `DESKTOP` (2560x2048) | `49e7b65ddf144b03a6212a0168acfa53` | [`02_can_xu_ly_hom_nay.html`](file:///c:/Users/Admin/Workspaces/gsj-stock-sense/docs/stitch_prototypes/02_can_xu_ly_hom_nay.html) | 4 nhóm rủi ro: Deadstock/Ngừng bán (14 SKU), Bán chậm >60 ngày (48 SKU), Cuối vụ máy lạnh (22 SKU), Cạn kho <3 ngày (9 SKU); Bảng Smart Action Grid kèm thanh thao tác hàng loạt cố định. |
| **03** | **Gợi Ý Xả Hàng & Kịch Bản Khuyến Mại** (Module 03 - Liquidation & Pricing) | `DESKTOP` (2560x3146) | `5e01898372e44593bc8d1813a6d2e7b5` | [`03_goi_y_xa_hang.html`](file:///c:/Users/Admin/Workspaces/gsj-stock-sense/docs/stitch_prototypes/03_goi_y_xa_hang.html) | Mô phỏng 3 kịch bản xả (Flash sale lẻ, Bán sỉ đại lý B2B, Combo quà tặng); So sánh giá thị trường đối thủ trực tiếp (Điện Máy Xanh, Nguyễn Kim); Đề xuất giá xả bảo toàn vốn và biên lãi. Nút đồng bộ sang POS KiotViet. |
| **04** | **Đề Xuất Nhập Hàng Thông Minh** (Module 04 - Smart Replenishment & PO) | `DESKTOP` (2560x4282) | `6d861cec218442fe937ebb7ef4597f2c` | [`04_de_xuat_nhap_hang.html`](file:///c:/Users/Admin/Workspaces/gsj-stock-sense/docs/stitch_prototypes/04_de_xuat_nhap_hang.html) | Trực quan hóa công thức MRP minh bạch: `[PO Qty] = [Dự báo 30N] - [ATP] - [In-transit] + [Buffer]`; Bảng 18 SKU cần đặt với 5 nhà cung cấp chính (LG, Daikin, Casper, Sony, Philips); Thanh gom đơn phát hành PO đồng bộ KiotViet. |
| **05 & 06** | **Chăm Sóc Khách Hàng Bán Kèm & Báo Cáo ROI** (Module 05 & 06 - Retention & ROI) | `DESKTOP` (2560x3012) | `544a56cdeb8340f7b0abb5676f8654d9` | [`05_cham_soc_kh_va_roi.html`](file:///c:/Users/Admin/Workspaces/gsj-stock-sense/docs/stitch_prototypes/05_cham_soc_kh_va_roi.html) | 3 Triggers tự động (Điều hòa >6 tháng, TV OLED >30 ngày, Máy giặt >3 tháng); Tích hợp gửi Zalo ZNS / SMS 1-click; Biểu đồ thu hồi vốn lũy kế 2.15 tỷ / 2.85 tỷ (75.4%), ROI +18.4% và khuyến nghị tái đầu tư. |
| **06 (Field)** | **Màn Hình Thực Địa Thủ Kho - Soạn Hàng & Giải Phóng Đơn Treo** (Rugged Tablet View) | `TABLET` (1024x768 cảm ứng) | `bad4889fb8c44e31bf7df4289521bb32` | [`06_tablet_thu_kho_thuc_dia.html`](file:///c:/Users/Admin/Workspaces/gsj-stock-sense/docs/stitch_prototypes/06_tablet_thu_kho_thuc_dia.html) | Thiết kế cho máy tính bảng công nghiệp / iPad cầm tay tại Dock kho; Phân quyền ẩn giá vốn (`*** đ`); Touch targets $\ge 44\text{px}$ hỗ trợ găng tay bảo hộ; Định vị vị trí kệ Bin (`A04-R02-B11`); Modal cảm ứng lớn giải phóng 5 đơn trả góp quá hạn 48h. |

---

## 3. Cách Thức Trải Nghiệm Prototype Trực Tiếp

### Cách 1: Sử dụng cổng duyệt trung tâm Hub Preview
Mở tệp HTML trung tâm [docs/stitch_prototypes/index.html](file:///c:/Users/Admin/Workspaces/gsj-stock-sense/docs/stitch_prototypes/index.html) bằng trình duyệt (Chrome, Edge). Giao diện này cung cấp thanh điều hướng chuyển đổi mượt mà giữa cả 6 màn hình (tự động co kích thước phù hợp giữa Desktop và Tablet).

### Cách 2: Mở từng màn hình độc lập
Người dùng có thể nhấp chuột trực tiếp vào từng tệp `.html` trong thư mục `docs/stitch_prototypes/`:
- `01_tong_quan_kho_executive.html`
- `02_can_xu_ly_hom_nay.html`
- `03_goi_y_xa_hang.html`
- `04_de_xuat_nhap_hang.html`
- `05_cham_soc_kh_va_roi.html`
- `06_tablet_thu_kho_thuc_dia.html`

---

## 4. Kiểm Tra & Tuân Thủ Chuẩn Thiết Kế

1. **Nhất quán thẩm mỹ (Design System Consistency)**:
   - 100% các màn hình sử dụng chung `DesignSystem ID`: `assets/7b5f117fe92d41edb27860f6473c49c5`.
   - Màu sắc theo đúng chuẩn: Slate 900/800 cho khung điều khiển, viền 1px sắc nét `#E2E8F0`, màu trạng thái tương phản cao (Stock Emerald `#059669`, Logistics Blue `#2563EB`, Warning Amber `#D97706`, Crimson Red `#DC2626`).
2. **Khả dụng số liệu & Thuật ngữ ngành điện máy**:
   - Sử dụng các mã hàng điện máy thực tế (Tivi Samsung OLED 65\", Điều hòa Casper Inverter, Máy giặt lồng ngang LG AI DD, Tủ lạnh Toshiba...).
   - Chỉ số nghiệp vụ: ATP (Available-to-Promise), DOH (Days on Hand), In-transit inbound, Run-rate 30 ngày, Margin gộp, Lead-time nhà cung cấp.
3. **Phân quyền và bảo mật**:
   - Màn hình Executive & Quản lý: Hiển thị đầy đủ biên lãi, giá vốn, ROI dòng tiền.
   - Màn hình Thủ kho (Tablet): Ẩn giá vốn (`*** đ`), tối ưu kích thước nút bấm cảm ứng cho thao tác găng tay tại kho.
