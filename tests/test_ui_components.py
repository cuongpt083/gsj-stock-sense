"""
Kiểm thử Unit Tests cho UI Helper Components (Phase 3 TDD).
"""
import pytest
from src.ui.components import (
    format_currency,
    format_number,
    render_status_badge,
    render_trend_delta,
)


def test_format_currency():
    """Kiểm tra format tiền tệ VNĐ."""
    assert format_currency(15820500000) == "15,820,500,000 đ"
    assert format_currency(0) == "0 đ"
    assert format_currency(None, is_masked=True) == "*** đ (Bảo mật)"


def test_format_number():
    """Kiểm tra format số lượng."""
    assert format_number(1248) == "1,248"
    assert format_number(0) == "0"
    assert format_number(50000) == "50,000"


def test_render_status_badge():
    """Kiểm tra tạo mã HTML badge màu cảnh báo theo trạng thái."""
    badge_out = render_status_badge("HẾT KHẢ DỤNG")
    assert "background-color: #ff4d4f" in badge_out
    assert "HẾT KHẢ DỤNG" in badge_out

    badge_low = render_status_badge("SẮP HẾT")
    assert "background-color: #faad14" in badge_low

    badge_normal = render_status_badge("BÌNH THƯỜNG")
    assert "background-color: #52c41a" in badge_normal

    badge_transit = render_status_badge("ĐANG VỀ")
    assert "background-color: #1890ff" in badge_transit


def test_render_trend_delta():
    """Kiểm tra render chuỗi delta % tăng giảm."""
    assert render_trend_delta(2.5) == "↑ +2.5%"
    assert render_trend_delta(-1.8) == "↓ -1.8%"
    assert render_trend_delta(0.0) == "0.0%"
    assert render_trend_delta(None) == ""
