"""
Kiểm thử Unit & Integration Tests cho US 1.1 (Asset Service) theo TDD.
"""
import pytest
from src.services.asset_service import AssetService


@pytest.fixture
def asset_service():
    return AssetService()


def test_get_branches(asset_service):
    """Kiểm tra lấy danh sách chi nhánh phục vụ bộ lọc."""
    branches = asset_service.get_branches()
    assert len(branches) >= 3
    branch_ids = [b["branch_id"] for b in branches]
    assert "BR_KHO_TONG" in branch_ids
    assert "BR_CAU_GIAY" in branch_ids
    assert "BR_HA_DONG" in branch_ids


def test_get_categories(asset_service):
    """Kiểm tra lấy danh sách nhóm hàng cấp 1."""
    categories = asset_service.get_categories()
    assert len(categories) >= 4
    cat_names = [c["category_name"] for c in categories]
    assert "Điện lạnh" in cat_names
    assert "Điện tử" in cat_names


def test_calculate_kpi_summary_all_branches(asset_service):
    """Kiểm tra tính toán KPI tài sản kho cho toàn bộ chi nhánh (ROLE_OWNER)."""
    kpi = asset_service.get_kpi_summary(branch_id="ALL", role="ROLE_OWNER")

    assert kpi["total_skus"]["value"] >= 50
    assert kpi["total_on_hand_units"]["value"] > 500
    assert kpi["total_valuation"]["value"] > 1_000_000_000  # Hơn 1 tỷ VNĐ
    assert kpi["total_valuation"]["is_masked"] is False
    assert kpi["total_valuation"]["currency"] == "VND"
    assert "trend_percentage" in kpi["total_valuation"]


def test_calculate_kpi_summary_filtered_by_branch(asset_service):
    """Kiểm tra lọc theo chi nhánh cụ thể."""
    kpi_tong = asset_service.get_kpi_summary(branch_id="BR_KHO_TONG", role="ROLE_OWNER")
    kpi_cg = asset_service.get_kpi_summary(branch_id="BR_CAU_GIAY", role="ROLE_OWNER")

    # Kho Tổng phải có số lượng tồn lớn hơn Showroom Cầu Giấy
    assert kpi_tong["total_on_hand_units"]["value"] > kpi_cg["total_on_hand_units"]["value"]
    assert kpi_tong["total_valuation"]["value"] > kpi_cg["total_valuation"]["value"]


def test_calculate_kpi_summary_filtered_by_category(asset_service):
    """Kiểm tra lọc theo danh mục cụ thể (Điện lạnh)."""
    kpi_all = asset_service.get_kpi_summary(branch_id="ALL", role="ROLE_OWNER")
    kpi_dienlanh = asset_service.get_kpi_summary(branch_id="ALL", category_name="Điện lạnh", role="ROLE_OWNER")

    assert kpi_dienlanh["total_skus"]["value"] < kpi_all["total_skus"]["value"]
    assert kpi_dienlanh["total_valuation"]["value"] < kpi_all["total_valuation"]["value"]


def test_calculate_kpi_summary_filtered_by_brand(asset_service):
    """Kiểm tra lọc theo thương hiệu cụ thể (Sony)."""
    kpi_all = asset_service.get_kpi_summary(branch_id="ALL", role="ROLE_OWNER")
    kpi_sony = asset_service.get_kpi_summary(branch_id="ALL", brand="Sony", role="ROLE_OWNER")

    assert kpi_sony["total_skus"]["value"] < kpi_all["total_skus"]["value"]
    assert kpi_sony["total_valuation"]["value"] < kpi_all["total_valuation"]["value"]



def test_cost_masking_for_warehouse_role(asset_service):
    """Kiểm tra cơ chế Dynamic Cost Masking bảo mật giá vốn cho vai trò Thủ kho (ROLE_WAREHOUSE)."""
    kpi_warehouse = asset_service.get_kpi_summary(branch_id="ALL", role="ROLE_WAREHOUSE")

    assert kpi_warehouse["total_valuation"]["value"] is None
    assert kpi_warehouse["total_valuation"]["is_masked"] is True

    # Tuy nhiên vẫn phải thấy số lượng SKU và số lượng chiếc
    assert kpi_warehouse["total_skus"]["value"] > 0
    assert kpi_warehouse["total_on_hand_units"]["value"] > 0


def test_top_capital_tied_products_owner_vs_warehouse(asset_service):
    """Kiểm tra top 10 sản phẩm đọng vốn và phân quyền hiển thị."""
    # 1. Owner role: thấy đầy đủ cost_price và total_cost
    top_products_owner = asset_service.get_top_capital_products(branch_id="ALL", limit=10, role="ROLE_OWNER")
    assert len(top_products_owner) == 10
    assert top_products_owner[0]["total_cost"] >= top_products_owner[1]["total_cost"]  # Sắp xếp giảm dần
    assert top_products_owner[0]["cost_price"] is not None

    # 2. Warehouse role: cost_price và total_cost bị ẩn
    top_products_wh = asset_service.get_top_capital_products(branch_id="ALL", limit=10, role="ROLE_WAREHOUSE")
    assert len(top_products_wh) == 10
    assert top_products_wh[0]["cost_price"] is None
    assert top_products_wh[0]["total_cost"] is None
    assert top_products_wh[0]["on_hand_qty"] > 0


def test_category_allocation(asset_service):
    """Kiểm tra cơ cấu phân bổ vốn theo ngành hàng."""
    allocations = asset_service.get_category_allocation(branch_id="ALL", role="ROLE_OWNER")
    assert len(allocations) >= 4
    total_share = sum(item["percentage"] for item in allocations)
    assert pytest.approx(total_share, rel=1e-2) == 100.0  # Tổng tỷ lệ ~ 100%
