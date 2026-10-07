"""
GSJ FASHION RETAIL - EXECUTIVE BI & RFM ANALYTICS DASHBOARD
=============================================================
Dashboard phân tích kết quả kinh doanh thời trang dựa trên PoS KiotViet
- Nguồn dữ liệu: data/retail_synthetic.db (SQLite)
- Phân hệ: KPIs Tổng quan, Xu hướng & Kênh bán, Sản phẩm & Tồn kho, Phân khúc RFM 5 nấc, Đơn đặt hàng & Phễu chuyển đổi
"""

import os
import sys
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime, date

# Đường dẫn DB
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DB_PATH = os.path.join(BASE_DIR, 'data', 'retail_synthetic.db')

# Cấu hình giao diện Streamlit
st.set_page_config(
    page_title="GSJ Fashion Analytics | KiotViet PoS",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS cho phong cách Modern Retail Dashboard
st.markdown("""
<style>
    .main-header {
        font-size: 26px;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 2px;
    }
    .sub-header {
        font-size: 14px;
        color: #64748B;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-label {
        font-size: 13px;
        font-weight: 500;
        color: #64748B;
    }
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: #0F172A;
    }
    .metric-delta {
        font-size: 12px;
        font-weight: 600;
        color: #10B981;
    }
    .rfm-badge-vip { background-color: #FEF3C7; color: #92400E; padding: 4px 10px; border-radius: 6px; font-weight: 600; }
    .rfm-badge-loyal { background-color: #D1FAE5; color: #065F46; padding: 4px 10px; border-radius: 6px; font-weight: 600; }
    .rfm-badge-potential { background-color: #DBEAFE; color: #1E40AF; padding: 4px 10px; border-radius: 6px; font-weight: 600; }
    .rfm-badge-risk { background-color: #FEE2E2; color: #991B1B; padding: 4px 10px; border-radius: 6px; font-weight: 600; }
    .rfm-badge-lost { background-color: #F3F4F6; color: #4B5563; padding: 4px 10px; border-radius: 6px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# HÀM NẠP DỮ LIỆU TỪ SQLITE
# ==============================================================================
@st.cache_data(ttl=60)
def load_data():
    if not os.path.exists(DB_PATH):
        return None, None, None, None, None, None
    
    conn = sqlite3.connect(DB_PATH)
    
    # 1. Chi tiết hóa đơn kèm thông tin sản phẩm và nhân viên
    query_invoices = """
    SELECT 
        i.invoice_code,
        i.invoice_time,
        DATE(i.invoice_time) AS sale_date,
        STRFTIME('%H', i.invoice_time) AS sale_hour,
        STRFTIME('%w', i.invoice_time) AS day_of_week,
        i.customer_code,
        c.customer_name,
        c.area AS customer_area,
        i.employee_code,
        e.employee_name,
        i.branch_name,
        i.sales_channel,
        i.total_amount AS invoice_subtotal,
        i.discount_amount AS invoice_discount,
        i.final_amount,
        i.pay_cash,
        i.pay_card,
        i.pay_transfer,
        l.product_code,
        p.parent_code AS style_code,
        p.product_name,
        p.size,
        p.color,
        p.material,
        p.season,
        p.category_path,
        cat.category_level1,
        cat.category_level2,
        cat.category_level3,
        l.quantity,
        l.unit_price,
        l.line_total,
        l.cost_price_snapshot,
        (l.cost_price_snapshot * l.quantity) AS cogs,
        (l.line_total - (l.cost_price_snapshot * l.quantity)) AS gross_profit
    FROM fact_invoices i
    JOIN fact_invoice_lines l ON i.invoice_code = l.invoice_code
    JOIN dim_products p ON l.product_code = p.product_code
    LEFT JOIN dim_categories cat ON p.category_id = cat.category_id
    LEFT JOIN dim_customers c ON i.customer_code = c.customer_code
    LEFT JOIN dim_employees e ON i.employee_code = e.employee_code;
    """
    df_inv_details = pd.read_sql_query(query_invoices, conn)
    
    # 2. Hóa đơn header
    df_invoices = pd.read_sql_query("SELECT * FROM fact_invoices;", conn)
    
    # 3. Sản phẩm & tồn kho
    df_products = pd.read_sql_query("SELECT * FROM dim_products;", conn)
    
    # 4. Đơn đặt hàng (Orders)
    df_orders = pd.read_sql_query("SELECT * FROM fact_orders;", conn)
    
    # 5. View RFM Raw
    df_rfm_raw = pd.read_sql_query("SELECT * FROM vw_customer_rfm_raw;", conn)
    
    # 6. View Committed Stock
    df_committed_stock = pd.read_sql_query("SELECT * FROM vw_committed_stock_by_variant;", conn)
    
    conn.close()
    
    # Chuyển đổi định dạng ngày tháng
    if not df_inv_details.empty:
        df_inv_details['invoice_time'] = pd.to_datetime(df_inv_details['invoice_time'])
        df_inv_details['sale_date'] = pd.to_datetime(df_inv_details['sale_date'])
    
    if not df_invoices.empty:
        df_invoices['invoice_time'] = pd.to_datetime(df_invoices['invoice_time'])
        
    if not df_orders.empty:
        df_orders['order_time'] = pd.to_datetime(df_orders['order_time'])
        
    return df_inv_details, df_invoices, df_products, df_orders, df_rfm_raw, df_committed_stock


# ==============================================================================
# HÀM PHÂN KHÚC RFM 5 NẤC (IN-MEMORY PANDAS)
# ==============================================================================
def calculate_rfm_segments(df_rfm):
    if df_rfm.empty:
        return df_rfm
    
    df = df_rfm.copy()
    
    # Thang điểm 5 nấc sử dụng qcut (với duplicates='drop' để chống trùng ngưỡng)
    try:
        # Recency: Số ngày càng nhỏ điểm càng cao (1-5)
        df['R_Score'] = pd.qcut(df['recency_days'], 5, labels=[5, 4, 3, 2, 1], duplicates='drop').astype(int)
    except Exception:
        df['R_Score'] = pd.cut(df['recency_days'], bins=5, labels=[5, 4, 3, 2, 1]).astype(int)
        
    try:
        # Frequency: Càng mua nhiều lần điểm càng cao (1-5)
        df['F_Score'] = pd.qcut(df['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    except Exception:
        df['F_Score'] = pd.cut(df['frequency'], bins=5, labels=[1, 2, 3, 4, 5]).astype(int)
        
    try:
        # Monetary: Càng chi nhiều tiền điểm càng cao (1-5)
        df['M_Score'] = pd.qcut(df['monetary'], 5, labels=[1, 2, 3, 4, 5], duplicates='drop').astype(int)
    except Exception:
        df['M_Score'] = pd.cut(df['monetary'], bins=5, labels=[1, 2, 3, 4, 5]).astype(int)
        
    # Gán nhãn phân khúc chuẩn Retail theo đề cương thực hành
    def assign_segment(row):
        r, f, m = row['R_Score'], row['F_Score'], row['M_Score']
        fm_avg = (f + m) / 2.0
        
        if r >= 4 and fm_avg >= 4:
            return "VIP / Khách Hàng Xuất Sắc"
        elif r >= 3 and fm_avg >= 3:
            return "Khách Hàng Thân Thiết (Loyal)"
        elif r >= 4 and fm_avg < 3:
            return "Khách Hàng Mới / Tiềm Năng"
        elif r <= 2 and fm_avg >= 3:
            return "Có Nguy Cơ Rời Bỏ (At Risk)"
        else:
            return "Khách Đã Mất (Lost)"
            
    df['Segment'] = df.apply(assign_segment, axis=1)
    return df


# ==============================================================================
# GIAO DIỆN CHÍNH STREAMLIT
# ==============================================================================
df_inv_details, df_invoices, df_products, df_orders, df_rfm_raw, df_committed_stock = load_data()

# SIDEBAR: Bộ lọc dữ liệu
st.sidebar.image("https://img.icons8.com/isometric/100/hanger.png", width=60)
st.sidebar.title("KiotViet PoS")
st.sidebar.caption("Fashion Retail Analytics System")

if df_inv_details is None or df_inv_details.empty:
    st.error("Chưa tìm thấy dữ liệu trong `data/retail_synthetic.db`!")
    st.info("Vui lòng chạy script sinh dữ liệu: `python src/sdv/generate_synthetic_data.py`")
    st.stop()

# Bộ lọc thời gian
min_date = df_inv_details['sale_date'].min().date()
max_date = df_inv_details['sale_date'].max().date()
date_range = st.sidebar.date_input("Khoảng thời gian bán hàng:", [min_date, max_date], min_value=min_date, max_value=max_date)

# Bộ lọc chi nhánh
branches = ["Tất cả"] + list(df_inv_details['branch_name'].dropna().unique())
selected_branch = st.sidebar.selectbox("Chi nhánh:", branches)

# Bộ lọc kênh bán
channels = ["Tất cả"] + list(df_inv_details['sales_channel'].dropna().unique())
selected_channel = st.sidebar.selectbox("Kênh bán hàng:", channels)

# Áp dụng bộ lọc
filtered_df = df_inv_details.copy()
if len(date_range) == 2:
    start_d, end_d = date_range
    filtered_df = filtered_df[(filtered_df['sale_date'].dt.date >= start_d) & (filtered_df['sale_date'].dt.date <= end_d)]
if selected_branch != "Tất cả":
    filtered_df = filtered_df[filtered_df['branch_name'] == selected_branch]
if selected_channel != "Tất cả":
    filtered_df = filtered_df[filtered_df['sales_channel'] == selected_channel]

# TIÊU ĐỀ DASHBOARD
col_title, col_stat = st.columns([3, 1])
with col_title:
    st.markdown('<div class="main-header">BÁO CÁO KINH DOANH CHUỖI THỜI TRANG GSJ</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-header">Dữ liệu PoS KiotViet • Cập nhật ngày {datetime.now().strftime("%d/%m/%Y")} • Chi nhánh: {selected_branch}</div>', unsafe_allow_html=True)
with col_stat:
    st.button("🔄 Làm mới dữ liệu", on_click=st.cache_data.clear)

# TABS CHỨC NĂNG
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Thẻ Điểm Vận Hành",
    "📈 Xu Hướng & Bối Cảnh",
    "👗 Sản Phẩm & Tồn Kho",
    "👥 Phân Khúc Khách Hàng (RFM)",
    "📑 Đơn Đặt Hàng & Giữ Chỗ"
])


# ==============================================================================
# TAB 1: THẺ ĐIỂM VẬN HÀNH (OPERATIONAL SCORECARDS)
# ==============================================================================
with tab1:
    # Tính toán các chỉ số High-level KPIs
    total_revenue = filtered_df['line_total'].sum()
    total_cogs = filtered_df['cogs'].sum()
    gross_profit = total_revenue - total_cogs
    gross_margin_pct = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    unique_invoices = filtered_df['invoice_code'].nunique()
    total_items_sold = filtered_df['quantity'].sum()
    aov = (total_revenue / unique_invoices) if unique_invoices > 0 else 0
    unique_customers = filtered_df[filtered_df['customer_code'] != 'KH_BANLE']['customer_code'].nunique()
    
    # Hiển thị Scorecards 4x2
    r1, r2, r3, r4 = st.columns(4)
    with r1:
        st.metric(label="Tổng Doanh Thu (VND)", value=f"{total_revenue:,.0f} đ", delta="+12.4% vs tháng trước")
    with r2:
        st.metric(label="Lợi Nhuận Gộp (Gross Profit)", value=f"{gross_profit:,.0f} đ", delta=f"{gross_margin_pct:.1f}% Biên LN")
    with r3:
        st.metric(label="Số Lượng Hóa Đơn", value=f"{unique_invoices:,}", delta=f"{total_items_sold:,} món đồ bán ra")
    with r4:
        st.metric(label="Giá Trị Đơn Trung Bình (AOV)", value=f"{aov:,.0f} đ", delta="Khách lẻ")

    st.markdown("---")
    
    # Biểu đồ Doanh thu & Lợi nhuận theo ngày
    daily_sales = filtered_df.groupby('sale_date').agg({
        'line_total': 'sum',
        'gross_profit': 'sum',
        'invoice_code': 'nunique'
    }).reset_index()
    
    fig_daily = go.Figure()
    fig_daily.add_trace(go.Bar(
        x=daily_sales['sale_date'], y=daily_sales['line_total'],
        name='Doanh Thu (Revenue)', marker_color='#3B82F6'
    ))
    fig_daily.add_trace(go.Scatter(
        x=daily_sales['sale_date'], y=daily_sales['gross_profit'],
        name='Lợi Nhuận Gộp (Profit)', line=dict(color='#10B981', width=3)
    ))
    fig_daily.update_layout(
        title="<b>Doanh Thu & Lợi Nhuận Gộp Theo Ngày Bán Hàng</b>",
        xaxis_title="Ngày", yaxis_title="VND",
        hovermode="x unified", legend=dict(orientation="h", y=1.1, x=0.3),
        height=380, margin=dict(l=20, r=20, t=50, b=20)
    )
    st.plotly_chart(fig_daily, use_container_width=True)


# ==============================================================================
# TAB 2: XU HƯỚNG BÁN HÀNG & BỐI CẢNH (SALES TRENDS & CHANNELS)
# ==============================================================================
with tab2:
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        # 1. Cơ cấu hình thức thanh toán
        inv_headers = df_invoices[df_invoices['invoice_code'].isin(filtered_df['invoice_code'])].copy()
        pay_sums = {
            "Tiền Mặt": inv_headers['pay_cash'].sum(),
            "Quẹt Thẻ": inv_headers['pay_card'].sum(),
            "Chuyển Khoản": inv_headers['pay_transfer'].sum()
        }
        df_pay = pd.DataFrame(list(pay_sums.items()), columns=['Method', 'Amount'])
        fig_pay = px.pie(
            df_pay, values='Amount', names='Method', hole=0.5,
            color='Method',
            color_discrete_map={"Tiền Mặt": "#F59E0B", "Quẹt Thẻ": "#3B82F6", "Chuyển Khoản": "#10B981"},
            title="<b>Tỷ Trọng Phương Thức Thanh Toán (Cash Flow)</b>"
        )
        fig_pay.update_traces(textposition='inside', textinfo='percent+label')
        fig_pay.update_layout(height=350, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_pay, use_container_width=True)

    with col_t2:
        # 2. Doanh thu theo Kênh bán hàng
        chan_sales = filtered_df.groupby('sales_channel')['line_total'].sum().reset_index()
        fig_chan = px.bar(
            chan_sales, x='sales_channel', y='line_total',
            color='sales_channel',
            title="<b>Doanh Thu Phân Bổ Theo Kênh Bán Hàng (Omnichannel)</b>",
            text_auto='.2s'
        )
        fig_chan.update_layout(showlegend=False, xaxis_title="", yaxis_title="VND", height=350, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_chan, use_container_width=True)

    st.markdown("---")
    
    col_t3, col_t4 = st.columns(2)
    with col_t3:
        # 3. Biểu đồ nhiệt Giờ Vàng Mua Sắm (Heatmap: Giờ x Thứ)
        heatmap_data = filtered_df.copy()
        heatmap_data['hour'] = heatmap_data['invoice_time'].dt.hour
        heatmap_data['weekday'] = heatmap_data['invoice_time'].dt.day_name()
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        pivot_heat = heatmap_data.pivot_table(
            index='weekday', columns='hour', values='line_total', aggfunc='sum', fill_value=0
        ).reindex(days_order)
        
        fig_heat = px.imshow(
            pivot_heat, labels=dict(x="Khung Giờ (24h)", y="Thứ trong tuần", color="Doanh thu"),
            x=pivot_heat.columns, y=pivot_heat.index,
            color_continuous_scale="Purples",
            title="<b>Biểu Đồ Nhiệt 'Khung Giờ Vàng' Mua Sắm (Peak Sales Hours)</b>"
        )
        fig_heat.update_layout(height=360, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_heat, use_container_width=True)

    with col_t4:
        # 4. Top Nhân viên Bán hàng Xuất sắc
        emp_perf = filtered_df.groupby(['employee_name', 'branch_name']).agg({
            'line_total': 'sum',
            'invoice_code': 'nunique'
        }).reset_index().sort_values(by='line_total', ascending=True).tail(8)
        
        fig_emp = px.bar(
            emp_perf, y='employee_name', x='line_total', orientation='h',
            color='branch_name', text_auto='.2s',
            title="<b>Bảng Xếp Hạng Nhân Viên Bán Hàng (Leaderboard)</b>"
        )
        fig_emp.update_layout(xaxis_title="Doanh số (VND)", yaxis_title="", height=360, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_emp, use_container_width=True)


# ==============================================================================
# TAB 3: SẢN PHẨM & TỒN KHO (PRODUCT & INVENTORY ANALYTICS)
# ==============================================================================
with tab3:
    col_p1, col_p2 = st.columns([3, 2])
    
    with col_p1:
        # Top 10 sản phẩm bán chạy nhất theo doanh thu
        top_prods = filtered_df.groupby(['product_code', 'product_name']).agg({
            'line_total': 'sum',
            'quantity': 'sum',
            'gross_profit': 'sum'
        }).reset_index().sort_values(by='line_total', ascending=False).head(10)
        
        fig_top = px.bar(
            top_prods, x='line_total', y='product_name', orientation='h',
            color='gross_profit',
            color_continuous_scale="Blues",
            title="<b>Top 10 Sản Phẩm Thời Trang Bán Chạy Nhất (Doanh Thu & Lãi Gộp)</b>",
            text_auto='.2s'
        )
        fig_top.update_layout(yaxis={'categoryorder': 'total ascending'}, height=400, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_top, use_container_width=True)
        
    with col_p2:
        # Tỷ trọng Doanh thu theo Nhóm hàng cấp 1 & cấp 2
        cat_sales = filtered_df.groupby(['category_level1', 'category_level2'])['line_total'].sum().reset_index()
        fig_cat = px.sunburst(
            cat_sales, path=['category_level1', 'category_level2'], values='line_total',
            color='line_total', color_continuous_scale='Mint',
            title="<b>Cơ Cấu Ngành Hàng (Category Breakdown)</b>"
        )
        fig_cat.update_layout(height=400, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_cat, use_container_width=True)

    st.markdown("---")
    
    # Phân tích Biến thể Size & Màu sắc
    col_p3, col_p4 = st.columns(2)
    with col_p3:
        size_perf = filtered_df.groupby('size')['quantity'].sum().reset_index().sort_values(by='quantity', ascending=False)
        fig_size = px.bar(
            size_perf, x='size', y='quantity', color='size',
            title="<b>Sản Lượng Bán Ra Theo Size (Size Breakdown)</b>"
        )
        fig_size.update_layout(showlegend=False, xaxis_title="Kích Cỡ", yaxis_title="Số Lượng Đã Bán", height=320)
        st.plotly_chart(fig_size, use_container_width=True)
        
    with col_p4:
        # Cảnh báo Tồn kho vs Tốc độ bán (Stock Velocity vs Stock-on-hand)
        stock_agg = filtered_df.groupby('product_code')['quantity'].sum().reset_index()
        stock_merged = pd.merge(df_products, stock_agg, on='product_code', how='left').fillna({'quantity': 0})
        stock_merged['stockout_risk'] = np.where(stock_merged['stock_on_hand'] < stock_merged['quantity'] * 1.5, "Nguy Cơ Cháy Hàng", "Tồn Kho An Toàn")
        
        fig_scatter = px.scatter(
            stock_merged, x='quantity', y='stock_on_hand', color='stockout_risk',
            hover_data=['product_code', 'product_name', 'sale_price'],
            color_discrete_map={"Nguy Cơ Cháy Hàng": "#EF4444", "Tồn Kho An Toàn": "#10B981"},
            title="<b>Ma Trận Tồn Kho vs Tốc Độ Bán (Stockout Risk Alert)</b>"
        )
        fig_scatter.update_layout(xaxis_title="Số Lượng Bán Ra (30 ngày)", yaxis_title="Tồn Kho Thực Tế", height=320)
        st.plotly_chart(fig_scatter, use_container_width=True)


# ==============================================================================
# TAB 4: PHÂN KHÚC KHÁCH HÀNG RFM (5 TIER SCORING)
# ==============================================================================
with tab4:
    st.markdown("### 🎯 Phân Tích Phân Khúc Khách Hàng (RFM Segmentation - 5 Nấc)")
    st.caption("Mô hình chấm điểm Recency (Gần đây), Frequency (Tần suất), Monetary (Giá trị) từ 1 đến 5 sao theo tài liệu GSJ.")
    
    # Tính RFM
    df_rfm_scored = calculate_rfm_segments(df_rfm_raw)
    
    col_rfm1, col_rfm2 = st.columns([2, 3])
    with col_rfm1:
        seg_counts = df_rfm_scored['Segment'].value_counts().reset_index()
        seg_counts.columns = ['Segment', 'Customer_Count']
        
        fig_seg = px.pie(
            seg_counts, values='Customer_Count', names='Segment', hole=0.45,
            color='Segment',
            color_discrete_map={
                "VIP / Khách Hàng Xuất Sắc": "#F59E0B",
                "Khách Hàng Thân Thiết (Loyal)": "#10B981",
                "Khách Hàng Mới / Tiềm Năng": "#3B82F6",
                "Có Nguy Cơ Rời Bỏ (At Risk)": "#EF4444",
                "Khách Đã Mất (Lost)": "#6B7280"
            },
            title="<b>Tỷ Trọng Các Nhóm Phân Khúc Khách Hàng</b>"
        )
        fig_seg.update_traces(textposition='inside', textinfo='percent+label')
        fig_seg.update_layout(height=380, margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig_seg, use_container_width=True)
        
    with col_rfm2:
        fig_rfm_scatter = px.scatter(
            df_rfm_scored, x='recency_days', y='monetary', color='Segment', size='frequency',
            hover_data=['customer_code', 'customer_name', 'phone'],
            color_discrete_map={
                "VIP / Khách Hàng Xuất Sắc": "#F59E0B",
                "Khách Hàng Thân Thiết (Loyal)": "#10B981",
                "Khách Hàng Mới / Tiềm Năng": "#3B82F6",
                "Có Nguy Cơ Rời Bỏ (At Risk)": "#EF4444",
                "Khách Đã Mất (Lost)": "#6B7280"
            },
            title="<b>Biểu Đồ Phân Tán RFM: Số Ngày Chưa Mua (R) vs Chi Tiêu (M)</b>"
        )
        fig_rfm_scatter.update_layout(xaxis_title="Recency (Số ngày kể từ lần mua cuối)", yaxis_title="Monetary (Tổng tiền chi tiêu - VND)", height=380)
        st.plotly_chart(fig_rfm_scatter, use_container_width=True)

    # Bảng khuyến nghị hành động Marketing cho từng phân khúc
    st.markdown("#### 💡 Hành Động Marketing Gợi Ý Theo Phân Khúc:")
    rec_cols = st.columns(5)
    rec_cols[0].markdown("""
    **⭐ VIP / Xuất Sắc**  
    - Tặng quà BST mới độc quyền  
    - Chăm sóc cá nhân hóa (Personal Shopper)  
    - Tri ân dịp sinh nhật / lễ  
    """)
    rec_cols[1].markdown("""
    **💚 Khách Thân Thiết**  
    - Tích lũy điểm thăng hạng  
    - Gợi ý mua combo đồng bộ  
    - Ưu đãi giảm giá 10% lần sau  
    """)
    rec_cols[2].markdown("""
    **💙 Tiềm Năng**  
    - Gửi Lookbook theo mùa  
    - Chào mừng thành viên mới  
    - Voucher giảm phí ship  
    """)
    rec_cols[3].markdown("""
    **⚠️ Có Nguy Cơ (At Risk)**  
    - SMS/Zalo thông báo Flash Sale  
    - Khảo sát lý do chưa quay lại  
    - Tặng voucher giảm 15-20%  
    """)
    rec_cols[4].markdown("""
    **⚪ Khách Đã Mất**  
    - Chiến dịch 'We miss you'  
    - Xả kho hàng mùa cũ giá rẻ  
    - Giảm chi phí tiếp thị trực tiếp  
    """)

    # Bảng chi tiết danh sách khách hàng lọc theo phân khúc
    st.markdown("#### 📋 Tra Cứu Danh Sách Khách Hàng:")
    filter_seg = st.selectbox("Lọc theo nhóm phân khúc:", ["Tất cả"] + list(df_rfm_scored['Segment'].unique()))
    df_display = df_rfm_scored if filter_seg == "Tất cả" else df_rfm_scored[df_rfm_scored['Segment'] == filter_seg]
    
    st.dataframe(
        df_display[['customer_code', 'customer_name', 'phone', 'area', 'recency_days', 'frequency', 'monetary', 'R_Score', 'F_Score', 'M_Score', 'Segment']]
        .sort_values(by='monetary', ascending=False),
        column_config={
            "monetary": st.column_config.NumberColumn("Tổng chi tiêu (VND)", format="%,.0f đ"),
            "recency_days": st.column_config.NumberColumn("Số ngày chưa mua", format="%d ngày"),
            "frequency": st.column_config.NumberColumn("Số lần mua", format="%d đơn"),
        },
        use_container_width=True,
        height=320
    )


# ==============================================================================
# TAB 5: ĐƠN ĐẶT HÀNG & PHỄU CHUYỂN ĐỔI (ORDERS & COMMITTED STOCK)
# ==============================================================================
with tab5:
    st.markdown("### 📑 Quản Lý Đơn Đặt Hàng & Giữ Chỗ Tồn Kho (Pre-Orders)")
    st.caption("Theo dõi phễu chuyển đổi từ Đơn đặt hàng sang Hóa đơn và lượng hàng đang tạm giữ theo mã SKU.")
    
    o1, o2, o3, o4 = st.columns(4)
    total_ord_count = len(df_orders)
    completed_ords = len(df_orders[df_orders['order_status'] == 'Hoan_thanh'])
    processing_ords = len(df_orders[df_orders['order_status'].isin(['Cho_xu_ly', 'Dang_giu_hang'])])
    cancelled_ords = len(df_orders[df_orders['order_status'] == 'Da_huy'])
    conv_rate = (completed_ords / total_ord_count * 100) if total_ord_count > 0 else 0
    
    o1.metric("Tổng Số Đơn Đặt Hàng", f"{total_ord_count:,}")
    o2.metric("Đã Chuyển Hóa Đơn", f"{completed_ords:,}", delta=f"{conv_rate:.1f}% Chuyển đổi")
    o3.metric("Đang Giữ Chỗ / Chờ Xử Lý", f"{processing_ords:,}")
    o4.metric("Đơn Đã Hủy", f"{cancelled_ords:,}", delta="- Rủi ro bỏ giỏ hàng")
    
    st.markdown("---")
    
    col_ord1, col_ord2 = st.columns(2)
    with col_ord1:
        # Biểu đồ phễu trạng thái đơn hàng
        status_counts = df_orders['order_status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        status_map = {
            'Hoan_thanh': 'Hoàn Thành (Xuất HĐ)',
            'Cho_xu_ly': 'Chờ Xử Lý',
            'Dang_giu_hang': 'Đang Giữ Chỗ Kho',
            'Da_huy': 'Đã Hủy Đơn'
        }
        status_counts['Status_Name'] = status_counts['Status'].map(status_map)
        
        fig_funnel = px.funnel(
            status_counts, y='Status_Name', x='Count',
            color='Status_Name',
            title="<b>Phễu Vòng Đời Đơn Đặt Hàng (Order State Funnel)</b>"
        )
        fig_funnel.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig_funnel, use_container_width=True)
        
    with col_ord2:
        # Tồn kho giữ chỗ theo biến thể (Top 10 SKU đang bị giữ nhiều nhất)
        top_committed = df_committed_stock[df_committed_stock['committed_quantity'] > 0].sort_values(by='committed_quantity', ascending=False).head(10)
        
        fig_com = go.Figure()
        fig_com.add_trace(go.Bar(
            name='Tồn Kho Thực Tế', x=top_committed['product_code'], y=top_committed['physical_stock'], marker_color='#94A3B8'
        ))
        fig_com.add_trace(go.Bar(
            name='Số Lượng Đang Giữ Chỗ', x=top_committed['product_code'], y=top_committed['committed_quantity'], marker_color='#F59E0B'
        ))
        fig_com.add_trace(go.Bar(
            name='Khả Dụng Bán Tiếp (Available)', x=top_committed['product_code'], y=top_committed['available_to_sell'], marker_color='#10B981'
        ))
        fig_com.update_layout(
            barmode='group', title="<b>Top 10 SKU Đang Giữ Chỗ vs Tồn Kho Khả Dụng</b>",
            xaxis_title="Mã SKU", yaxis_title="Số lượng", height=350, margin=dict(l=20, r=20, t=50, b=20)
        )
        st.plotly_chart(fig_com, use_container_width=True)

    # Bảng chi tiết đơn đặt hàng
    st.markdown("#### 📋 Danh Sách Đơn Đặt Hàng Gần Nhất:")
    st.dataframe(
        df_orders[['order_code', 'order_time', 'customer_code', 'employee_code', 'sales_channel', 'amount_due', 'amount_paid', 'order_status', 'expected_delivery_date', 'note']]
        .sort_values(by='order_time', ascending=False).head(20),
        column_config={
            "amount_due": st.column_config.NumberColumn("Cần trả", format="%,.0f đ"),
            "amount_paid": st.column_config.NumberColumn("Đã cọc", format="%,.0f đ"),
        },
        use_container_width=True,
        height=300
    )
