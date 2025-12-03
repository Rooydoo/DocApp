"""
ダッシュボードデータ集計サービス
"""
from typing import Dict, List
from datetime import datetime, timedelta
from database.connection import get_db_session
from repositories.hospital_repository import HospitalRepository
from repositories.staff_repository import StaffRepository
from repositories.assignment_repository import AssignmentRepository
from repositories.commute_cache_repository import CommuteCacheRepository
from config.constants import StaffType, AssignmentStatus
from utils.logger import get_logger

logger = get_logger(__name__)


class DashboardService:
    """
    ダッシュボードデータ集計サービス
    
    責務:
    - 各種メトリクスの集計
    - アラート情報の生成
    - 最近のアクティビティ取得
    """
    
    def get_metrics(self) -> Dict:
        """
        メトリクスデータを取得
        
        Returns:
            Dict: {
                "hospital_count": int,          # 病院数
                "staff_count": int,             # 職員総数
                "resident_count": int,          # 選考医数
                "assigned_count": int,          # 配置済み数
                "unassigned_count": int,        # 未配置数
                "staff_by_type": Dict[str, int] # 職員種別ごとの人数
            }
        """
        try:
            with get_db_session() as db:
                hospital_repo = HospitalRepository(db)
                staff_repo = StaffRepository(db)
                assignment_repo = AssignmentRepository(db)
                
                # 病院数
                hospital_count = len(hospital_repo.get_all())
                
                # 職員数
                all_staff = staff_repo.get_all()
                staff_count = len(all_staff)
                
                # 選考医数
                resident_doctors = staff_repo.get_resident_doctors()
                resident_count = len(resident_doctors)
                
                # 配置数
                assignments = assignment_repo.get_all()
                assigned_count = sum(1 for a in assignments if a.status == AssignmentStatus.MATCHED)
                
                # 未配置数（選考医のうち配置されていない人数）
                assigned_staff_ids = {a.staff_id for a in assignments if a.status == AssignmentStatus.MATCHED}
                unassigned_count = sum(1 for s in resident_doctors if s.id not in assigned_staff_ids)
                
                # 職員種別ごとの人数
                staff_by_type = {}
                for staff_type in StaffType.all():
                    staff_by_type[staff_type] = staff_repo.count_by_staff_type(staff_type)
                
                return {
                    "hospital_count": hospital_count,
                    "staff_count": staff_count,
                    "resident_count": resident_count,
                    "assigned_count": assigned_count,
                    "unassigned_count": unassigned_count,
                    "staff_by_type": staff_by_type
                }
        
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return {
                "hospital_count": 0,
                "staff_count": 0,
                "resident_count": 0,
                "assigned_count": 0,
                "unassigned_count": 0,
                "staff_by_type": {}
            }
    
    def get_alerts(self) -> List[Dict]:
        """
        アラート情報を取得
        
        Returns:
            List[Dict]: [
                {
                    "level": str,      # "error", "warning", "info"
                    "icon": str,       # "🔴", "🟡", "🔵"
                    "message": str
                }
            ]
        """
        alerts = []
        
        try:
            with get_db_session() as db:
                assignment_repo = AssignmentRepository(db)
                staff_repo = StaffRepository(db)
                hospital_repo = HospitalRepository(db)
                cache_repo = CommuteCacheRepository(db)
                
                # アンマッチ数チェック
                assignments = assignment_repo.get_all()
                mismatched_count = sum(1 for a in assignments if a.status == AssignmentStatus.MISMATCHED)
                
                if mismatched_count > 0:
                    alerts.append({
                        "level": "error",
                        "icon": "🔴",
                        "message": f"アンマッチ: {mismatched_count}件"
                    })
                
                # 未配置の選考医チェック
                resident_doctors = staff_repo.get_resident_doctors()
                assigned_staff_ids = {a.staff_id for a in assignments}
                unassigned = [s for s in resident_doctors if s.id not in assigned_staff_ids]
                
                if len(unassigned) > 0:
                    alerts.append({
                        "level": "warning",
                        "icon": "🟡",
                        "message": f"未配置の選考医: {len(unassigned)}人"
                    })
                
                # 通勤時間キャッシュ未計算チェック
                residents_with_address = staff_repo.get_resident_doctors_with_address()
                hospitals_with_address = hospital_repo.get_hospitals_with_address()
                
                expected_cache_count = len(residents_with_address) * len(hospitals_with_address)
                actual_cache_count = len(cache_repo.get_all())
                missing_cache_count = expected_cache_count - actual_cache_count
                
                if missing_cache_count > 0:
                    alerts.append({
                        "level": "warning",
                        "icon": "🟡",
                        "message": f"通勤時間キャッシュ未計算: {missing_cache_count}組み合わせ"
                    })
                
                # アラートがない場合
                if not alerts:
                    alerts.append({
                        "level": "info",
                        "icon": "🟢",
                        "message": "問題はありません"
                    })
        
        except Exception as e:
            logger.error(f"Failed to get alerts: {e}")
            alerts.append({
                "level": "error",
                "icon": "🔴",
                "message": f"アラート取得エラー: {str(e)}"
            })
        
        return alerts
    
    def get_recent_activities(self, limit: int = 10) -> List[Dict]:
        """
        最近のアクティビティを取得
        
        Args:
            limit: 取得件数
        
        Returns:
            List[Dict]: [
                {
                    "timestamp": datetime,
                    "type": str,       # "hospital", "staff", "assignment"
                    "icon": str,
                    "message": str
                }
            ]
        """
        activities = []
        
        try:
            with get_db_session() as db:
                hospital_repo = HospitalRepository(db)
                staff_repo = StaffRepository(db)
                assignment_repo = AssignmentRepository(db)
                
                # 病院の最近の登録
                hospitals = hospital_repo.get_all()
                hospitals_sorted = sorted(hospitals, key=lambda h: h.created_at, reverse=True)
                for hospital in hospitals_sorted[:5]:
                    activities.append({
                        "timestamp": hospital.created_at,
                        "type": "hospital",
                        "icon": "🏥",
                        "message": f"病院「{hospital.name}」を登録"
                    })
                
                # 職員の最近の登録
                staff = staff_repo.get_all()
                staff_sorted = sorted(staff, key=lambda s: s.created_at, reverse=True)
                for s in staff_sorted[:5]:
                    activities.append({
                        "timestamp": s.created_at,
                        "type": "staff",
                        "icon": "👤",
                        "message": f"{s.staff_type}「{s.name}」を登録"
                    })
                
                # 配置の最近の変更
                assignments = assignment_repo.get_all()
                assignments_sorted = sorted(assignments, key=lambda a: a.created_at, reverse=True)
                for assignment in assignments_sorted[:5]:
                    staff_obj = staff_repo.get(assignment.staff_id)
                    hospital_obj = hospital_repo.get(assignment.hospital_id)
                    
                    if staff_obj and hospital_obj:
                        activities.append({
                            "timestamp": assignment.created_at,
                            "type": "assignment",
                            "icon": "📍",
                            "message": f"「{staff_obj.name}」を「{hospital_obj.name}」に配置"
                        })
                
                # タイムスタンプでソート
                activities.sort(key=lambda a: a["timestamp"], reverse=True)
                
                return activities[:limit]
        
        except Exception as e:
            logger.error(f"Failed to get recent activities: {e}")
            return []
    
    def get_capacity_status(self) -> Dict:
        """
        病院の受入人数状況を取得
        
        Returns:
            Dict: {
                "total_capacity": int,          # 総受入人数
                "used_capacity": int,           # 使用中
                "available_capacity": int,      # 空き
                "utilization_rate": float       # 使用率（%）
            }
        """
        try:
            with get_db_session() as db:
                hospital_repo = HospitalRepository(db)
                assignment_repo = AssignmentRepository(db)
                
                hospitals = hospital_repo.get_all()
                
                # 各病院の専攻医受入人数を合計
                total_capacity = sum(h.resident_capacity for h in hospitals)
                
                # 配置済み数
                assignments = assignment_repo.get_all()
                used_capacity = sum(1 for a in assignments if a.status == AssignmentStatus.MATCHED)
                
                # 空き
                available_capacity = max(0, total_capacity - used_capacity)
                
                # 使用率
                utilization_rate = (used_capacity / total_capacity * 100) if total_capacity > 0 else 0
                
                return {
                    "total_capacity": total_capacity,
                    "used_capacity": used_capacity,
                    "available_capacity": available_capacity,
                    "utilization_rate": round(utilization_rate, 1)
                }
        
        except Exception as e:
            logger.error(f"Failed to get capacity status: {e}")
            return {
                "total_capacity": 0,
                "used_capacity": 0,
                "available_capacity": 0,
                "utilization_rate": 0.0
            }


# シングルトンインスタンス
dashboard_service = DashboardService()
