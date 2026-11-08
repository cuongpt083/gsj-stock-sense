# HƯỚNG DẪN CẤU HÌNH UI-STYLING & MÃ NGUỒN MẪU PROTOTYPE HTML
## DỰ ÁN: HỆ THỐNG QUẢN LÝ KHO HÀNG ĐIỆN MÁY THÔNG MINH - STOCK SENSE
### CHUYÊN ĐỀ: THIẾT KẾ PROTOTYPE HTML CHUẨN DESIGN SYSTEM

---

| Thông tin tài liệu | Chi tiết |
| :--- | :--- |
| **Mã tài liệu** | `SS-DOC-UI-STYLING-GUIDE` |
| **Tên tài liệu** | Hướng dẫn UI-Styling & Bộ Component Snippets Thiết kế Prototype HTML |
| **Phiên bản** | `1.0` |
| **Ngày ban hành** | 08/11/2026 |
| **Căn cứ hệ thống** | `docs/UI_UX_DESIGN_SYSTEM.md`, `docs/design-tokens.css`, `docs/design-tokens.json` |
| **Mục đích** | Cung cấp tài liệu kỹ thuật và mã nguồn mẫu để lập trình viên/designer cắt giao diện Prototype HTML tức thì |

---

## 1. THIẾT LẬP MÔI TRƯỜNG NHANH CHO FILE PROTOTYPE HTML

Để dựng nhanh file Prototype HTML độc lập (Standalone Prototype) mà không cần cấu hình build phức tạp (webpack/vite), bạn chỉ cần nhúng 3 thư viện nhẹ qua CDN vào thẻ `<head>` của file HTML:

```html
<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Stock Sense - Prototype Tổng quan Kho</title>
  
  <!-- 1. Google Fonts: Rubik (Heading) + Nunito Sans (Body) + JetBrains Mono (Numbers/SKU) -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Nunito+Sans:ital,opsz,wght@0,6..12,400..700;1,6..12,400..700&family=Rubik:wght@500;600;700&display=swap" rel="stylesheet">
  
  <!-- 2. Tailwind CSS CDN (Hỗ trợ class tiện ích nhanh) -->
  <script src="https://cdn.tailwindcss.com"></script>
  
  <!-- 3. Lucide Icons (Bộ Icon SVG chuẩn chuyên nghiệp, không dùng emoji) -->
  <script src="https://unpkg.com/lucide@latest"></script>
  
  <!-- 4. Nhúng Design Tokens CSS nội bộ -->
  <link rel="stylesheet" href="design-tokens.css">
  
  <!-- Cấu hình Tailwind mở rộng màu sắc theo Design Tokens -->
  <script>
    tailwind.config = {
      theme: {
        extend: {
          colors: {
            brand: {
              slate: '#1E293B',
              emerald: '#059669',
              amber: '#D97706',
              red: '#DC2626',
              blue: '#2563EB',
            }
          },
          fontFamily: {
            heading: ['Rubik', 'sans-serif'],
            body: ['Nunito Sans', 'sans-serif'],
            mono: ['JetBrains Mono', 'monospace'],
          }
        }
      }
    }
  </script>
</head>
```

---

## 2. BỘ THÀNH PHẦN MẪU (UI COMPONENT SNIPPETS)

### Snippet 1: Thẻ Chỉ số Đo lường (Metric Card - US 1.1)

```html
<!-- Metric Card: Tổng giá vốn tồn kho -->
<div class="bg-white rounded-lg p-5 border border-slate-200 shadow-sm hover:border-slate-300 transition duration-150">
  <div class="flex items-center justify-between mb-2">
    <span class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Tổng Giá Vốn Tồn Kho</span>
    <span class="p-1.5 bg-slate-100 rounded text-slate-600">
      <i data-lucide="circle-dollar-sign" class="w-4 h-4"></i>
    </span>
  </div>
  <div class="text-2xl font-bold text-slate-900 tabular-nums mb-1" id="kpi-valuation">
    15.820.500.000 đ
  </div>
  <div class="flex items-center text-xs text-emerald-600 font-medium">
    <i data-lucide="trending-up" class="w-3.5 h-3.5 mr-1"></i>
    <span>+2.5% so với đầu tuần</span>
  </div>
</div>
```

---

### Snippet 2: Bộ Huy hiệu Trạng thái (Status Badges)

```html
<!-- 1. Hết Hàng Khả Dụng (ATP = 0) -->
<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-red-50 text-red-700 border border-red-200">
  <span class="w-1.5 h-1.5 rounded-full bg-red-600 mr-1.5"></span>
  HẾT KHẢ DỤNG
</span>

<!-- 2. Treo Trả Góp Quá Hạn > 48h -->
<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-red-100 text-red-800 border border-red-300">
  <i data-lucide="clock-alert" class="w-3 h-3 mr-1 text-red-700"></i>
  TREO TRẢ GÓP &gt; 48H
</span>

<!-- 3. Sắp Hết Hàng (1 <= ATP <= 3) -->
<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
  <span class="w-1.5 h-1.5 rounded-full bg-amber-600 mr-1.5"></span>
  SẮP HẾT (ATP: 2)
</span>

<!-- 4. Hàng Đang Về từ Nhà Cung Cấp -->
<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
  <i data-lucide="truck" class="w-3 h-3 mr-1 text-blue-600"></i>
  ĐANG VỀ: 10
</span>

<!-- 5. Tồn Kho An Toàn -->
<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
  <span class="w-1.5 h-1.5 rounded-full bg-emerald-600 mr-1.5"></span>
  BÌNH THƯỜNG
</span>
```

---

### Snippet 3: Banner Tác chiến Khẩn cấp (Action Alert Banner)

```html
<!-- Banner cảnh báo kẹt đơn trả góp quá hạn -->
<div class="bg-red-50 border-l-4 border-red-600 p-4 rounded-r-lg mb-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-sm">
  <div class="flex items-start">
    <div class="flex-shrink-0 text-red-600 mr-3 mt-0.5">
      <i data-lucide="alert-triangle" class="w-5 h-5"></i>
    </div>
    <div>
      <h4 class="text-sm font-bold text-red-900">CẢNH BÁO NGHẼN DÒNG TIỀN DO ĐƠN TRẢ GÓP TREO</h4>
      <p class="text-xs text-red-700 mt-0.5">
        Phát hiện <strong class="font-bold underline">145 sản phẩm</strong> đang bị giữ chỗ bởi hồ sơ trả góp quá hạn 48 giờ. Hàng khả dụng (ATP) bị thiếu hụt nhân tạo!
      </p>
    </div>
  </div>
  <button 
    onclick="openReleaseModal()"
    class="inline-flex items-center px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-xs font-bold uppercase tracking-wider rounded-md shadow transition duration-150 whitespace-nowrap"
  >
    <i data-lucide="zap" class="w-4 h-4 mr-1.5"></i>
    Giải Phóng Đơn Quá Hạn &gt; 48h
  </button>
</div>
```

---

### Snippet 4: Bảng Dữ liệu Hàng hóa Chuẩn Kho Vận (Data Table)

```html
<!-- Table Hàng Hóa Kho Vận -->
<div class="bg-white border border-slate-200 rounded-lg overflow-hidden shadow-sm">
  <div class="overflow-x-auto">
    <table class="w-full text-left text-sm">
      <thead class="bg-slate-100 text-slate-700 text-xs font-semibold uppercase tracking-wider border-b border-slate-200">
        <tr>
          <th class="py-3 px-4">Mã SKU</th>
          <th class="py-3 px-4">Tên Sản Phẩm</th>
          <th class="py-3 px-4">Ngành Hàng</th>
          <th class="py-3 px-4 text-right">Tồn Vật Lý</th>
          <th class="py-3 px-4 text-right">Đang Giữ</th>
          <th class="py-3 px-4 text-right font-bold text-emerald-700">Khả Dụng (ATP)</th>
          <th class="py-3 px-4 text-right text-blue-700">Đang Về</th>
          <th class="py-3 px-4 text-center">Trạng Thái</th>
          <th class="py-3 px-4 text-center">Thao Tác</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-slate-100">
        <!-- Row 1: Hàng bình thường -->
        <tr class="hover:bg-slate-50 transition duration-100">
          <td class="py-3 px-4 font-mono font-medium text-slate-800">SP_DK_FTKC</td>
          <td class="py-3 px-4 font-medium text-slate-900">Máy lạnh Daikin Inverter 1.5 HP FTKC35UVMV</td>
          <td class="py-3 px-4 text-slate-500 text-xs">Điện lạnh</td>
          <td class="py-3 px-4 text-right tabular-nums text-slate-800">35</td>
          <td class="py-3 px-4 text-right tabular-nums text-slate-600">5</td>
          <td class="py-3 px-4 text-right tabular-nums font-bold text-emerald-600">30</td>
          <td class="py-3 px-4 text-right tabular-nums text-blue-600">10</td>
          <td class="py-3 px-4 text-center">
            <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">BÌNH THƯỜNG</span>
          </td>
          <td class="py-3 px-4 text-center">
            <button class="text-slate-400 hover:text-slate-600" title="Xem chi tiết"><i data-lucide="eye" class="w-4 h-4"></i></button>
          </td>
        </tr>

        <!-- Row 2: Hết khả dụng do bị giữ chỗ -->
        <tr class="hover:bg-slate-50 transition duration-100 bg-red-50/20">
          <td class="py-3 px-4 font-mono font-medium text-slate-800">SP_SN_XR65</td>
          <td class="py-3 px-4 font-medium text-slate-900">Smart Tivi Sony Bravia OLED 4K 65 inch</td>
          <td class="py-3 px-4 text-slate-500 text-xs">Điện tử</td>
          <td class="py-3 px-4 text-right tabular-nums text-slate-800 font-semibold">18</td>
          <td class="py-3 px-4 text-right tabular-nums text-red-600 font-bold">18</td>
          <td class="py-3 px-4 text-right tabular-nums font-black text-red-600 bg-red-50">0</td>
          <td class="py-3 px-4 text-right tabular-nums text-blue-600">20</td>
          <td class="py-3 px-4 text-center">
            <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-red-50 text-red-700 border border-red-200">HẾT KHẢ DỤNG</span>
          </td>
          <td class="py-3 px-4 text-center">
            <button class="text-red-600 hover:text-red-800 font-medium text-xs underline">Xem đơn giữ</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
```

---

### Snippet 5: Hộp thoại Xác nhận Giải phóng Đơn hàng (Action Modal)

```html
<!-- Modal Xác nhận giải phóng kho -->
<div id="releaseModal" class="hidden fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
  <div class="bg-white rounded-lg max-w-md w-full p-6 shadow-xl border border-slate-200">
    <div class="flex items-center text-red-600 mb-3">
      <i data-lucide="alert-octagon" class="w-6 h-6 mr-2"></i>
      <h3 class="text-lg font-bold text-slate-900 font-heading">Xác Nhận Giải Phóng Hàng Giữ Chỗ</h3>
    </div>
    <p class="text-sm text-slate-600 mb-4 leading-relaxed">
      Hệ thống sẽ tự động hủy lệnh giữ chỗ của <strong class="text-slate-900">3 đơn hàng trả góp quá hạn 48 giờ</strong> và hoàn trả <strong class="text-emerald-600">12 sản phẩm</strong> vào lượng tồn khả dụng (ATP) để tiếp tục bán hàng.
    </p>
    <div class="flex justify-end gap-3">
      <button 
        onclick="closeReleaseModal()"
        class="px-4 py-2 border border-slate-300 rounded text-slate-700 text-sm font-medium hover:bg-slate-50 transition"
      >
        Hủy Bỏ
      </button>
      <button 
        onclick="confirmRelease()"
        class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-bold rounded shadow transition"
      >
        Đồng Ý Giải Phóng
      </button>
    </div>
  </div>
</div>
```

---

## 3. LƯU Ý KHI THIẾT KẾ & TÍNH NĂNG TƯƠNG TÁC JS

1. **Khởi tạo Icons:**
   Khi DOM đã nạp xong, hãy luôn gọi `lucide.createIcons()` để chuyển đổi các thẻ `<i data-lucide="..."></i>` thành mã SVG sắc nét:
   ```javascript
   document.addEventListener('DOMContentLoaded', () => {
     lucide.createIcons();
   });
   ```

2. **Chế độ kiểm thử Phân quyền (Role Switcher Demo):**
   Trong file Prototype HTML, hãy tạo 1 dropdown chọn Role ở thanh Topbar:
   - Khi chọn `Thủ kho`: Dùng JavaScript đổi text thẻ `Tổng giá vốn` thành `"*** đ (Bảo mật)"`, đồng thời ẩn cột Giá vốn trong bảng.
   - Khi chọn `Chủ doanh nghiệp`: Hiển thị số tiền thực tế `15.820.500.000 đ`.

---
*Tài liệu hướng dẫn phát triển bởi UI/UX Pro Max Skill.*
