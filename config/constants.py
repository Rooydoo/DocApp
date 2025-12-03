"""
アプリケーション定数定義
"""
from typing import Final

# ===== UI関連定数 =====

# カラーパレット
class Colors:
    """UIカラー定義"""
    # プライマリカラー
    PRIMARY: Final[str] = "#3498db"
    PRIMARY_HOVER: Final[str] = "#2980b9"
    
    # グラデーション
    GRADIENT_START: Final[str] = "#667eea"
    GRADIENT_END: Final[str] = "#764ba2"
    
    # セカンダリカラー
    DARK_GRAY: Final[str] = "#2c3e50"
    MEDIUM_GRAY: Final[str] = "#34495e"
    LIGHT_GRAY: Final[str] = "#ecf0f1"
    
    # 背景色
    BG_MAIN: Final[str] = "#f8f9fa"
    BG_CARD: Final[str] = "#ffffff"
    
    # テキスト色
    TEXT_PRIMARY: Final[str] = "#2c3e50"
    TEXT_SECONDARY: Final[str] = "#7f8c8d"
    TEXT_WHITE: Final[str] = "#ffffff"
    
    # アクセントカラー
    SUCCESS: Final[str] = "#27ae60"
    WARNING: Final[str] = "#f39c12"
    ERROR: Final[str] = "#e74c3c"
    INFO: Final[str] = "#3498db"


# フォント設定
class Fonts:
    """フォント定義"""
    FAMILY: Final[str] = "Meiryo"
    
    # サイズ
    TITLE: Final[int] = 18
    SUBTITLE: Final[int] = 16
    BODY: Final[int] = 14
    CAPTION: Final[int] = 13
    SMALL: Final[int] = 12
    
    # ウェイト
    NORMAL: Final[str] = "normal"
    MEDIUM: Final[str] = "normal"  # CustomTkinterは"medium"未対応
    BOLD: Final[str] = "bold"


# スペーシング
class Spacing:
    """スペーシング定義"""
    # パディング
    PADDING_LARGE: Final[int] = 24
    PADDING_MEDIUM: Final[int] = 16
    PADDING_SMALL: Final[int] = 12
    PADDING_XSMALL: Final[int] = 8
    
    # マージン
    MARGIN_SECTION: Final[int] = 24
    MARGIN_ELEMENT: Final[int] = 16
    MARGIN_COMPONENT: Final[int] = 12
    
    # ボーダー半径
    RADIUS_CARD: Final[int] = 8
    RADIUS_BUTTON: Final[int] = 6
    RADIUS_INPUT: Final[int] = 6
    RADIUS_COPILOT: Final[int] = 12


# ウィンドウサイズ
class WindowSize:
    """ウィンドウサイズ定義"""
    MIN_WIDTH: Final[int] = 1280
    MIN_HEIGHT: Final[int] = 720
    DEFAULT_WIDTH: Final[int] = 1400
    DEFAULT_HEIGHT: Final[int] = 900
    
    # タイトルバー・フッター
    TITLEBAR_HEIGHT: Final[int] = 44
    TABBAR_HEIGHT: Final[int] = 60
    FOOTER_HEIGHT: Final[int] = 36
    
    # Copilot
    COPILOT_WIDTH: Final[int] = 360
    COPILOT_HEIGHT: Final[int] = 460
    COPILOT_MINIMIZED_SIZE: Final[int] = 60


# ===== ビジネスロジック定数 =====

# 職員タイプ
class StaffType:
    """職員種別"""
    RESIDENT_DOCTOR: Final[str] = "選考医"
    ASSISTANT_PROFESSOR: Final[str] = "助教"
    LECTURER: Final[str] = "講師"
    ASSOCIATE_PROFESSOR: Final[str] = "准教授"
    PROFESSOR: Final[str] = "教授"
    ADMINISTRATIVE: Final[str] = "事務職員"
    
    @classmethod
    def all(cls) -> list[str]:
        """全ての職員タイプを取得"""
        return [
            cls.RESIDENT_DOCTOR,
            cls.ASSISTANT_PROFESSOR,
            cls.LECTURER,
            cls.ASSOCIATE_PROFESSOR,
            cls.PROFESSOR,
            cls.ADMINISTRATIVE
        ]


# 配置結果
class AssignmentStatus:
    """配置ステータス"""
    MATCHED: Final[str] = "マッチ"
    MISMATCHED: Final[str] = "アンマッチ"
    PENDING: Final[str] = "未確定"


# アンマッチ理由
class MismatchReason:
    """アンマッチ理由"""
    CAPACITY_FULL: Final[str] = "受入人数上限"
    LOW_FITNESS: Final[str] = "適合度不足"
    CONSTRAINT_VIOLATION: Final[str] = "制約違反"
    NO_PREFERENCE: Final[str] = "希望なし"


# 外勤曜日
class Weekday:
    """曜日"""
    MONDAY: Final[str] = "月"
    TUESDAY: Final[str] = "火"
    WEDNESDAY: Final[str] = "水"
    THURSDAY: Final[str] = "木"
    FRIDAY: Final[str] = "金"
    SATURDAY: Final[str] = "土"
    SUNDAY: Final[str] = "日"
    
    @classmethod
    def all(cls) -> list[str]:
        """全ての曜日を取得"""
        return [
            cls.MONDAY,
            cls.TUESDAY,
            cls.WEDNESDAY,
            cls.THURSDAY,
            cls.FRIDAY,
            cls.SATURDAY,
            cls.SUNDAY
        ]


# 時間帯
class TimeSlot:
    """時間帯"""
    MORNING: Final[str] = "午前"
    AFTERNOON: Final[str] = "午後"
    EVENING: Final[str] = "夜間"
    
    @classmethod
    def all(cls) -> list[str]:
        """全ての時間帯を取得"""
        return [cls.MORNING, cls.AFTERNOON, cls.EVENING]


# ===== データベース関連定数 =====

# テーブル名
class TableName:
    """テーブル名"""
    HOSPITAL: Final[str] = "hospital"
    STAFF: Final[str] = "staff"
    ASSIGNMENT: Final[str] = "assignment"
    COMMUTE_CACHE: Final[str] = "commute_cache"
    STAFF_WEIGHT: Final[str] = "staff_weight"
    OUTPATIENT_SLOT: Final[str] = "outpatient_slot"
    OUTPATIENT_ASSIGNMENT: Final[str] = "outpatient_assignment"
    MAIL_TEMPLATE: Final[str] = "mail_template"
    DOCUMENT_TEMPLATE: Final[str] = "document_template"
    SYSTEM_CONFIG: Final[str] = "system_config"
    BACKUP_HISTORY: Final[str] = "backup_history"
    # GA用評価要素テーブル
    EVALUATION_FACTOR: Final[str] = "evaluation_factor"
    STAFF_FACTOR_WEIGHT: Final[str] = "staff_factor_weight"
    ADMIN_EVALUATION: Final[str] = "admin_evaluation"
    HOSPITAL_CHOICE: Final[str] = "hospital_choice"


# 評価要素タイプ
class FactorType:
    """評価要素タイプ"""
    STAFF_PREFERENCE: Final[str] = "staff_preference"  # 専攻医が重視する要素（年収、通勤等）
    ADMIN_EVALUATION: Final[str] = "admin_evaluation"  # 医局側の評価要素（学術実績、人柄等）

    @classmethod
    def all(cls) -> list[str]:
        """全てのタイプを取得"""
        return [cls.STAFF_PREFERENCE, cls.ADMIN_EVALUATION]

    @classmethod
    def display_name(cls, factor_type: str) -> str:
        """表示名を取得"""
        names = {
            cls.STAFF_PREFERENCE: "専攻医重視要素",
            cls.ADMIN_EVALUATION: "医局側評価要素",
        }
        return names.get(factor_type, factor_type)


# ===== API関連定数 =====

# Google Maps API
class GoogleMapsConfig:
    """Google Maps設定"""
    MODE: Final[str] = "driving"  # 移動手段: 車のみ
    UNITS: Final[str] = "metric"  # 単位: メートル法
    TIMEOUT_SECONDS: Final[int] = 10  # タイムアウト（秒）
    MAX_RETRIES: Final[int] = 3  # 最大リトライ回数


# Gmail API スコープ
class GmailScopes:
    """Gmail APIスコープ"""
    COMPOSE: Final[str] = "https://www.googleapis.com/auth/gmail.compose"
    READONLY: Final[str] = "https://www.googleapis.com/auth/gmail.readonly"
    
    @classmethod
    def all(cls) -> list[str]:
        """全てのスコープを取得"""
        return [cls.COMPOSE, cls.READONLY]


# Google Forms API スコープ
class FormsScopes:
    """Google Forms APIスコープ"""
    RESPONSES_READONLY: Final[str] = "https://www.googleapis.com/auth/forms.responses.readonly"

    @classmethod
    def all(cls) -> list[str]:
        """全てのスコープを取得"""
        return [cls.RESPONSES_READONLY]


# Google Sheets API スコープ
class SheetsScopes:
    """Google Sheets APIスコープ"""
    SPREADSHEETS: Final[str] = "https://www.googleapis.com/auth/spreadsheets"
    SPREADSHEETS_READONLY: Final[str] = "https://www.googleapis.com/auth/spreadsheets.readonly"
    DRIVE_FILE: Final[str] = "https://www.googleapis.com/auth/drive.file"

    @classmethod
    def all(cls) -> list[str]:
        """全てのスコープを取得"""
        return [cls.SPREADSHEETS, cls.DRIVE_FILE]


# ===== LLM関連定数 =====

# LLMチェーン名
class LLMChainName:
    """LLMチェーン名"""
    PERSONNEL_NOTIFICATION: Final[str] = "personnel_notification"
    TEMPLATE_CUSTOMIZE: Final[str] = "template_customize"
    DOCUMENT_GENERATION: Final[str] = "document_generation"
    DOCUMENT_CONVERSATION: Final[str] = "document_conversation"
    COMMAND_INTERPRETATION: Final[str] = "command_interpretation"
    QA_RESPONSE: Final[str] = "qa_response"


# ===== その他定数 =====

# バックアップ
class BackupConfig:
    """バックアップ設定"""
    AUTO_BACKUP_HOUR: Final[int] = 3  # 午前3時に自動バックアップ
    MAX_BACKUPS: Final[int] = 10  # 保持する最大バックアップ数
    BACKUP_FORMAT: Final[str] = "backup_%Y%m%d_%H%M%S.zip"


# バリデーション
class ValidationLimits:
    """バリデーション制限"""
    MAX_NAME_LENGTH: Final[int] = 100
    MAX_ADDRESS_LENGTH: Final[int] = 200
    MAX_EMAIL_LENGTH: Final[int] = 100
    MAX_NOTES_LENGTH: Final[int] = 1000
    MIN_CAPACITY: Final[int] = 0
    MAX_CAPACITY: Final[int] = 100
    MIN_ROTATION_MONTHS: Final[int] = 1
    MAX_ROTATION_MONTHS: Final[int] = 36


# 通勤時間キャッシュ
class CommuteCacheConfig:
    """通勤時間キャッシュ設定"""
    # キャッシュ更新のバッチサイズ（ログ出力頻度）
    BATCH_LOG_SIZE: Final[int] = 10
    
    # キャッシュの有効期限（日数）- 将来的に自動更新する場合に使用
    CACHE_EXPIRY_DAYS: Final[int] = 90