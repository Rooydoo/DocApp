"""経歴API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Career
from schemas import CareerCreate, CareerUpdate, CareerResponse

router = APIRouter(prefix="/api/careers", tags=["careers"])


@router.get("", response_model=List[CareerResponse])
def get_all_careers(staff_id: int = None, db: Session = Depends(get_db)):
    """経歴一覧取得"""
    query = db.query(Career)
    if staff_id:
        query = query.filter(Career.staff_id == staff_id)
    return query.order_by(Career.period.desc()).all()


@router.get("/{career_id}", response_model=CareerResponse)
def get_career(career_id: int, db: Session = Depends(get_db)):
    """経歴詳細取得"""
    career = db.query(Career).filter(Career.id == career_id).first()
    if not career:
        raise HTTPException(status_code=404, detail="経歴が見つかりません")
    return career


@router.post("", response_model=CareerResponse)
def create_career(data: CareerCreate, db: Session = Depends(get_db)):
    """経歴登録"""
    career = Career(**data.model_dump())
    db.add(career)
    db.commit()
    db.refresh(career)
    return career


@router.put("/{career_id}", response_model=CareerResponse)
def update_career(career_id: int, data: CareerUpdate, db: Session = Depends(get_db)):
    """経歴更新"""
    career = db.query(Career).filter(Career.id == career_id).first()
    if not career:
        raise HTTPException(status_code=404, detail="経歴が見つかりません")

    for key, value in data.model_dump().items():
        setattr(career, key, value)

    db.commit()
    db.refresh(career)
    return career


@router.delete("/{career_id}")
def delete_career(career_id: int, db: Session = Depends(get_db)):
    """経歴削除"""
    career = db.query(Career).filter(Career.id == career_id).first()
    if not career:
        raise HTTPException(status_code=404, detail="経歴が見つかりません")

    db.delete(career)
    db.commit()
    return {"message": "削除しました"}
