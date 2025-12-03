"""
データベースモデル統合
全てのモデルをここからインポート可能
"""
from database.models.hospital import Hospital
from database.models.staff import Staff
from database.models.assignment import Assignment
from database.models.commute_cache import CommuteCache
from database.models.staff_weight import StaffWeight
from database.models.outpatient_slot import OutpatientSlot
from database.models.outpatient_assignment import OutpatientAssignment
from database.models.mail_template import MailTemplate
from database.models.document_template import DocumentTemplate
from database.models.system_config import SystemConfig
from database.models.backup_history import BackupHistory
# GA用評価要素テーブル
from database.models.evaluation_factor import EvaluationFactor
from database.models.staff_factor_weight import StaffFactorWeight
from database.models.admin_evaluation import AdminEvaluation
from database.models.hospital_choice import HospitalChoice

__all__ = [
    "Hospital",
    "Staff",
    "Assignment",
    "CommuteCache",
    "StaffWeight",
    "OutpatientSlot",
    "OutpatientAssignment",
    "MailTemplate",
    "DocumentTemplate",
    "SystemConfig",
    "BackupHistory",
    # GA用評価要素テーブル
    "EvaluationFactor",
    "StaffFactorWeight",
    "AdminEvaluation",
    "HospitalChoice",
]