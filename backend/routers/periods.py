"""期間API"""
from fastapi import APIRouter
from datetime import datetime
from typing import List
from schemas import PeriodOption

router = APIRouter(prefix="/api/periods", tags=["periods"])


def generate_periods(start_year: int = 2015, end_year: int = None) -> List[PeriodOption]:
    """期間選択肢を生成"""
    if end_year is None:
        end_year = datetime.now().year + 2  # 2年先まで

    periods = []
    for year in range(start_year, end_year + 1):
        for q in range(1, 5):
            value = f"{year}Q{q}"
            months = {1: "4-6月", 2: "7-9月", 3: "10-12月", 4: "1-3月"}
            label = f"{year}年度 Q{q} ({months[q]})"
            periods.append(PeriodOption(value=value, label=label))

    return periods


@router.get("", response_model=List[PeriodOption])
def get_periods():
    """期間選択肢取得"""
    return generate_periods()


@router.get("/current")
def get_current_period():
    """現在の期間を取得"""
    now = datetime.now()
    year = now.year
    month = now.month

    # 4月始まりの年度計算
    if month >= 4:
        fiscal_year = year
        if month <= 6:
            q = 1
        elif month <= 9:
            q = 2
        else:
            q = 3
    else:
        fiscal_year = year - 1
        if month <= 3:
            q = 4
        else:
            q = 1

    return {"value": f"{fiscal_year}Q{q}", "fiscal_year": fiscal_year, "quarter": q}
