"""Pydanticスキーマ定義"""
from pydantic import BaseModel
from typing import Optional, List


# ===== 職員 =====
class StaffBase(BaseModel):
    last_name: str
    first_name: str
    last_name_kana: Optional[str] = None
    first_name_kana: Optional[str] = None
    position: str
    email: Optional[str] = None
    phone: Optional[str] = None
    join_year: Optional[int] = None
    address: Optional[str] = None
    evaluation_memo: Optional[str] = None


class StaffCreate(StaffBase):
    pass


class StaffUpdate(StaffBase):
    pass


class StaffResponse(StaffBase):
    id: int
    display_name: str

    class Config:
        from_attributes = True


# ===== 病院 =====
class HospitalBase(BaseModel):
    name: str
    address: Optional[str] = None
    capacity: int = 0
    allows_external: bool = True


class HospitalCreate(HospitalBase):
    pass


class HospitalUpdate(HospitalBase):
    pass


class HospitalResponse(HospitalBase):
    id: int

    class Config:
        from_attributes = True


# ===== 外勤病院 =====
class ExternalHospitalBase(BaseModel):
    name: str
    address: Optional[str] = None


class ExternalHospitalCreate(ExternalHospitalBase):
    pass


class ExternalHospitalUpdate(ExternalHospitalBase):
    pass


class ExternalHospitalResponse(ExternalHospitalBase):
    id: int

    class Config:
        from_attributes = True


# ===== 経歴 =====
class CareerBase(BaseModel):
    staff_id: int
    period: str
    hospital_id: Optional[int] = None
    hospital_name_manual: Optional[str] = None
    notes: Optional[str] = None


class CareerCreate(CareerBase):
    pass


class CareerUpdate(CareerBase):
    pass


class CareerResponse(CareerBase):
    id: int
    hospital_display: str

    class Config:
        from_attributes = True


# ===== 外勤登録 =====
class ExternalWorkBase(BaseModel):
    staff_id: int
    external_hospital_id: int
    day_of_week: str
    time_slot: str
    frequency: str
    period: str


class ExternalWorkCreate(ExternalWorkBase):
    pass


class ExternalWorkUpdate(ExternalWorkBase):
    pass


class ExternalWorkResponse(ExternalWorkBase):
    id: int

    class Config:
        from_attributes = True


# ===== 外勤一括登録（表形式）=====
class ExternalWorkSlot(BaseModel):
    """1コマ分の外勤設定"""
    day_of_week: str
    time_slot: str
    external_hospital_id: Optional[int] = None
    frequency: Optional[str] = None


class ExternalWorkBulkUpdate(BaseModel):
    """外勤一括更新（職員側）"""
    staff_id: int
    period: str
    slots: List[ExternalWorkSlot]


class ExternalWorkByHospitalSlot(BaseModel):
    """病院側の1コマ"""
    day_of_week: str
    time_slot: str
    staff_id: Optional[int] = None
    frequency: Optional[str] = None


class ExternalWorkByHospitalUpdate(BaseModel):
    """外勤一括更新（病院側）"""
    external_hospital_id: int
    period: str
    slots: List[ExternalWorkByHospitalSlot]


# ===== 選択肢 =====
class StaffOption(BaseModel):
    """職員選択肢"""
    id: int
    display_name: str  # 山田（太）


class PeriodOption(BaseModel):
    """期間選択肢"""
    value: str  # "2024Q1"
    label: str  # "2024年度 Q1 (4-6月)"
