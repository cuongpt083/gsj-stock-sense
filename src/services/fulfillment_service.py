"""
Dịch vụ Quản lý Giao vận, ATP Engine & Giữ chỗ kho (US 1.2 - Fulfillment Service).
Tuân thủ đặc tả SRS_01_Tong_Quan_Kho.md.
"""
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from src.database.connection import get_db_connection, transaction_scope


class InsufficientATPError(Exception):
    """Ngoại lệ khi số lượng hàng khả dụng (ATP) không đủ để đáp ứng đơn đặt."""
    pass


class FulfillmentService:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path

    def _get_connection(self):
        if self.db_path:
            return get_db_connection(self.db_path)
        return get_db_connection()

    def get_fulfillment_kpi(self, branch_id: str = "ALL") -> Dict[str, Any]:
        """Thống kê chi tiết các chỉ số fulfillment, phân loại đơn trả thẳng vs trả góp."""
        conn = self._get_connection()
        cursor = conn.cursor()

        inv_where = "1=1"
        res_where = "r.status = 'ACTIVE'"
        params_inv: List[Any] = []
        params_res: List[Any] = []

        if branch_id and branch_id != "ALL":
            inv_where += " AND branch_id = ?"
            params_inv.append(branch_id)
            res_where += " AND r.branch_id = ?"
            params_res.append(branch_id)

        # 1. Truy vấn từ inventories
        query_inv = f"""
            SELECT 
                COALESCE(SUM(on_hand_qty), 0) AS on_hand_units,
                COALESCE(SUM(reserved_qty), 0) AS reserved_units,
                COALESCE(SUM(atp_qty), 0) AS atp_units,
                COALESCE(SUM(in_transit_qty), 0) AS in_transit_units
            FROM inventories
            WHERE {inv_where};
        """
        cursor.execute(query_inv, params_inv)
        inv_row = cursor.fetchone()

        # 2. Truy vấn bóc tách phân loại đơn từ inventory_reservations
        query_res = f"""
            SELECT 
                COALESCE(SUM(CASE WHEN r.reservation_type = 'INSTALLMENT_HOLD' THEN r.reserved_qty ELSE 0 END), 0) AS installment_units,
                COALESCE(SUM(CASE WHEN r.reservation_type = 'FULL_HOLD' THEN r.reserved_qty ELSE 0 END), 0) AS full_payment_units,
                COALESCE(SUM(CASE 
                    WHEN r.reservation_type = 'INSTALLMENT_HOLD' AND r.expires_at < DATETIME('now', 'localtime') 
                    THEN r.reserved_qty ELSE 0 END), 0) AS expired_installment_units
            FROM inventory_reservations r
            WHERE {res_where};
        """
        cursor.execute(query_res, params_res)
        res_row = cursor.fetchone()
        conn.close()

        total_reserved = inv_row["reserved_units"] if inv_row else 0
        atp = inv_row["atp_units"] if inv_row else 0
        in_transit = inv_row["in_transit_units"] if inv_row else 0

        inst_units = res_row["installment_units"] if res_row else 0
        full_units = res_row["full_payment_units"] if res_row else 0
        exp_units = res_row["expired_installment_units"] if res_row else 0

        return {
            "total_reserved_units": total_reserved,
            "installment_reserved_units": inst_units,
            "full_payment_reserved_units": full_units,
            "expired_installment_units": exp_units,
            "atp_units": atp,
            "in_transit_units": in_transit,
            "stockout_risk_skus_count": self._count_stockout_risk_skus(branch_id),
        }

    def _count_stockout_risk_skus(self, branch_id: str = "ALL") -> int:
        """Đếm số SKU có nguy cơ hết hàng khả dụng (ATP <= 1)."""
        conn = self._get_connection()
        cursor = conn.cursor()
        where_sql = "atp_qty <= 1"
        params = []
        if branch_id and branch_id != "ALL":
            where_sql += " AND branch_id = ?"
            params.append(branch_id)
        cursor.execute(f"SELECT COUNT(*) FROM inventories WHERE {where_sql};", params)
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def reserve_stock(
        self,
        order_code: str,
        branch_id: str,
        product_code: str,
        quantity: int,
        reservation_type: str = "FULL_HOLD"
    ) -> Dict[str, Any]:
        """
        Cơ chế Khóa giữ hàng chống bán hàng ảo (Anti-Phantom Stock).
        Đảm bảo tính nhất quán qua Database Transaction.
        """
        if quantity <= 0:
            raise ValueError("Số lượng giữ hàng phải lớn hơn 0")

        with transaction_scope(self.db_path) if self.db_path else transaction_scope() as conn:
            cursor = conn.cursor()

            # 1. Kiểm tra tồn kho khả dụng hiện tại
            cursor.execute("""
                SELECT on_hand_qty, reserved_qty, atp_qty 
                FROM inventories 
                WHERE branch_id = ? AND product_code = ?;
            """, (branch_id, product_code))
            inv = cursor.fetchone()

            if not inv:
                raise ValueError(f"Không tìm thấy bản ghi tồn kho cho mã SP '{product_code}' tại chi nhánh '{branch_id}'")

            current_atp = inv["atp_qty"]
            if current_atp < quantity:
                raise InsufficientATPError(
                    f"Sản phẩm {product_code} không đủ số lượng khả dụng. Hiện khả dụng: {current_atp}, yêu cầu: {quantity}."
                )

            # 2. Cập nhật trừ ATP và tăng reserved_qty
            cursor.execute("""
                UPDATE inventories
                SET reserved_qty = reserved_qty + ?,
                    atp_qty = atp_qty - ?,
                    last_updated = DATETIME('now', 'localtime')
                WHERE branch_id = ? AND product_code = ?;
            """, (quantity, quantity, branch_id, product_code))

            # 3. Tính thời gian hết hạn giữ chỗ (Trả góp: 48h, Trả thẳng: 24h)
            now = datetime.now()
            hours_limit = 48 if reservation_type == "INSTALLMENT_HOLD" else 24
            expires_at = (now + timedelta(hours=hours_limit)).strftime("%Y-%m-%d %H:%M:%S")
            res_id = str(uuid.uuid4())

            cursor.execute("""
                INSERT INTO inventory_reservations (
                    reservation_id, order_code, branch_id, product_code, 
                    reserved_qty, reservation_type, status, expires_at, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, 'ACTIVE', ?, DATETIME('now', 'localtime'));
            """, (res_id, order_code, branch_id, product_code, quantity, reservation_type, expires_at))

            return {
                "success": True,
                "reservation_id": res_id,
                "order_code": order_code,
                "product_code": product_code,
                "reserved_qty": quantity,
                "remaining_atp": current_atp - quantity,
                "expires_at": expires_at,
            }

    def release_expired_installment_reservations(self) -> Dict[str, Any]:
        """
        Tiến trình ngầm (Auto-Release Worker):
        Tự động hủy các đơn trả góp bị quá hạn thẩm định 48 giờ và hoàn trả số lượng ATP.
        """
        with transaction_scope(self.db_path) if self.db_path else transaction_scope() as conn:
            cursor = conn.cursor()

            # 1. Tìm các bản ghi giữ chỗ trả góp quá hạn đang ACTIVE
            cursor.execute("""
                SELECT reservation_id, order_code, branch_id, product_code, reserved_qty 
                FROM inventory_reservations
                WHERE reservation_type = 'INSTALLMENT_HOLD' 
                AND status = 'ACTIVE' 
                AND expires_at < DATETIME('now', 'localtime');
            """)
            expired_list = cursor.fetchall()

            if not expired_list:
                return {"released_reservations_count": 0, "restored_units_count": 0}

            total_restored = 0
            for item in expired_list:
                res_id = item["reservation_id"]
                b_id = item["branch_id"]
                p_code = item["product_code"]
                qty = item["reserved_qty"]

                # Hoàn trả vào inventories
                cursor.execute("""
                    UPDATE inventories
                    SET reserved_qty = reserved_qty - ?,
                        atp_qty = atp_qty + ?,
                        last_updated = DATETIME('now', 'localtime')
                    WHERE branch_id = ? AND product_code = ?;
                """, (qty, qty, b_id, p_code))

                # Cập nhật trạng thái reservation sang RELEASED
                cursor.execute("""
                    UPDATE inventory_reservations
                    SET status = 'RELEASED',
                        updated_at = DATETIME('now', 'localtime')
                    WHERE reservation_id = ?;
                """, (res_id,))

                # Gắn cờ hủy vào FACT_ORDERS
                cursor.execute("""
                    UPDATE FACT_ORDERS
                    SET status = 'Đã hủy',
                        note = COALESCE(note, '') || ' [Tự động hủy giữ hàng do quá hạn 48h]'
                    WHERE order_code = ?;
                """, (item["order_code"],))

                total_restored += qty

            return {
                "released_reservations_count": len(expired_list),
                "restored_units_count": total_restored,
            }

    def get_stock_status_table(
        self,
        branch_id: str = "ALL",
        status_filter: str = "ALL",
        search_term: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Lấy danh sách chi tiết trạng thái hàng hóa và đơn hàng."""
        conn = self._get_connection()
        cursor = conn.cursor()

        where_clauses = ["p.is_active = 1"]
        params: List[Any] = []

        if branch_id and branch_id != "ALL":
            where_clauses.append("i.branch_id = ?")
            params.append(branch_id)

        if search_term:
            where_clauses.append("(p.product_code LIKE ? OR p.product_name LIKE ? OR p.brand LIKE ?)")
            term = f"%{search_term}%"
            params.extend([term, term, term])

        where_sql = " AND ".join(where_clauses)

        query = f"""
            SELECT 
                p.product_code,
                p.product_name,
                p.brand,
                p.category_path,
                p.uom,
                p.cost_price,
                p.sale_price,
                SUM(i.on_hand_qty) AS on_hand_qty,
                SUM(i.reserved_qty) AS reserved_qty,
                SUM(i.atp_qty) AS atp_qty,
                SUM(i.in_transit_qty) AS in_transit_qty
            FROM inventories i
            JOIN DIM_PRODUCTS p ON i.product_code = p.product_code
            WHERE {where_sql}
            GROUP BY p.product_code
            ORDER BY atp_qty ASC, on_hand_qty DESC;
        """
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        results = []
        for r in rows:
            atp = r["atp_qty"]
            on_hand = r["on_hand_qty"]
            in_transit = r["in_transit_qty"]

            # Xác định cờ trạng thái (Status Flag)
            if atp <= 0:
                flag = "HẾT KHẢ DỤNG"
            elif atp <= 3:
                flag = "SẮP HẾT"
            elif in_transit > 0:
                flag = "ĐANG VỀ"
            else:
                flag = "BÌNH THƯỜNG"

            # Áp dụng bộ lọc trạng thái (status_filter)
            if status_filter == "LOW_ATP" and flag not in ("HẾT KHẢ DỤNG", "SẮP HẾT"):
                continue
            if status_filter == "STOCKOUT" and flag != "HẾT KHẢ DỤNG":
                continue
            if status_filter == "HAS_IN_TRANSIT" and in_transit <= 0:
                continue

            results.append({
                "product_code": r["product_code"],
                "product_name": r["product_name"],
                "brand": r["brand"],
                "category_path": r["category_path"],
                "uom": r["uom"],
                "on_hand_qty": on_hand,
                "reserved_qty": r["reserved_qty"],
                "atp_qty": atp,
                "in_transit_qty": in_transit,
                "projected_stock": atp + in_transit,
                "status_flag": flag,
            })

        return results
