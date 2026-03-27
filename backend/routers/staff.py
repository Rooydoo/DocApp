"""職員API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Staff, Hospital
from schemas import StaffCreate, StaffUpdate, StaffResponse, StaffOption

router = APIRouter(prefix="/api/staff", tags=["staff"])


@router.get("", response_model=List[StaffResponse])
def get_all_staff(db: Session = Depends(get_db)):
    """職員一覧取得"""
    staff_list = db.query(Staff).order_by(Staff.last_name_kana, Staff.first_name_kana).all()
    return staff_list


@router.get("/options", response_model=List[StaffOption])
def get_staff_options(external_allowed_only: bool = False, db: Session = Depends(get_db)):
    """職員選択肢取得（プルダウン用）"""
    query = db.query(Staff)

    if external_allowed_only:
        # 外勤可能な病院に配属されている職員のみ
        # TODO: 現在の配置先を見て判定する必要あり
        pass

    staff_list = query.order_by(Staff.last_name_kana, Staff.first_name_kana).all()
    return [{"id": s.id, "display_name": s.display_name} for s in staff_list]


@router.get("/{staff_id}", response_model=StaffResponse)
def get_staff(staff_id: int, db: Session = Depends(get_db)):
    """職員詳細取得"""
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="職員が見つかりません")
    return staff


@router.post("", response_model=StaffResponse)
def create_staff(data: StaffCreate, db: Session = Depends(get_db)):
    """職員登録"""
    staff = Staff(**data.model_dump())
    db.add(staff)
    db.commit()
    db.refresh(staff)
    return staff


@router.put("/{staff_id}", response_model=StaffResponse)
def update_staff(staff_id: int, data: StaffUpdate, db: Session = Depends(get_db)):
    """職員更新"""
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="職員が見つかりません")

    for key, value in data.model_dump().items():
        setattr(staff, key, value)

    db.commit()
    db.refresh(staff)
    return staff


@router.delete("/{staff_id}")
def delete_staff(staff_id: int, db: Session = Depends(get_db)):
    """職員削除"""
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="職員が見つかりません")

    db.delete(staff)
    db.commit()
    return {"message": "削除しました"}
