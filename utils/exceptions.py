"""
カスタム例外定義
アプリケーション全体で使用する例外クラス
"""


class AppException(Exception):
    """アプリケーション基底例外"""
    
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self):
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


# ===== データベース関連例外 =====

class DatabaseException(AppException):
    """データベース関連の基底例外"""
    pass


class RecordNotFoundException(DatabaseException):
    """レコードが見つからない"""
    
    def __init__(self, model_name: str, record_id: int = None, details: dict = None):
        message = f"{model_name} not found"
        if record_id:
            message += f" (ID: {record_id})"
        super().__init__(message, details)


class DuplicateRecordException(DatabaseException):
    """重複レコード"""
    
    def __init__(self, model_name: str, field: str = None, value: str = None, details: dict = None):
        message = f"Duplicate {model_name}"
        if field and value:
            message += f" ({field}: {value})"
        super().__init__(message, details)


class IntegrityConstraintException(DatabaseException):
    """整合性制約違反"""
    
    def __init__(self, message: str, constraint: str = None, details: dict = None):
        if constraint:
            message = f"{message} (Constraint: {constraint})"
        super().__init__(message, details)


class DatabaseConnectionException(DatabaseException):
    """データベース接続エラー"""
    pass


# ===== API関連例外 =====

class APIException(AppException):
    """API関連の基底例外"""
    pass


class GmailAPIException(APIException):
    """Gmail API エラー"""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        if error_code:
            message = f"Gmail API Error [{error_code}]: {message}"
        super().__init__(message, details)


class GoogleMapsAPIException(APIException):
    """Google Maps API エラー"""
    
    def __init__(self, message: str, status: str = None, details: dict = None):
        if status:
            message = f"Google Maps API Error [{status}]: {message}"
        super().__init__(message, details)


class GoogleFormsAPIException(APIException):
    """Google Forms API エラー"""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        if error_code:
            message = f"Google Forms API Error [{error_code}]: {message}"
        super().__init__(message, details)


class APIAuthenticationException(APIException):
    """API認証エラー"""
    pass


class APIRateLimitException(APIException):
    """APIレート制限エラー"""
    pass


# ===== LLM関連例外 =====

class LLMException(AppException):
    """LLM関連の基底例外"""
    pass


class ModelNotAvailableException(LLMException):
    """LLMモデルが利用不可"""
    
    def __init__(self, model_name: str, details: dict = None):
        message = f"LLM model '{model_name}' is not available"
        super().__init__(message, details)


class GenerationFailedException(LLMException):
    """LLM生成失敗"""
    
    def __init__(self, message: str = "LLM generation failed", details: dict = None):
        super().__init__(message, details)


class PromptTooLongException(LLMException):
    """プロンプトが長すぎる"""
    
    def __init__(self, token_count: int, max_tokens: int, details: dict = None):
        message = f"Prompt too long: {token_count} tokens (max: {max_tokens})"
        super().__init__(message, details)


# ===== バリデーション関連例外 =====

class ValidationException(AppException):
    """バリデーション関連の基底例外"""
    pass


class InvalidInputException(ValidationException):
    """無効な入力"""
    
    def __init__(self, field: str, value: str = None, reason: str = None, details: dict = None):
        message = f"Invalid input for field '{field}'"
        if value:
            message += f": '{value}'"
        if reason:
            message += f" ({reason})"
        super().__init__(message, details)


class ConstraintViolationException(ValidationException):
    """制約違反"""
    
    def __init__(self, constraint: str, message: str = None, details: dict = None):
        if not message:
            message = f"Constraint violation: {constraint}"
        super().__init__(message, details)


class RequiredFieldException(ValidationException):
    """必須フィールド未入力"""
    
    def __init__(self, field: str, details: dict = None):
        message = f"Required field '{field}' is missing"
        super().__init__(message, details)


# ===== ビジネスロジック関連例外 =====

class BusinessLogicException(AppException):
    """ビジネスロジック関連の基底例外"""
    pass


class GAOptimizationException(BusinessLogicException):
    """GA最適化エラー"""
    pass


class AssignmentException(BusinessLogicException):
    """配置関連エラー"""
    pass


class InsufficientCapacityException(AssignmentException):
    """受入人数不足"""
    
    def __init__(self, hospital_name: str, capacity: int, requested: int, details: dict = None):
        message = f"Insufficient capacity at '{hospital_name}': {capacity} available, {requested} requested"
        super().__init__(message, details)


# ===== ファイル操作関連例外 =====

class FileOperationException(AppException):
    """ファイル操作関連の基底例外"""
    pass


class FileNotFoundException(FileOperationException):
    """ファイルが見つからない"""
    
    def __init__(self, file_path: str, details: dict = None):
        message = f"File not found: {file_path}"
        super().__init__(message, details)


class FileWriteException(FileOperationException):
    """ファイル書き込みエラー"""
    
    def __init__(self, file_path: str, reason: str = None, details: dict = None):
        message = f"Failed to write file: {file_path}"
        if reason:
            message += f" ({reason})"
        super().__init__(message, details)


class BackupException(FileOperationException):
    """バックアップエラー"""
    pass


class RestoreException(FileOperationException):
    """リストアエラー"""
    pass


# ===== エクスポート =====

__all__ = [
    # Base
    "AppException",
    
    # Database
    "DatabaseException",
    "RecordNotFoundException",
    "DuplicateRecordException",
    "IntegrityConstraintException",
    "DatabaseConnectionException",
    
    # API
    "APIException",
    "GmailAPIException",
    "GoogleMapsAPIException",
    "GoogleFormsAPIException",
    "APIAuthenticationException",
    "APIRateLimitException",
    
    # LLM
    "LLMException",
    "ModelNotAvailableException",
    "GenerationFailedException",
    "PromptTooLongException",
    
    # Validation
    "ValidationException",
    "InvalidInputException",
    "ConstraintViolationException",
    "RequiredFieldException",
    
    # Business Logic
    "BusinessLogicException",
    "GAOptimizationException",
    "AssignmentException",
    "InsufficientCapacityException",
    
    # File Operations
    "FileOperationException",
    "FileNotFoundException",
    "FileWriteException",
    "BackupException",
    "RestoreException",
]
