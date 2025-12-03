"""
バリデーションヘルパー
共通的なバリデーション処理
"""
import re
from typing import Any
from config.constants import ValidationLimits
from utils.exceptions import InvalidInputException, RequiredFieldException


def validate_required(field_name: str, value: Any) -> None:
    """
    必須フィールドチェック
    
    Args:
        field_name: フィールド名
        value: 値
    
    Raises:
        RequiredFieldException: 値がNoneまたは空文字の場合
    """
    if value is None or (isinstance(value, str) and value.strip() == ""):
        raise RequiredFieldException(field_name)


def validate_email(email: str, field_name: str = "email") -> str:
    """
    メールアドレスの検証
    
    Args:
        email: メールアドレス
        field_name: フィールド名
    
    Returns:
        str: 正規化されたメールアドレス
    
    Raises:
        InvalidInputException: 無効なメールアドレスの場合
    """
    if not email:
        raise RequiredFieldException(field_name)
    
    email = email.strip().lower()
    
    # 簡易的なメールアドレス検証
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise InvalidInputException(
            field_name, 
            email, 
            "Invalid email format"
        )
    
    if len(email) > ValidationLimits.MAX_EMAIL_LENGTH:
        raise InvalidInputException(
            field_name,
            email,
            f"Email too long (max: {ValidationLimits.MAX_EMAIL_LENGTH})"
        )
    
    return email


def validate_string_length(
    value: str,
    field_name: str,
    min_length: int = None,
    max_length: int = None
) -> str:
    """
    文字列長の検証
    
    Args:
        value: 検証する文字列
        field_name: フィールド名
        min_length: 最小文字数
        max_length: 最大文字数
    
    Returns:
        str: トリムされた文字列
    
    Raises:
        InvalidInputException: 文字列長が範囲外の場合
    """
    if value is None:
        value = ""
    
    value = value.strip()
    length = len(value)
    
    if min_length is not None and length < min_length:
        raise InvalidInputException(
            field_name,
            value,
            f"Too short (min: {min_length} characters)"
        )
    
    if max_length is not None and length > max_length:
        raise InvalidInputException(
            field_name,
            value,
            f"Too long (max: {max_length} characters)"
        )
    
    return value


def validate_integer_range(
    value: int,
    field_name: str,
    min_value: int = None,
    max_value: int = None
) -> int:
    """
    整数値の範囲検証
    
    Args:
        value: 検証する整数
        field_name: フィールド名
        min_value: 最小値
        max_value: 最大値
    
    Returns:
        int: 検証済み整数
    
    Raises:
        InvalidInputException: 値が範囲外の場合
    """
    if not isinstance(value, int):
        try:
            value = int(value)
        except (ValueError, TypeError):
            raise InvalidInputException(
                field_name,
                str(value),
                "Must be an integer"
            )
    
    if min_value is not None and value < min_value:
        raise InvalidInputException(
            field_name,
            str(value),
            f"Too small (min: {min_value})"
        )
    
    if max_value is not None and value > max_value:
        raise InvalidInputException(
            field_name,
            str(value),
            f"Too large (max: {max_value})"
        )
    
    return value


def validate_float_range(
    value: float,
    field_name: str,
    min_value: float = None,
    max_value: float = None
) -> float:
    """
    浮動小数点数の範囲検証
    
    Args:
        value: 検証する浮動小数点数
        field_name: フィールド名
        min_value: 最小値
        max_value: 最大値
    
    Returns:
        float: 検証済み浮動小数点数
    
    Raises:
        InvalidInputException: 値が範囲外の場合
    """
    if not isinstance(value, (int, float)):
        try:
            value = float(value)
        except (ValueError, TypeError):
            raise InvalidInputException(
                field_name,
                str(value),
                "Must be a number"
            )
    
    if min_value is not None and value < min_value:
        raise InvalidInputException(
            field_name,
            str(value),
            f"Too small (min: {min_value})"
        )
    
    if max_value is not None and value > max_value:
        raise InvalidInputException(
            field_name,
            str(value),
            f"Too large (max: {max_value})"
        )
    
    return float(value)


def validate_choice(
    value: str,
    field_name: str,
    choices: list[str]
) -> str:
    """
    選択肢の検証
    
    Args:
        value: 検証する値
        field_name: フィールド名
        choices: 有効な選択肢のリスト
    
    Returns:
        str: 検証済み値
    
    Raises:
        InvalidInputException: 無効な選択肢の場合
    """
    if value not in choices:
        raise InvalidInputException(
            field_name,
            value,
            f"Must be one of: {', '.join(choices)}"
        )
    
    return value


def validate_phone_number(phone: str, field_name: str = "phone") -> str:
    """
    電話番号の検証（日本の形式）
    
    Args:
        phone: 電話番号
        field_name: フィールド名
    
    Returns:
        str: 正規化された電話番号（ハイフンなし）
    
    Raises:
        InvalidInputException: 無効な電話番号の場合
    """
    if not phone:
        return ""
    
    # ハイフンとスペースを除去
    phone = phone.strip().replace("-", "").replace(" ", "").replace("　", "")
    
    # 数字のみかチェック
    if not phone.isdigit():
        raise InvalidInputException(
            field_name,
            phone,
            "Phone number must contain only digits"
        )
    
    # 日本の電話番号は10桁または11桁
    if len(phone) not in [10, 11]:
        raise InvalidInputException(
            field_name,
            phone,
            "Phone number must be 10 or 11 digits"
        )
    
    return phone


def validate_postal_code(postal_code: str, field_name: str = "postal_code") -> str:
    """
    郵便番号の検証（日本の形式）
    
    Args:
        postal_code: 郵便番号
        field_name: フィールド名
    
    Returns:
        str: 正規化された郵便番号（ハイフンなし）
    
    Raises:
        InvalidInputException: 無効な郵便番号の場合
    """
    if not postal_code:
        return ""
    
    # ハイフンを除去
    postal_code = postal_code.strip().replace("-", "")
    
    # 数字のみかチェック
    if not postal_code.isdigit():
        raise InvalidInputException(
            field_name,
            postal_code,
            "Postal code must contain only digits"
        )
    
    # 日本の郵便番号は7桁
    if len(postal_code) != 7:
        raise InvalidInputException(
            field_name,
            postal_code,
            "Postal code must be 7 digits"
        )
    
    return postal_code


# 開発用: バリデーションテスト
if __name__ == "__main__":
    print("=== Validation Tests ===\n")
    
    # メールアドレステスト
    try:
        email = validate_email("test@example.com")
        print(f"✓ Valid email: {email}")
    except Exception as e:
        print(f"✗ Email validation failed: {e}")
    
    # 文字列長テスト
    try:
        name = validate_string_length("田中太郎", "name", max_length=100)
        print(f"✓ Valid name: {name}")
    except Exception as e:
        print(f"✗ Name validation failed: {e}")
    
    # 整数範囲テスト
    try:
        capacity = validate_integer_range(5, "capacity", min_value=0, max_value=100)
        print(f"✓ Valid capacity: {capacity}")
    except Exception as e:
        print(f"✗ Capacity validation failed: {e}")
    
    # 電話番号テスト
    try:
        phone = validate_phone_number("090-1234-5678")
        print(f"✓ Valid phone: {phone}")
    except Exception as e:
        print(f"✗ Phone validation failed: {e}")
    
    # 郵便番号テスト
    try:
        postal = validate_postal_code("123-4567")
        print(f"✓ Valid postal code: {postal}")
    except Exception as e:
        print(f"✗ Postal code validation failed: {e}")
    
    print("\n=== Error Tests ===\n")
    
    # 無効なメール
    try:
        validate_email("invalid-email")
    except InvalidInputException as e:
        print(f"✓ Caught invalid email: {e}")
    
    # 範囲外の整数
    try:
        validate_integer_range(150, "capacity", max_value=100)
    except InvalidInputException as e:
        print(f"✓ Caught out of range: {e}")
