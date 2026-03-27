"""病院API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Hospital
from schemas import HospitalCreate, HospitalUpdate, HospitalResponse

router = APIRouter(prefix="/api/hospitals", tags=["hospitals"])


@router.get("", response_model=List[HospitalResponse])
def get_all_hospitals(db: Session = Depends(get_db)):
    """病院一覧取得"""
    return db.query(Hospital).order_by(Hospital.name).all()


@router.get("/{hospital_id}", response_model=HospitalResponse)
def get_hospital(hospital_id: int, db: Session = Depends(get_db)):
    """病院詳細取得"""
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="病院が見つかりません")
    return hospital


@router.post("", response_model=HospitalResponse)
def create_hospital(data: HospitalCreate, db: Session = Depends(get_db)):
    """病院登録"""
    hospital = Hospital(**data.model_dump())
    db.add(hospital)
    db.commit()
    db.refresh(hospital)
    return hospital


@router.put("/{hospital_id}", response_model=HospitalResponse)
def update_hospital(hospital_id: int, data: HospitalUpdate, db: Session = Depends(get_db)):
    """病院更新"""
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="病院が見つかりません")

    for key, value in data.model_dump().items():
        setattr(hospital, key, value)

    db.commit()
    db.refresh(hospital)
    return hospital


@router.delete("/{hospital_id}")
def delete_hospital(hospital_id: int, db: Session = Depends(get_db)):
    """病院削除"""
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="病院が見つかりません")

    db.delete(hospital)
    db.commit()
    return {"message": "削除しました"}
