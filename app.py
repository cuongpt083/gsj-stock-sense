"""
Ứng dụng Dashboard Streamlit - Phân hệ Tổng quan Kho (Module 01: Inventory Overview).
Dự án Stock Sense - Hệ thống Quản lý Kho Hàng Điện Máy Thông Minh.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.services.asset_service import AssetService
from src.services.fulfillment_service import FulfillmentService
from src.ui.components import format_currency, format_number, render_trend_delta

# Cấu hình giao diện Streamlit
st.set_page_config(
    page_title="Stock Sense - Tổng quan Kho",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS cho giao diện phong cách Dashboard điều hành
st.markdown("""
<style>
    .metric-card {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: 1px solid #e8e8e8;
        margin-bottom: 12px;
    }
    .metric-title {
        font-size: 13px;
        font-weight: 600;
        color: #595959;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 26px;
        font-weight: 700;
        color: #1f1f1f;
        margin-bottom: 4px;
    }
    .metric-delta-up {
        font-size: 12px;
        font-weight: 600;
        color: #52c41a;
    }
    .metric-delta-down {
        font-size: 12px;
        font-weight: 600;
        color: #ff4d4f;
    }
    .alert-banner {
        background-color: #fff1f0;
        border: 1px solid #ffa39e;
        border-radius: 6px;
        padding: 12px 18px;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)


# Khởi tạo services
@st.cache_resource
def get_services():
    return AssetService(), FulfillmentService()

asset_svc, fulfill_svc = get_services()


# --- SIDEBAR: PHÂN QUYỀN & BỘ LỌC ĐA CHIỀU ---
st.sidebar.image("https://img.icons8.com/fluency/96/warehouse.png", width=64)
st.sidebar.title("STOCK SENSE")
st.sidebar.caption("Phân hệ 01: Tổng quan Kho Điện Máy")

# 1. Phân quyền người dùng (Role Switcher)
role_option = st.sidebar.selectbox(
    "Vai trò người dùng:",
    options=["Chủ doanh nghiệp / Quản lý", "Thủ kho"],
    help="Chọn vai trò để kiểm thử cơ chế Dynamic Cost Masking (bảo mật giá vốn)."
)
current_role = "ROLE_OWNER" if role_option == "Chủ doanh nghiệp / Quản lý" else "ROLE_WAREHOUSE"

if current_role == "ROLE_WAREHOUSE":
    st.sidebar.info("🔒 Đang kích hoạt chế độ **Thủ kho**: Thông tin giá vốn và định giá tài sản được che giấu tự động.")

st.sidebar.divider()
st.sidebar.subheader("Bộ lọc đa chiều")

# 2. Bộ lọc Chi nhánh
branches_data = asset_svc.get_branches()
branch_choices = {"Tất cả chi nhánh": "ALL"}
for b in branches_data:
    branch_choices[f"{b['branch_name']} ({b['branch_id']})"] = b["branch_id"]

selected_branch_label = st.sidebar.selectbox("Chi nhánh / Kho:", list(branch_choices.keys()))
selected_branch_id = branch_choices[selected_branch_label]

# 3. Bộ lọc Ngành hàng
categories_data = asset_svc.get_categories()
cat_choices = ["Tất cả ngành hàng"] + [c["category_name"] for c in categories_data]
selected_cat = st.sidebar.selectbox("Ngành hàng:", cat_choices)
cat_filter = None if selected_cat == "Tất cả ngành hàng" else selected_cat

# 4. Tìm kiếm từ khóa
search_term = st.sidebar.text_input("Tìm kiếm SKU / Tên máy:", placeholder="Nhập mã hoặc tên...")

st.sidebar.divider()
st.sidebar.caption("Stock Sense v1.0 • Chuẩn TDD • Streamlit 1.65")


# --- DỮ LIỆU TỔNG QUAN ---
kpi_asset = asset_svc.get_kpi_summary(branch_id=selected_branch_id, category_name=cat_filter, role=current_role)
kpi_fulfill = fulfill_svc.get_fulfillment_kpi(branch_id=selected_branch_id)


# --- TIÊU ĐỀ CHÍNH ---
st.title("📊 Tổng Quan Kho Hàng & Dòng Chảy Sản Phẩm")
st.caption(f"Dữ liệu thời gian thực • Phạm vi: **{selected_branch_label}** • Ngành hàng: **{selected_cat}**")


# ============================================================================
# ⏱️ PHÚT THỨ 1: TỔNG QUAN TÀI SẢN KHO (US 1.1)
# ============================================================================
st.subheader("1. Tổng Quan Tài Sản Kho")

col1, col2, col3 = st.columns(3)

with col1:
    delta_sku = render_trend_delta(kpi_asset["total_skus"]["trend_percentage"])
    st.metric(
        label="TỔNG SỐ LƯỢNG MÃ SẢN PHẨM (SKU)",
        value=format_number(kpi_asset["total_skus"]["value"]),
        delta=f"{delta_sku} tuần này",
        delta_color="normal"
    )

with col2:
    delta_units = render_trend_delta(kpi_asset["total_on_hand_units"]["trend_percentage"])
    st.metric(
        label="TỔNG SỐ LƯỢNG TỒN KHO THỰC TẾ",
        value=f"{format_number(kpi_asset['total_on_hand_units']['value'])} chiếc",
        delta=f"{delta_units} hôm nay",
        delta_color="inverse"
    )

with col3:
    if kpi_asset["total_valuation"]["is_masked"]:
        st.metric(
            label="TỔNG GIÁ VỐN TỒN KHO (VALUATION)",
            value="*** đ (Bảo mật)",
            delta="Chỉ hiển thị cho Quản lý",
            delta_color="off"
        )
    else:
        delta_val = render_trend_delta(kpi_asset["total_valuation"]["trend_percentage"])
        st.metric(
            label="TỔNG GIÁ VỐN TỒN KHO (VALUATION)",
            value=format_currency(kpi_asset["total_valuation"]["value"]),
            delta=f"{delta_val} so với tháng trước",
            delta_color="normal"
        )

st.divider()


# ============================================================================
# ⏱️ PHÚT THỨ 2: TRẠNG THÁI HÀNG HÓA & KIỂM SOÁT ĐƠN HÀNG (US 1.2)
# ============================================================================
st.subheader("2. Kiểm Soát Đơn Hàng & Hàng Khả Dụng Bán (ATP)")

fcol1, fcol2, fcol3, fcol4 = st.columns(4)

with fcol1:
    st.metric(
        label="HÀNG KHẢ DỤNG BÁN (ATP)",
        value=f"{format_number(kpi_fulfill['atp_units'])} chiếc",
        help="Số lượng thực tế tối đa nhân viên bán hàng được cam kết bán giao ngay cho khách."
    )

with fcol2:
    st.metric(
        label="HÀNG ĐANG GIỮ CHỖ (RESERVED)",
        value=f"{format_number(kpi_fulfill['total_reserved_units'])} chiếc",
        delta=f"Trả thẳng: {kpi_fulfill['full_payment_reserved_units']} | Trả góp: {kpi_fulfill['installment_reserved_units']}",
        delta_color="off",
        help="Hàng đã gắn với đơn bán nhưng chưa xuất kho vật lý."
    )

with fcol3:
    exp_units = kpi_fulfill["expired_installment_units"]
    st.metric(
        label="TRẢ GÓP TREO > 48H",
        value=f"{exp_units} chiếc",
        delta="CẦN GIẢI PHÓNG" if exp_units > 0 else "Ổn định",
        delta_color="inverse" if exp_units > 0 else "normal",
        help="Số lượng máy bị giam lỏng bởi đơn trả góp quá hạn duyệt hồ sơ 48 giờ."
    )

with fcol4:
    st.metric(
        label="HÀNG ĐANG TRÊN ĐƯỜNG VỀ",
        value=f"{format_number(kpi_fulfill['in_transit_units'])} chiếc",
        help="Số lượng hàng đã ký PO với nhà cung cấp đang vận chuyển về kho."
    )


# ============================================================================
# ⏱️ PHÚT THỨ 3: HÀNH ĐỘNG TÁC CHIẾN & CHI TIẾT SẢN PHẨM (ACTIONABLE INSIGHTS)
# ============================================================================
st.subheader("3. Tác Chiến Ra Quyết Định & Điều Phối Kho")

# Banner cảnh báo và nút hành động giải phóng hàng quá hạn
if exp_units > 0:
    st.error(
        f"🚨 **CẢNH BÁO NGHẼN DÒNG TIỀN:** Phát hiện **{exp_units} sản phẩm** đang bị giam lỏng "
        f"bởi các đơn trả góp quá hạn thẩm định 48 giờ, làm cạn kiệt hàng khả dụng (ATP) của khách mua trả thẳng!"
    )
    if st.button("⚡ GIẢI PHÓNG NGAY CÁC ĐƠN TRẢ GÓP QUÁ HẠN > 48H", type="primary"):
        release_res = fulfill_svc.release_expired_installment_reservations()
        st.success(
            f"✅ Đã hủy giữ chỗ thành công **{release_res['released_reservations_count']} đơn hàng quá hạn**, "
            f"phục hồi lại **{release_res['restored_units_count']} sản phẩm** vào lượng tồn khả dụng (ATP)!"
        )
        st.rerun()

# Layout 2 cột: Bảng chi tiết vs Biểu đồ phân bổ
chart_col, table_col = st.columns([1, 1])

with chart_col:
    st.markdown("#### Cơ Cấu Phân Bổ Theo Ngành Hàng")
    allocations = asset_svc.get_category_allocation(branch_id=selected_branch_id, role=current_role)
    if allocations:
        df_alloc = pd.DataFrame(allocations)
        value_column = "units" if current_role == "ROLE_WAREHOUSE" else "valuation"
        hover_title = "Số lượng (chiếc)" if current_role == "ROLE_WAREHOUSE" else "Giá trị vốn (VNĐ)"
        
        fig = px.pie(
            df_alloc,
            names="category_name",
            values=value_column,
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=False, height=320)
        st.plotly_chart(fig, use_container_width=True)

with table_col:
    st.markdown("#### Top 5 Sản Phẩm Đọng Vốn Lưu Động Cao Nhất")
    top_prods = asset_svc.get_top_capital_products(branch_id=selected_branch_id, limit=5, role=current_role)
    if top_prods:
        df_top = pd.DataFrame(top_prods)
        cols_show = ["product_name", "brand", "on_hand_qty"]
        if current_role == "ROLE_OWNER":
            cols_show.append("total_cost")
            df_top["total_cost"] = df_top["total_cost"].apply(lambda v: format_currency(v))
        
        rename_map = {
            "product_name": "Tên sản phẩm",
            "brand": "Hãng",
            "on_hand_qty": "Tồn kho",
            "total_cost": "Tổng vốn tồn"
        }
        st.dataframe(df_top[cols_show].rename(columns=rename_map), use_container_width=True, hide_index=True)


# BẢNG CHI TIẾT TRẠNG THÁI HÀNG HÓA
st.markdown("#### Bảng Chi Tiết Trạng Thái Hàng Hóa Cần Lưu Ý")

status_tab_choice = st.radio(
    "Lọc trạng thái hàng:",
    options=["Tất cả", "Cảnh báo (Hết / Sắp hết khả dụng)", "Có hàng đang về"],
    horizontal=True
)
status_map = {
    "Tất cả": "ALL",
    "Cảnh báo (Hết / Sắp hết khả dụng)": "LOW_ATP",
    "Có hàng đang về": "HAS_IN_TRANSIT"
}

table_data = fulfill_svc.get_stock_status_table(
    branch_id=selected_branch_id,
    status_filter=status_map[status_tab_choice],
    search_term=search_term if search_term else None
)

if table_data:
    df_table = pd.DataFrame(table_data)
    cols_display = [
        "product_code", "product_name", "brand", "uom",
        "on_hand_qty", "reserved_qty", "atp_qty", "in_transit_qty", "status_flag"
    ]
    renames = {
        "product_code": "Mã SKU",
        "product_name": "Tên sản phẩm",
        "brand": "Hãng",
        "uom": "ĐVT",
        "on_hand_qty": "Tồn kho",
        "reserved_qty": "Giữ chỗ",
        "atp_qty": "Khả dụng (ATP)",
        "in_transit_qty": "Đang về",
        "status_flag": "Trạng thái"
    }
    st.dataframe(
        df_table[cols_display].rename(columns=renames),
        use_container_width=True,
        hide_index=True,
        height=350
    )
else:
    st.info("Không có sản phẩm nào thỏa mãn điều kiện lọc.")
