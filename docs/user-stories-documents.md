# BÁO CÁO KHẢO SÁT YÊU CẦU NGƯỜI DÙNG (USER STORIES)
**Dự án:** Phần mềm quản lý kho hàng điện máy thông minh - Stock Sense
**Tài liệu:** Báo cáo khảo sát phục vụ xây dựng URD
**Đối tượng sử dụng:** Ban Giám đốc, Quản lý cửa hàng, Đội ngũ BA/Phát triển sản phẩm

---

## MỤC TIÊU TÀI LIỆU
Tài liệu này hệ thống hóa các yêu cầu chức năng của phần mềm Stock Sense dựa trên kết quả thống nhất giữa đội ngũ khảo sát và đại diện doanh nghiệp kinh doanh điện máy. Các yêu cầu được trình bày dưới dạng User Story (Câu chuyện người dùng) nhằm đảm bảo sự gắn kết chặt chẽ giữa tính năng phần mềm và lợi ích nghiệp vụ thực tế.

---

## DANH SÁCH USER STORIES (YÊU CẦU CHỨC NĂNG)

### 1. Nhóm chức năng: Tổng quan kho
**US 1.1: Theo dõi tổng quan tài sản kho**
* **Là** Quản lý cửa hàng / Chủ doanh nghiệp,
* **Tôi muốn** xem thống kê tổng số lượng sản phẩm, tổng số lượng tồn kho và tổng giá vốn tồn kho trên một màn hình duy nhất,
* **Để** tôi có thể nắm bắt nhanh chóng quy mô và tình hình phân bổ vốn lưu động trong kho hàng.

**US 1.2: Theo dõi trạng thái hàng hóa và đơn hàng**
* **Là** Quản lý cửa hàng / Thủ kho,
* **Tôi muốn** xem thống kê chi tiết theo dõi đơn hàng (bao gồm: lượng hàng đã giữ cho các đơn, lượng hàng đang trên đường nhập về, và phân loại đơn hàng trả góp / thanh toán toàn phần),
* **Để** tôi có kế hoạch luân chuyển hàng hóa chính xác, tránh tình trạng hứa bán cho khách nhưng thực tế trong kho không còn hàng (hàng ảo).

### 2. Nhóm chức năng: Cần xử lý hôm nay
**US 2.1: Danh sách cảnh báo hàng hóa cần xử lý**
* **Là** Quản lý cửa hàng / Quản lý ngành hàng,
* **Tôi muốn** hệ thống tự động tổng hợp và hiển thị danh sách các mặt hàng "cần xử lý ngay trong ngày" (bao gồm: hàng bán chậm, hàng ngừng kinh doanh, hàng sắp qua mùa vụ, và sản phẩm sắp hết hàng),
* **Để** tôi có thể lập tức đưa ra chỉ đạo nhập thêm hoặc xả hàng mà không mất thời gian tổng hợp báo cáo thủ công mỗi sáng.

### 3. Nhóm chức năng: Gợi ý xả hàng
**US 3.1: Chi tiết sản phẩm cần xả và lượng bán mục tiêu**
* **Là** Quản lý ngành hàng / Trưởng phòng Kinh doanh,
* **Tôi muốn** xem danh sách các sản phẩm cần xả hàng, kèm theo lý do cảnh báo cụ thể (ví dụ: tồn kho quá 90 ngày) và số lượng cần bán để đạt mức an toàn,
* **Để** tôi xác định đúng mục tiêu và quy mô của chiến dịch xả hàng.

**US 3.2: Gợi ý kịch bản khuyến mại và giá bán**
* **Là** Quản lý ngành hàng / Trưởng phòng Kinh doanh,
* **Tôi muốn** hệ thống cung cấp các phương án khuyến mại khả thi, mức lãi dự kiến, đồng thời so sánh giá với các đối thủ cạnh tranh trên thị trường để đưa ra một "mức giá bán gợi ý",
* **Để** tôi có thể ra quyết định hạ giá xả hàng một cách khoa học, vừa cạnh tranh được với đối thủ vừa tối ưu hóa tỷ suất lợi nhuận còn lại.

### 4. Nhóm chức năng: Gợi ý nhập hàng
**US 4.1: Đề xuất nhập hàng thông minh**
* **Là** Nhân viên Mua hàng (Purchasing) / Quản lý cửa hàng,
* **Tôi muốn** hệ thống tính toán và đưa ra số lượng nhập hàng đề xuất (dựa trên: nhu cầu dự kiến của thị trường, số lượng tồn hiện có thể bán, và lượng hàng đang trên đường về),
* **Để** tôi lên đơn đặt hàng nhà cung cấp một cách chính xác, đảm bảo độ tin cậy cao, tránh nhập thừa gây đọng vốn hoặc nhập thiếu làm mất doanh thu.

### 5. Nhóm chức năng: Khách hàng cần chăm sóc
**US 5.1: Gợi ý danh sách khách hàng tiềm năng để up-sell/cross-sell**
* **Là** Nhân viên Kinh doanh / Chăm sóc khách hàng (CSKH),
* **Tôi muốn** nhận được danh sách "Khách hàng cần chăm sóc" bao gồm Tên khách hàng, sản phẩm điện máy họ đã mua, các dấu hiệu phát sinh nhu cầu mới, lịch sử liên hệ gần nhất và các gợi ý tư vấn kịch bản,
* **Để** tôi có thể chủ động gọi điện hỏi thăm, tư vấn bán kèm (ví dụ: khách mua điều hòa được 6 tháng -> gợi ý dịch vụ vệ sinh điều hòa hoặc mua thêm máy lọc không khí) nhằm tăng doanh thu.

### 6. Nhóm chức năng: Báo cáo hiệu quả
**US 6.1: Đánh giá hiệu quả kinh doanh và xả hàng**
* **Là** Chủ doanh nghiệp / Giám đốc kinh doanh,
* **Tôi muốn** xem báo cáo đo lường hiệu quả (bao gồm: khối lượng hàng tồn đã xả thành công, tổng số tiền vốn đã thu hồi được, và doanh thu từ việc bán kèm - cross sell),
* **Để** tôi có thể đánh giá tính hiệu quả của phần mềm Stock Sense cũng như năng lực thực thi của đội ngũ nhân viên kinh doanh.

---
**Xác nhận của Đại diện Doanh nghiệp:**
*Ký và ghi rõ họ tên*

**Xác nhận của Đại diện Phân tích Nghiệp vụ (BA):**
*Ký và ghi rõ họ tên*