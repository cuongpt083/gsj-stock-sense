"""
Các UI Helper Components & Formatters cho Dashboard Streamlit Stock Sense.
"""
from typing import Optional


def format_currency(amount: Optional[float], is_masked: bool = False) -> str:
    """Định dạng tiền tệ VNĐ (hỗ trợ che giá vốn bảo mật)."""
    if is_masked or amount is None:
        return "*** đ (Bảo mật)"
    return f"{int(round(amount)):,} đ".replace(",", ".") if "." in "" else f"{int(round(amount)):,} đ"


def format_number(val: Optional[int]) -> str:
    """Định dạng số lượng phân cách hàng nghìn."""
    if val is None:
        return "0"
    return f"{int(val):,}"


def render_status_badge(status_flag: str) -> str:
    """Tạo badge HTML có màu sắc trực quan theo trạng thái sản phẩm."""
    color_map = {
        "HẾT KHẢ DỤNG": ("#ff4d4f", "#fff1f0", "#ffccc7"),
        "SẮP HẾT": ("#faad14", "#fffbe6", "#ffe58f"),
        "ĐANG VỀ": ("#1890ff", "#e6f7ff", "#91d5ff"),
        "BÌNH THƯỜNG": ("#52c41a", "#f6ffed", "#b7eb8f"),
    }
    color, bg, border = color_map.get(status_flag, ("#595959", "#f5f5f5", "#d9d9d9"))
    return (
        f'<span style="display:inline-block; padding: 2px 8px; border-radius: 4px; '
        f'font-size: 12px; font-weight: 600; color: white; background-color: {color}; '
        f'border: 1px solid {border};">{status_flag}</span>'
    )


def render_trend_delta(trend_pct: Optional[float]) -> str:
    """Tạo nhãn xu hướng tăng giảm."""
    if trend_pct is None:
        return ""
    if trend_pct > 0:
        return f"↑ +{trend_pct:.1f}%"
    elif trend_pct < 0:
        return f"↓ {trend_pct:.1f}%"
    return "0.0%"
