"""外勤API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import ExternalWork, Staff, ExternalHospital
from schemas import (
    ExternalWorkCreate, ExternalWorkResponse,
    ExternalWorkBulkUpdate, ExternalWorkByHospitalUpdate
)

router = APIRouter(prefix="/api/external-works", tags=["external-works"])

# 定数
DAYS_OF_WEEK = ["月", "火", "水", "木", "金"]
TIME_SLOTS = ["午前", "午後"]
FREQUENCIES = ["毎週", "第1週", "第2週", "第3週", "第4週", "第1,3週", "第2,4週"]
MAX_EXTERNAL_SLOTS = 3


@router.get("/constants")
def get_constants():
    """定数取得"""
    return {
        "days_of_week": DAYS_OF_WEEK,
        "time_slots": TIME_SLOTS,
        "frequencies": FREQUENCIES,
        "max_slots": MAX_EXTERNAL_SLOTS
    }


@router.get("", response_model=List[ExternalWorkResponse])
def get_external_works(
    staff_id: int = None,
    external_hospital_id: int = None,
    period: str = None,
    db: Session = Depends(get_db)
):
    """外勤一覧取得"""
    query = db.query(ExternalWork)
    if staff_id:
        query = query.filter(ExternalWork.staff_id == staff_id)
    if external_hospital_id:
        query = query.filter(ExternalWork.external_hospital_id == external_hospital_id)
    if period:
        query = query.filter(ExternalWork.period == period)
    return query.all()


@router.get("/by-staff/{staff_id}/{period}")
def get_external_works_by_staff(staff_id: int, period: str, db: Session = Depends(get_db)):
    """職員の外勤表取得（表形式用）"""
    works = db.query(ExternalWork).filter(
        ExternalWork.staff_id == staff_id,
        ExternalWork.period == period
    ).all()

    # 10枠のグリッドに変換
    grid = {}
    for day in DAYS_OF_WEEK:
        for slot in TIME_SLOTS:
            key = f"{day}_{slot}"
            grid[key] = None

    for work in works:
        key = f"{work.day_of_week}_{work.time_slot}"
        grid[key] = {
            "external_hospital_id": work.external_hospital_id,
            "frequency": work.frequency
        }

    return {"staff_id": staff_id, "period": period, "grid": grid}


@router.get("/by-hospital/{external_hospital_id}/{period}")
def get_external_works_by_hospital(external_hospital_id: int, period: str, db: Session = Depends(get_db)):
    """外勤病院の外勤表取得（表形式用）"""
    works = db.query(ExternalWork).filter(
        ExternalWork.external_hospital_id == external_hospital_id,
        ExternalWork.period == period
    ).all()

    # 10枠のグリッドに変換（複数人可能）
    grid = {}
    for day in DAYS_OF_WEEK:
        for slot in TIME_SLOTS:
            key = f"{day}_{slot}"
            grid[key] = []

    for work in works:
        key = f"{work.day_of_week}_{work.time_slot}"
        staff = db.query(Staff).filter(Staff.id == work.staff_id).first()
        grid[key].append({
            "staff_id": work.staff_id,
            "staff_display_name": staff.display_name if staff else "",
            "frequency": work.frequency
        })

    return {"external_hospital_id": external_hospital_id, "period": period, "grid": grid}


@router.post("/bulk-update-by-staff")
def bulk_update_by_staff(data: ExternalWorkBulkUpdate, db: Session = Depends(get_db)):
    """外勤一括更新（職員側）"""
    # 既存データ削除
    db.query(ExternalWork).filter(
        ExternalWork.staff_id == data.staff_id,
        ExternalWork.period == data.period
    ).delete()

    # 新規登録
    count = 0
    for slot in data.slots:
        if slot.external_hospital_id and slot.frequency:
            if count >= MAX_EXTERNAL_SLOTS:
                raise HTTPException(status_code=400, detail=f"外勤は最大{MAX_EXTERNAL_SLOTS}コマまでです")
            work = ExternalWork(
                staff_id=data.staff_id,
                external_hospital_id=slot.external_hospital_id,
                day_of_week=slot.day_of_week,
                time_slot=slot.time_slot,
                frequency=slot.frequency,
                period=data.period
            )
            db.add(work)
            count += 1

    db.commit()
    return {"message": f"{count}件の外勤を登録しました"}


@router.post("/bulk-update-by-hospital")
def bulk_update_by_hospital(data: ExternalWorkByHospitalUpdate, db: Session = Depends(get_db)):
    """外勤一括更新（病院側）"""
    # 既存データ削除
    db.query(ExternalWork).filter(
        ExternalWork.external_hospital_id == data.external_hospital_id,
        ExternalWork.period == data.period
    ).delete()

    # 新規登録
    for slot in data.slots:
        if slot.staff_id and slot.frequency:
            # 職員の外勤上限チェック
            existing_count = db.query(ExternalWork).filter(
                ExternalWork.staff_id == slot.staff_id,
                ExternalWork.period == data.period,
                ExternalWork.external_hospital_id != data.external_hospital_id
            ).count()

            if existing_count >= MAX_EXTERNAL_SLOTS:
                staff = db.query(Staff).filter(Staff.id == slot.staff_id).first()
                raise HTTPException(
                    status_code=400,
                    detail=f"{staff.display_name}は既に{MAX_EXTERNAL_SLOTS}コマの外勤があります"
                )

            work = ExternalWork(
                staff_id=slot.staff_id,
                external_hospital_id=data.external_hospital_id,
                day_of_week=slot.day_of_week,
                time_slot=slot.time_slot,
                frequency=slot.frequency,
                period=data.period
            )
            db.add(work)

    db.commit()
    return {"message": "外勤を登録しました"}
