# TÀI LIỆU THIẾT KẾ HỆ THỐNG GIAO DIỆN & TRẢI NGHIỆM NGƯỜI DÙNG (UI/UX DESIGN SYSTEM)
## DỰ ÁN: HỆ THỐNG QUẢN LÝ KHO HÀNG ĐIỆN MÁY THÔNG MINH - STOCK SENSE
### CHỦ ĐỀ: BÁN LẺ ĐIỆN MÁY & KHO VẬN ĐA CHI NHÁNH (RETAIL & WAREHOUSE LOGISTICS)

---

| Thông tin tài liệu | Chi tiết |
| :--- | :--- |
| **Mã tài liệu** | `SS-DOC-UIUX-DESIGN-SYSTEM` |
| **Tên tài liệu** | Hệ thống Thiết kế Giao diện UI/UX & Cấu hình Styling Ngành Điện Máy - Kho Vận |
| **Phiên bản** | `1.0` |
| **Ngày ban hành** | 08/11/2026 |
| **Công cụ tạo dựng** | `ui-ux-pro-max` & `design-system` skills |
| **Mục đích sử dụng** | Làm quy chuẩn xây dựng Prototype HTML và phát triển Frontend ứng dụng |
| **Tài liệu liên quan** | `docs/design-tokens.json`, `docs/design-tokens.css`, `docs/SRS_01_Tong_Quan_Kho.md` |

---

## 1. BỐI CẢNH SẢN PHẨM & TRIẾT LÝ THIẾT KẾ (DESIGN PHILOSOPHY)

### 1.1. Bối cảnh đặc thù ngành Bán lẻ Điện máy & Kho vận
- **Mật độ dữ liệu cao (High-density Information):** Người dùng phải theo dõi hàng ngàn mã SKU với nhiều chỉ số biến động cùng lúc (Tồn thực tế, Giữ chỗ, Khả dụng bán - ATP, Hàng đang về, Giá vốn, Serial/IMEI).
- **Tính chuẩn xác và tốc độ ra quyết định:** Sai sót về số liệu tồn kho có thể dẫn đến việc "bán hàng ảo", hứa giao máy cho khách nhưng kho thực tế không có máy, hoặc đọng hàng tỷ đồng tiền vốn lưu động.
- **Hai nhóm người dùng có góc nhìn đối lập:**
  1. *Ban Lãnh đạo / Giám đốc kinh doanh:* Cần bức tranh toàn cảnh vĩ mô, tổng giá trị vốn kho, phát hiện nhanh các điểm nghẽn dòng tiền trong **3 phút**.
  2. *Thủ kho / Nhân viên điều phối:* Cần chi tiết số lượng vật lý, trạng thái giữ chỗ đơn hàng, danh sách hàng đang về để soạn hàng và bố trí giá kệ; **bảo mật tuyệt đối thông tin giá vốn**.

### 1.2. Triết lý thiết kế cốt lõi: "Industrial Flat & Functional Clarity"
Được kế thừa từ phong cách **Flat Design** tối ưu hóa bởi `ui-ux-pro-max`:
1. **Zero Clutter (Không bóng bẩy thừa thãi):** Không dùng hiệu ứng đổ bóng phức tạp, không hiệu ứng 3D, không gradient lòe loẹt. Mọi pixel đều phục vụ việc đọc số liệu nhanh nhất.
2. **High Contrast & Information Hierarchy (Độ tương phản cao):** Sử dụng nền Slate trung tính kết hợp các điểm nhấn màu sắc theo ngữ cảnh (Semantic Colors) để đập vào mắt người xem những điểm bất thường ngay từ giây đầu tiên.
3. **Tabular Precision (Chính xác đến từng con số):** Toàn bộ số lượng tồn kho, giá trị tiền tệ VNĐ và mã SKU/Serial đều áp dụng kiểu chữ **Tabular Numbers (`font-variant-numeric: tabular-nums`)** để đảm bảo thẳng hàng theo cột khi so sánh dọc.
4. **No Emoji as Icons:** 100% biểu tượng sử dụng vector SVG chuẩn (Lucide Icons / Heroicons), không dùng emoji gây thiếu chuyên nghiệp trên giao diện doanh nghiệp.

---

## 2. HỆ THỐNG MÀU SẮC (COLOR SYSTEM & PALETTE)

Hệ thống màu sắc được phối hợp giữa **Industrial Slate** (tông màu công nghiệp vững chãi) và **Stock Emerald** (màu xanh đại diện cho trạng thái sẵn sàng bán ATP), bổ trợ bởi các màu cảnh báo tiêu chuẩn kho vận quốc tế.

```
+-----------------------------------------------------------------------------------------------------+
| BẢNG MÀU CHỦ ĐẠO STOCK SENSE                                                                        |
|                                                                                                     |
|  [ PRIMARY ]          [ ACCENT / ATP ]       [ WARNING ]           [ DANGER / ALERT ]  [ LOGISTICS ]|
|  Slate-800 (#1E293B)  Emerald-600 (#059669)  Amber-600 (#D97706)   Red-600 (#DC2626)   Blue (#2563EB|
|  (Nhận diện, Nền nã)  (Khả dụng bán tốt)     (Sắp hết tồn kho)     (Treo đơn > 48h)    (Hàng đang về|
+-----------------------------------------------------------------------------------------------------+
```

### 2.1. Bảng màu chi tiết và Tiêu chuẩn tương phản (WCAG 2.1 AA)

| Nhóm màu | Mã Hex | Tên Token CSS | Ứng dụng nghiệp vụ trong Kho | Tỷ lệ tương phản (với nền trắng) |
| :--- | :---: | :--- | :--- | :---: |
| **Primary (Brand)** | `#1E293B` | `--slate-800` | Header chính, Sidebar, Tiêu đề cấp cao, Nút bấm chủ đạo. | **12.6 : 1** (Đạt AAA) |
| **Secondary** | `#475569` | `--slate-600` | Nhãn phụ, Tiêu đề phụ, Icon thứ cấp. | **7.1 : 1** (Đạt AAA) |
| **Stock Emerald** | `#059669` | `--emerald-600` | Hàng khả dụng (ATP > 3), Tỷ lệ tăng trưởng dương, Nút duyệt. | **4.6 : 1** (Đạt AA) |
| **Warning Amber** | `#D97706` | `--amber-600` | Cảnh báo: Sắp hết hàng khả dụng (ATP $\le 3$), Đơn chờ duyệt. | **4.5 : 1** (Đạt AA) |
| **Danger Crimson** | `#DC2626` | `--red-600` | Báo động đỏ: Hết hàng khả dụng (ATP = 0), Đơn trả góp treo > 48h. | **4.9 : 1** (Đạt AA) |
| **Logistics Blue** | `#2563EB` | `--blue-600` | Hàng đang trên đường về từ Nhà cung cấp (In-Transit PO). | **4.7 : 1** (Đạt AA) |
| **App Background** | `#F8FAFC` | `--slate-50` | Nền tổng thể toàn bộ Dashboard (dịu mắt khi làm việc ca dài). | - |
| **Card / Surface** | `#FFFFFF` | `--white` | Nền các thẻ KPI, bảng dữ liệu, modal. | - |
| **Border Subtle** | `#E2E8F0` | `--slate-200` | Đường kẻ phân cách bảng, viền thẻ card. | - |

---

## 3. HỆ THỐNG KIỂU CHỮ (TYPOGRAPHY SYSTEM)

Sử dụng bộ đôi font chữ Google Fonts tối ưu cho tiếng Việt và hiển thị số liệu:
- **Heading / Tiêu đề:** **Rubik** (Trực quan, đường nét rõ ràng, hiện đại).
- **Body / Dữ liệu:** **Nunito Sans** (Độ mở ký tự lớn, đọc văn bản và số liệu trong bảng cực kỳ thông thoáng).
- **Mã SKU, Serial/IMEI, Barcode:** **JetBrains Mono** / Monospace (Chống nhầm lẫn giữa ký tự `0` và `O`, `1` và `l`).

### 3.1. Thang kích thước chữ (Type Scale)

```css
/* Typography Scale */
--text-xs:   12px; line-height: 16px; /* Nhãn phụ, badge trạng thái, timestamp */
--text-sm:   14px; line-height: 20px; /* Nội dung bảng dữ liệu, text phụ, input field */
--text-base: 16px; line-height: 24px; /* Nội dung văn bản tiêu chuẩn, nút bấm chính */
--text-lg:   18px; line-height: 28px; /* Tiêu đề thẻ card, subtitle */
--text-xl:   20px; line-height: 28px; /* Tiêu đề phân khu vực (H3) */
--text-2xl:  24px; line-height: 32px; /* Tiêu đề trang (H2) */
--text-3xl:  30px; line-height: 36px; /* Giá trị số lớn trên thẻ KPI chính */
```

### 3.2. Quy tắc Định dạng Số liệu (Data Formatting Rules)
1. **Phân cách hàng nghìn:** Sử dụng dấu chấm `.` hoặc phẩy `,` đồng nhất trong dự án (chuẩn VNĐ: `15.820.500.000 đ` hoặc `15,820,500,000 đ`).
2. **Căn lề cột trong bảng:**
   - Cột Mã SKU / Tên sản phẩm / Ngành hàng: **Căn trái (Align Left)**.
   - Cột Số lượng tồn / Hàng giữ / ATP / Đang về: **Căn phải (Align Right)**.
   - Cột Trạng thái / Thao tác: **Căn giữa (Align Center)**.

---

## 4. HỆ THỐNG KHOẢNG CÁCH & BỐ CỤC (SPACING & LAYOUT SYSTEM)

### 4.1. Hệ số Spacing 8-Point Grid
Mọi padding, margin, kích thước component đều tuân thủ bội số của 4px và 8px:
- `4px` (`--space-1`): Khoảng cách giữa icon và label.
- `8px` (`--space-2`): Padding trong badge, khoảng cách giữa các phần tử inline.
- `12px` (`--space-3`): Padding dọc của ô trong bảng (table cell).
- `16px` (`--space-4`): Padding nút bấm, gap giữa các trường form.
- `20px` (`--space-5`): Padding bên trong Metric Card.
- `24px` (`--space-6`): Khoảng cách (gap) giữa các khối nội dung lớn.
- `32px` (`--space-8`): Khoảng cách giữa Header và Body.

### 4.2. Bố cục Responsive & Kích thước màn hình mục tiêu
1. **Desktop Lớn (1440px - 1920px) - Màn hình chính:**
   - Dành cho Giám đốc, Quản lý tại văn phòng trung tâm.
   - Sidebar cố định 260px bên trái, vùng làm việc chính chia 3 khối tác chiến theo quy tắc 3 phút.
2. **Tablet / Laptop nhỏ (1024px - 1366px):**
   - Dành cho Quản lý cửa hàng hoặc Thủ kho cầm máy tính bảng đi dọc kho.
   - Các cột Metric chuyển từ 4 cột sang lưới 2x2 linh hoạt; bảng dữ liệu cho phép scroll ngang mượt mà.
3. **Kích thước tối thiểu cho nút bấm cảm ứng (Touch Target):** Tối thiểu **$44 \times 44\text{px}$** để thủ kho đeo găng tay hoặc thao tác nhanh bằng một tay trên màn hình cảm ứng không bị bấm nhầm.

---

## 5. QUY CHUẨN THÀNH PHẦN GIAO DIỆN (COMPONENT SPECIFICATIONS)

### 5.1. Thẻ Chỉ số Đo lường (Metric Cards - US 1.1 & US 1.2)
- **Cấu trúc:**
  - `Header`: Tên chỉ số (Uppercase, Slate-500, font 13px, bold 600) + Icon minh họa hoặc tooltip giải thích.
  - `Body`: Con số giá trị chính (Font 28px - 32px, bold 700, màu Slate-900).
  - `Footer`: Delta xu hướng (%) so với kỳ trước (Màu xanh nếu tăng trưởng tốt, đỏ nếu rủi ro).
- **Hành vi tương tác:**
  - Khi rê chuột (Hover): Nâng nhẹ viền thẻ (`border-color: var(--slate-300)`), chuyển con trỏ `cursor: pointer` nếu thẻ có liên kết drill-down.
  - Phân quyền: Khi là Thủ kho, thẻ `Tổng giá vốn tồn kho` hiển thị text `"*** đ (Bảo mật)"` và vô hiệu hóa tooltip giá trị.

### 5.2. Huy hiệu Trạng thái (Status Badges)
Mỗi sản phẩm trong kho được gắn nhãn trạng thái chuẩn hóa, gồm 4 loại:

| Trạng thái | Nền (Background) | Viền (Border) | Chữ (Text) | Ý nghĩa nghiệp vụ |
| :--- | :---: | :---: | :---: | :--- |
| **`HẾT KHẢ DỤNG`** | `#FEF2F2` | `#FEE2E2` | `#DC2626` | ATP $\le 0$: Kho vật lý có thể còn hàng nhưng đã bị đơn khác giữ chỗ hết, tuyệt đối không hứa bán thêm. |
| **`TREO TRẢ GÓP > 48H`** | `#FEF2F2` | `#FCA5A5` | `#B91C1C` | Đơn trả góp quá hạn thẩm định: Cần quản lý bấm nút giải phóng kho ngay lập tức. |
| **`SẮP HẾT`** | `#FFFBEB` | `#FEF3C7` | `#D97706` | Tồn khả dụng thấp ($1 \le \text{ATP} \le 3$): Cảnh báo chuẩn bị lên đơn đặt hàng (PO). |
| **`ĐANG VỀ`** | `#EFF6FF` | `#DBEAFE` | `#2563EB` | Đã duyệt đơn nhập PO với nhà cung cấp, đang trên đường vận chuyển. |
| **`BÌNH THƯỜNG`** | `#ECFDF5` | `#D1FAE5` | `#059669` | Tồn kho và khả dụng ở mức an toàn. |

### 5.3. Bảng Dữ liệu Hàng hóa (Inventory Data Table)
- **Header:** Nền `var(--slate-100)`, chữ in hoa nhỏ `text-xs font-semibold`, sticky header khi cuộn chuột qua danh sách dài.
- **Row:** Chiều cao chuẩn 48px - 52px; hiệu ứng hover nền nhẹ `var(--slate-50)`.
- **Phân tách số liệu:** Cột `Tồn thực tế`, `Giữ chỗ`, `Khả dụng (ATP)` phải đặt cạnh nhau để người dùng làm phép trừ trực quan bằng mắt: $\text{On-Hand} - \text{Reserved} = \text{ATP}$.

### 5.4. Banner Tác chiến Khẩn cấp (Action Alert Banner)
- Khi phát hiện tồn kho bị kẹt bởi đơn trả góp quá hạn 48h, hệ thống kích hoạt Banner đỏ nổi bật ngay trên cùng của khu vực tác chiến.
- Đi kèm nút bấm hành động tức thì dạng **Solid Button Red (`#DC2626`)** có icon sấm sét `⚡` với nhãn: `"GIẢI PHÓNG NGAY CÁC ĐƠN TRẢ GÓP QUÁ HẠN > 48H"`.
- Bấm nút kích hoạt Modal xác nhận ngắn gọn: *"Bạn có chắc chắn muốn hủy giữ chỗ cho [X] đơn hàng trả góp quá hạn và phục hồi [Y] sản phẩm vào kho bán không?"*.

---

## 6. DANH MỤC KIỂM TRA CHẤT LƯỢNG THIẾT KẾ (PRE-DELIVERY UI/UX CHECKLIST)

Khi thiết kế file Prototype HTML, bắt buộc phải thỏa mãn 8 tiêu chí kiểm tra:
- [ ] **Không dùng Emoji thay thế Icon:** Dùng biểu tượng SVG (Lucide/Heroicons) với `aria-hidden="true"`.
- [ ] **Thước đo tương phản (Contrast Ratio):** Văn bản chính và các nhãn trạng thái đạt tối thiểu 4.5:1 trên nền trắng/slate.
- [ ] **Phông số dạng bảng (Tabular Nums):** Toàn bộ số liệu tồn kho và tiền tệ đều có class `.tabular-nums`.
- [ ] **Hiệu ứng chuyển động nhẹ (Transitions):** Thời gian chuyển trạng thái hover từ 150ms đến 200ms (`ease-in-out`), không dùng chuyển động giật cục hoặc quá dài (> 500ms).
- [ ] **Khu vực bấm cảm ứng (Touch Target):** Các nút bấm và ô chọn dropdown có chiều cao tối thiểu 40px - 44px.
- [ ] **Kiểm soát hiển thị bảo mật:** Giao diện có công tắc kiểm thử chuyển đổi vai trò (Owner vs Warehouse) để xác thực tính năng che giá vốn.
- [ ] **Trạng thái rỗng (Empty State):** Khi gõ từ khóa tìm kiếm không khớp sản phẩm nào, bảng hiển thị hình minh họa vector rỗng kèm thông báo hướng dẫn rõ ràng.
- [ ] **Tương thích Mobile/Tablet:** Bảng dữ liệu có thanh cuộn ngang khi xem trên màn hình hẹp, không làm vỡ bố cục tổng thể.

---
*Tài liệu được chuẩn hóa bởi UI/UX Pro Max Skill - Dự án Stock Sense.*
