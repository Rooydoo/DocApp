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
]