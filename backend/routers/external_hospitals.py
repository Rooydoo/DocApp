"""外勤病院API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import ExternalHospital
from schemas import ExternalHospitalCreate, ExternalHospitalUpdate, ExternalHospitalResponse

router = APIRouter(prefix="/api/external-hospitals", tags=["external-hospitals"])


@router.get("", response_model=List[ExternalHospitalResponse])
def get_all_external_hospitals(db: Session = Depends(get_db)):
    """外勤病院一覧取得"""
    return db.query(ExternalHospital).order_by(ExternalHospital.name).all()


@router.get("/{hospital_id}", response_model=ExternalHospitalResponse)
def get_external_hospital(hospital_id: int, db: Session = Depends(get_db)):
    """外勤病院詳細取得"""
    hospital = db.query(ExternalHospital).filter(ExternalHospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="外勤病院が見つかりません")
    return hospital


@router.post("", response_model=ExternalHospitalResponse)
def create_external_hospital(data: ExternalHospitalCreate, db: Session = Depends(get_db)):
    """外勤病院登録"""
    hospital = ExternalHospital(**data.model_dump())
    db.add(hospital)
    db.commit()
    db.refresh(hospital)
    return hospital


@router.put("/{hospital_id}", response_model=ExternalHospitalResponse)
def update_external_hospital(hospital_id: int, data: ExternalHospitalUpdate, db: Session = Depends(get_db)):
    """外勤病院更新"""
    hospital = db.query(ExternalHospital).filter(ExternalHospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="外勤病院が見つかりません")

    for key, value in data.model_dump().items():
        setattr(hospital, key, value)

    db.commit()
    db.refresh(hospital)
    return hospital


@router.delete("/{hospital_id}")
def delete_external_hospital(hospital_id: int, db: Session = Depends(get_db)):
    """外勤病院削除"""
    hospital = db.query(ExternalHospital).filter(ExternalHospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="外勤病院が見つかりません")

    db.delete(hospital)
    db.commit()
    return {"message": "削除しました"}
