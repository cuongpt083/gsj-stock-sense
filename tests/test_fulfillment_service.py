"""
Kiểm thử Unit & Integration Tests cho US 1.2 (Fulfillment & ATP Service) theo TDD.
"""
import pytest
from src.services.fulfillment_service import FulfillmentService, InsufficientATPError


@pytest.fixture
def fulfillment_service():
    return FulfillmentService()


def test_atp_calculation_formula(fulfillment_service):
    """Kiểm tra công thức ATP = On-Hand - Reserved."""
    status_table = fulfillment_service.get_stock_status_table(branch_id="ALL")
    assert len(status_table) > 0
    for row in status_table:
        assert row["atp_qty"] == row["on_hand_qty"] - row["reserved_qty"]
        assert row["atp_qty"] >= 0


def test_get_fulfillment_kpi_summary(fulfillment_service):
    """Kiểm tra thống kê các chỉ số giao vận và phân loại đơn hàng."""
    kpi = fulfillment_service.get_fulfillment_kpi(branch_id="ALL")
    assert kpi["total_reserved_units"] >= 0
    assert kpi["installment_reserved_units"] >= 0
    assert kpi["full_payment_reserved_units"] >= 0
    assert kpi["total_reserved_units"] == kpi["installment_reserved_units"] + kpi["full_payment_reserved_units"]
    assert kpi["expired_installment_units"] > 0  # Có sản phẩm trả góp bị treo quá hạn
    assert kpi["atp_units"] > 0
    assert kpi["in_transit_units"] > 0


def test_reserve_stock_success_when_atp_sufficient(fulfillment_service):
    """Kiểm tra giữ hàng thành công khi kho còn đủ tồn khả dụng (ATP)."""
    # Lấy sản phẩm còn nhiều ATP
    table = fulfillment_service.get_stock_status_table(branch_id="BR_CAU_GIAY")
    available_item = next(item for item in table if item["atp_qty"] >= 2)
    sku = available_item["product_code"]
    initial_atp = available_item["atp_qty"]
    initial_reserved = available_item["reserved_qty"]

    # Giữ 1 sản phẩm
    result = fulfillment_service.reserve_stock(
        order_code="ORD_FULL_01",
        branch_id="BR_CAU_GIAY",
        product_code=sku,
        quantity=1,
        reservation_type="FULL_HOLD"
    )
    assert result["success"] is True

    # Kiểm tra lại tồn kho sau khi giữ
    table_after = fulfillment_service.get_stock_status_table(branch_id="BR_CAU_GIAY")
    item_after = next(item for item in table_after if item["product_code"] == sku)
    assert item_after["atp_qty"] == initial_atp - 1
    assert item_after["reserved_qty"] == initial_reserved + 1


def test_reserve_stock_fail_when_atp_insufficient(fulfillment_service):
    """Kiểm tra cơ chế Chống bán hàng ảo: Chặn đặt hàng khi ATP không đủ."""
    table = fulfillment_service.get_stock_status_table(branch_id="BR_CAU_GIAY")
    item = table[0]
    sku = item["product_code"]
    excessive_qty = item["atp_qty"] + 9999

    with pytest.raises(InsufficientATPError) as exc_info:
        fulfillment_service.reserve_stock(
            order_code="ORD_FULL_01",
            branch_id="BR_CAU_GIAY",
            product_code=sku,
            quantity=excessive_qty,
            reservation_type="FULL_HOLD"
        )
    assert "không đủ số lượng khả dụng" in str(exc_info.value).lower()


def test_auto_release_expired_installment_reservations(fulfillment_service):
    """Kiểm tra tiến trình Auto-Release tự động giải phóng hàng trả góp quá hạn 48h."""
    # Trước khi release, kiểm tra có ít nhất 1 đơn quá hạn
    kpi_before = fulfillment_service.get_fulfillment_kpi(branch_id="ALL")
    expired_count_before = kpi_before["expired_installment_units"]
    assert expired_count_before > 0

    # Chạy release worker
    release_result = fulfillment_service.release_expired_installment_reservations()
    assert release_result["released_reservations_count"] > 0
    assert release_result["restored_units_count"] == expired_count_before

    # Sau khi release, số lượng đơn quá hạn active phải bằng 0
    kpi_after = fulfillment_service.get_fulfillment_kpi(branch_id="ALL")
    assert kpi_after["expired_installment_units"] == 0
    # Số lượng ATP toàn hệ thống phải được phục hồi
    assert kpi_after["atp_units"] == kpi_before["atp_units"] + release_result["restored_units_count"]


def test_stock_status_table_filtering(fulfillment_service):
    """Kiểm tra bộ lọc trạng thái trong bảng chi tiết hàng hóa."""
    all_items = fulfillment_service.get_stock_status_table(branch_id="ALL", status_filter="ALL")
    low_atp_items = fulfillment_service.get_stock_status_table(branch_id="ALL", status_filter="LOW_ATP")
    in_transit_items = fulfillment_service.get_stock_status_table(branch_id="ALL", status_filter="HAS_IN_TRANSIT")
    stockout_items = fulfillment_service.get_stock_status_table(branch_id="ALL", status_filter="STOCKOUT")
    searched_items = fulfillment_service.get_stock_status_table(branch_id="ALL", search_term="Sony")

    assert len(all_items) >= len(low_atp_items)
    for item in in_transit_items:
        assert item["in_transit_qty"] > 0
    for item in stockout_items:
        assert item["atp_qty"] <= 0
    for item in searched_items:
        assert "Sony" in item["brand"] or "Sony" in item["product_name"]


def test_reserve_stock_validation_errors(fulfillment_service):
    """Kiểm tra validation dữ liệu đầu vào khi giữ hàng."""
    with pytest.raises(ValueError, match="lớn hơn 0"):
        fulfillment_service.reserve_stock(
            order_code="ORD_ERR",
            branch_id="BR_CAU_GIAY",
            product_code="SP_DK_FTKC",
            quantity=0
        )

    with pytest.raises(ValueError, match="Không tìm thấy bản ghi"):
        fulfillment_service.reserve_stock(
            order_code="ORD_ERR",
            branch_id="BR_CAU_GIAY",
            product_code="SP_NON_EXISTENT",
            quantity=1
        )


def test_fulfillment_kpi_by_branch(fulfillment_service):
    """Kiểm tra tính toán KPI fulfillment khi lọc theo chi nhánh cụ thể."""
    kpi_cg = fulfillment_service.get_fulfillment_kpi(branch_id="BR_CAU_GIAY")
    assert kpi_cg["total_reserved_units"] >= 0
    assert "stockout_risk_skus_count" in kpi_cg

