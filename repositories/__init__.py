"""
リポジトリ統合
全てのリポジトリをここからインポート可能
"""
from repositories.base_repository import BaseRepository
from repositories.hospital_repository import HospitalRepository
from repositories.staff_repository import StaffRepository
from repositories.assignment_repository import AssignmentRepository
from repositories.commute_cache_repository import CommuteCacheRepository
from repositories.staff_weight_repository import StaffWeightRepository
from repositories.outpatient_slot_repository import OutpatientSlotRepository
from repositories.outpatient_assignment_repository import OutpatientAssignmentRepository
from repositories.mail_template_repository import MailTemplateRepository
from repositories.document_template_repository import DocumentTemplateRepository
from repositories.system_config_repository import SystemConfigRepository
from repositories.backup_history_repository import BackupHistoryRepository
# GA用評価要素リポジトリ
from repositories.evaluation_factor_repository import EvaluationFactorRepository
from repositories.staff_factor_weight_repository import StaffFactorWeightRepository
from repositories.admin_evaluation_repository import AdminEvaluationRepository
from repositories.hospital_choice_repository import HospitalChoiceRepository

__all__ = [
    "BaseRepository",
    "HospitalRepository",
    "StaffRepository",
    "AssignmentRepository",
    "CommuteCacheRepository",
    "StaffWeightRepository",
    "OutpatientSlotRepository",
    "OutpatientAssignmentRepository",
    "MailTemplateRepository",
    "DocumentTemplateRepository",
    "SystemConfigRepository",
    "BackupHistoryRepository",
    # GA用評価要素リポジトリ
    "EvaluationFactorRepository",
    "StaffFactorWeightRepository",
    "AdminEvaluationRepository",
    "HospitalChoiceRepository",
]