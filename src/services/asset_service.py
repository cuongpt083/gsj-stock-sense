"""
Dịch vụ Quản lý & Thống kê Tài sản Kho (US 1.1 - Asset Service).
Tuân thủ đặc tả SRS_01_Tong_Quan_Kho.md và hỗ trợ Dynamic Cost Masking.
"""
from typing import Dict, Any, List, Optional
from src.database.connection import get_db_connection


class AssetService:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path

    def _get_connection(self):
        if self.db_path:
            return get_db_connection(self.db_path)
        return get_db_connection()

    def get_branches(self) -> List[Dict[str, Any]]:
        """Lấy danh sách các chi nhánh đang hoạt động."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT branch_id, branch_name, address FROM branches WHERE is_active = 1 ORDER BY branch_id;")
        rows = cursor.fetchall()
        conn.close()
        return [{"branch_id": r["branch_id"], "branch_name": r["branch_name"], "address": r["address"]} for r in rows]

    def get_categories(self) -> List[Dict[str, Any]]:
        """Lấy danh mục cấp 1 (Ngành hàng lớn) từ category_path."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category_path FROM DIM_PRODUCTS WHERE is_active = 1;")
        paths = [r["category_path"] for r in cursor.fetchall()]
        conn.close()

        cat_names = sorted({p.split(">")[0].strip() for p in paths if p})
        return [{"category_id": c, "category_name": c} for c in cat_names]

    def get_kpi_summary(
        self,
        branch_id: str = "ALL",
        category_name: Optional[str] = None,
        brand: Optional[str] = None,
        role: str = "ROLE_OWNER"
    ) -> Dict[str, Any]:
        """
        Tính toán 3 thẻ KPI tài sản kho theo bộ lọc.
        Tự động che giấu giá vốn nếu role == 'ROLE_WAREHOUSE'.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        where_clauses = ["p.is_active = 1"]
        params: List[Any] = []

        if branch_id and branch_id != "ALL":
            where_clauses.append("i.branch_id = ?")
            params.append(branch_id)

        if category_name and category_name != "ALL":
            where_clauses.append("p.category_path LIKE ?")
            params.append(f"{category_name}%")

        if brand and brand != "ALL":
            where_clauses.append("p.brand = ?")
            params.append(brand)

        where_sql = " AND ".join(where_clauses)

        query = f"""
            SELECT 
                COUNT(DISTINCT p.product_code) AS total_skus,
                COALESCE(SUM(i.on_hand_qty), 0) AS total_on_hand_units,
                COALESCE(SUM(i.on_hand_qty * p.cost_price), 0.0) AS total_valuation,
                COALESCE(SUM(i.reserved_qty), 0) AS total_reserved_units,
                COALESCE(SUM(i.atp_qty), 0) AS atp_units,
                COALESCE(SUM(i.in_transit_qty), 0) AS in_transit_units
            FROM inventories i
            JOIN DIM_PRODUCTS p ON i.product_code = p.product_code
            WHERE {where_sql};
        """
        cursor.execute(query, params)
        row = cursor.fetchone()
        conn.close()

        total_skus = row["total_skus"] if row else 0
        total_on_hand = row["total_on_hand_units"] if row else 0
        total_val = float(row["total_valuation"]) if row else 0.0
        total_reserved = row["total_reserved_units"] if row else 0
        atp_units = row["atp_units"] if row else 0
        in_transit = row["in_transit_units"] if row else 0

        # Mô phỏng tỷ lệ biến động tuần/tháng (Trend indicators)
        trend_skus = 2.5
        trend_on_hand = -1.8
        trend_val = -0.5

        is_warehouse = (role == "ROLE_WAREHOUSE")

        return {
            "total_skus": {
                "value": total_skus,
                "trend_percentage": trend_skus,
                "trend_direction": "UP" if trend_skus >= 0 else "DOWN",
            },
            "total_on_hand_units": {
                "value": total_on_hand,
                "trend_percentage": trend_on_hand,
                "trend_direction": "UP" if trend_on_hand >= 0 else "DOWN",
            },
            "total_valuation": {
                "value": None if is_warehouse else total_val,
                "currency": "VND",
                "trend_percentage": None if is_warehouse else trend_val,
                "trend_direction": "DOWN" if trend_val < 0 else "UP",
                "is_masked": is_warehouse,
            },
            "total_reserved_units": total_reserved,
            "atp_units": atp_units,
            "in_transit_units": in_transit,
        }

    def get_top_capital_products(
        self,
        branch_id: str = "ALL",
        limit: int = 10,
        role: str = "ROLE_OWNER"
    ) -> List[Dict[str, Any]]:
        """Lấy danh sách Top N sản phẩm chiếm vốn lưu động lớn nhất."""
        conn = self._get_connection()
        cursor = conn.cursor()

        where_sql = "p.is_active = 1"
        params: List[Any] = []
        if branch_id and branch_id != "ALL":
            where_sql += " AND i.branch_id = ?"
            params.append(branch_id)

        query = f"""
            SELECT 
                p.product_code,
                p.product_name,
                p.brand,
                p.uom,
                p.cost_price,
                SUM(i.on_hand_qty) AS on_hand_qty,
                SUM(i.on_hand_qty * p.cost_price) AS total_cost
            FROM inventories i
            JOIN DIM_PRODUCTS p ON i.product_code = p.product_code
            WHERE {where_sql}
            GROUP BY p.product_code
            ORDER BY total_cost DESC
            LIMIT ?;
        """
        params.append(limit)
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        is_warehouse = (role == "ROLE_WAREHOUSE")
        results = []
        for r in rows:
            results.append({
                "product_code": r["product_code"],
                "product_name": r["product_name"],
                "brand": r["brand"],
                "uom": r["uom"],
                "on_hand_qty": r["on_hand_qty"],
                "cost_price": None if is_warehouse else float(r["cost_price"]),
                "total_cost": None if is_warehouse else float(r["total_cost"]),
            })
        return results

    def get_category_allocation(
        self,
        branch_id: str = "ALL",
        role: str = "ROLE_OWNER"
    ) -> List[Dict[str, Any]]:
        """Cơ cấu phân bổ vốn hoặc số lượng theo ngành hàng cấp 1."""
        conn = self._get_connection()
        cursor = conn.cursor()

        where_sql = "p.is_active = 1"
        params: List[Any] = []
        if branch_id and branch_id != "ALL":
            where_sql += " AND i.branch_id = ?"
            params.append(branch_id)

        query = f"""
            SELECT 
                p.category_path,
                SUM(i.on_hand_qty) AS units,
                SUM(i.on_hand_qty * p.cost_price) AS valuation
            FROM inventories i
            JOIN DIM_PRODUCTS p ON i.product_code = p.product_code
            WHERE {where_sql}
            GROUP BY p.category_path;
        """
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        is_warehouse = (role == "ROLE_WAREHOUSE")
        cat_aggregates: Dict[str, Dict[str, float]] = {}

        for r in rows:
            cat_level_1 = r["category_path"].split(">")[0].strip()
            if cat_level_1 not in cat_aggregates:
                cat_aggregates[cat_level_1] = {"units": 0, "valuation": 0.0}
            cat_aggregates[cat_level_1]["units"] += r["units"]
            cat_aggregates[cat_level_1]["valuation"] += float(r["valuation"])

        metric_key = "units" if is_warehouse else "valuation"
        total_metric = sum(v[metric_key] for v in cat_aggregates.values()) or 1.0

        results = []
        for cat_name, data in sorted(cat_aggregates.items(), key=lambda x: x[1][metric_key], reverse=True):
            pct = round((data[metric_key] / total_metric) * 100, 2)
            results.append({
                "category_name": cat_name,
                "units": data["units"],
                "valuation": None if is_warehouse else data["valuation"],
                "percentage": pct,
            })
        return results
