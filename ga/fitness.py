"""
GA適合度（フィットネス）関数
"""
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from database.base import SessionLocal
from database.models.staff import Staff
from database.models.hospital import Hospital
from repositories.hospital_choice_repository import HospitalChoiceRepository
from repositories.staff_factor_weight_repository import StaffFactorWeightRepository
from repositories.admin_evaluation_repository import AdminEvaluationRepository
from repositories.commute_cache_repository import CommuteCacheRepository
from repositories.evaluation_factor_repository import EvaluationFactorRepository
from config.constants import FactorType
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class FitnessContext:
    """フィットネス計算に必要なコンテキストデータ"""
    # 専攻医リスト
    residents: List[Staff]
    # 病院リスト
    hospitals: List[Hospital]
    # 病院ID→インデックスのマップ
    hospital_id_to_idx: Dict[int, int]
    # 専攻医ID→インデックスのマップ
    resident_id_to_idx: Dict[int, int]
    # 年度
    fiscal_year: int
    # 各専攻医の病院希望 {staff_id: {rank: hospital_id}}
    hospital_choices: Dict[int, Dict[int, int]]
    # 各専攻医の要素重み {staff_id: {factor_id: weight}}
    staff_weights: Dict[int, Dict[int, float]]
    # 医局側評価 {staff_id: {factor_id: value}}
    admin_evaluations: Dict[int, Dict[int, float]]
    # 通勤時間キャッシュ {(staff_id, hospital_id): minutes}
    commute_cache: Dict[Tuple[int, int], float]
    # 専攻医重視要素リスト
    staff_factors: List[dict]
    # 医局側評価要素リスト
    admin_factors: List[dict]
    # 病院の受入定員
    hospital_capacities: Dict[int, int]
    # 設定
    mismatch_bonus: float = 1.5


def load_fitness_context(fiscal_year: int, residents: List[Staff], hospitals: List[Hospital]) -> FitnessContext:
    """
    フィットネス計算に必要なコンテキストを読み込む

    Args:
        fiscal_year: 年度
        residents: 専攻医リスト
        hospitals: 病院リスト

    Returns:
        FitnessContext: コンテキストデータ
    """
    with SessionLocal() as db:
        # マップ作成
        hospital_id_to_idx = {h.id: i for i, h in enumerate(hospitals)}
        resident_id_to_idx = {r.id: i for i, r in enumerate(residents)}

        # 病院希望を読み込み
        choice_repo = HospitalChoiceRepository(db)
        hospital_choices = {}
        for resident in residents:
            hospital_choices[resident.id] = choice_repo.get_choices_as_dict(
                resident.id, fiscal_year
            )

        # 専攻医の要素重みを読み込み
        weight_repo = StaffFactorWeightRepository(db)
        staff_weights = {}
        for resident in residents:
            staff_weights[resident.id] = weight_repo.get_weights_as_dict(
                resident.id, fiscal_year
            )

        # 医局側評価を読み込み
        eval_repo = AdminEvaluationRepository(db)
        admin_evaluations = {}
        for resident in residents:
            admin_evaluations[resident.id] = eval_repo.get_evaluations_as_dict(
                resident.id, fiscal_year
            )

        # 通勤時間キャッシュを読み込み
        commute_repo = CommuteCacheRepository(db)
        commute_cache = {}
        for resident in residents:
            for hospital in hospitals:
                cache = commute_repo.get_by_staff_and_hospital(resident.id, hospital.id)
                if cache:
                    commute_cache[(resident.id, hospital.id)] = float(cache.driving_time_minutes or 0)

        # 評価要素を読み込み
        factor_repo = EvaluationFactorRepository(db)
        staff_factors = [
            {"id": f.id, "name": f.name}
            for f in factor_repo.get_staff_preference_factors()
        ]
        admin_factors = [
            {"id": f.id, "name": f.name}
            for f in factor_repo.get_admin_evaluation_factors()
        ]

        # 病院の受入定員
        hospital_capacities = {h.id: h.resident_capacity for h in hospitals}

    return FitnessContext(
        residents=residents,
        hospitals=hospitals,
        hospital_id_to_idx=hospital_id_to_idx,
        resident_id_to_idx=resident_id_to_idx,
        fiscal_year=fiscal_year,
        hospital_choices=hospital_choices,
        staff_weights=staff_weights,
        admin_evaluations=admin_evaluations,
        commute_cache=commute_cache,
        staff_factors=staff_factors,
        admin_factors=admin_factors,
        hospital_capacities=hospital_capacities
    )


def calculate_fitness(individual: List[int], context: FitnessContext) -> Tuple[float,]:
    """
    個体の適合度を計算

    個体は [hospital_idx_for_resident_0, hospital_idx_for_resident_1, ...] の形式

    適合度の計算:
    1. 希望順位スコア（第1希望=1.0, 第2希望=0.66, 第3希望=0.33, 希望外=0）
    2. 専攻医の重視要素スコア（正規化された重みで加重平均）
    3. 医局側評価スコア（評価値の平均）
    4. 定員制約ペナルティ

    Args:
        individual: 個体（病院インデックスの配列）
        context: フィットネスコンテキスト

    Returns:
        Tuple[float,]: 適合度（タプル形式、DEAPの要件）
    """
    total_score = 0.0
    num_residents = len(context.residents)

    if num_residents == 0:
        return (0.0,)

    # 病院ごとの割り当て数をカウント
    hospital_assignment_count: Dict[int, int] = {}
    for hospital_idx in individual:
        hospital_id = context.hospitals[hospital_idx].id
        hospital_assignment_count[hospital_id] = hospital_assignment_count.get(hospital_id, 0) + 1

    for i, resident in enumerate(context.residents):
        hospital_idx = individual[i]
        hospital = context.hospitals[hospital_idx]

        resident_score = 0.0

        # 1. 希望順位スコア
        hope_score = calculate_hope_score(resident.id, hospital.id, context)
        resident_score += hope_score * 0.4  # 40%の重み

        # 2. 専攻医の重視要素スコア
        preference_score = calculate_preference_score(resident.id, hospital, context)
        resident_score += preference_score * 0.3  # 30%の重み

        # 3. 医局側評価スコア
        admin_score = calculate_admin_score(resident.id, context)
        resident_score += admin_score * 0.3  # 30%の重み

        total_score += resident_score

    # 4. 定員制約ペナルティ
    capacity_penalty = 0.0
    for hospital_id, count in hospital_assignment_count.items():
        capacity = context.hospital_capacities.get(hospital_id, 0)
        if count > capacity:
            # 超過した分だけペナルティ
            capacity_penalty += (count - capacity) * 0.5

    total_score -= capacity_penalty

    # 正規化（0-1の範囲に）
    normalized_score = total_score / num_residents if num_residents > 0 else 0.0

    return (max(0.0, normalized_score),)


def calculate_hope_score(staff_id: int, hospital_id: int, context: FitnessContext) -> float:
    """
    希望順位スコアを計算

    Args:
        staff_id: 専攻医ID
        hospital_id: 病院ID
        context: コンテキスト

    Returns:
        float: スコア（0.0-1.0）
    """
    choices = context.hospital_choices.get(staff_id, {})

    for rank, h_id in choices.items():
        if h_id == hospital_id:
            # 第1希望=1.0, 第2希望=0.66, 第3希望=0.33
            return 1.0 - (rank - 1) * 0.33

    # 希望外
    return 0.0


def calculate_preference_score(staff_id: int, hospital: Hospital, context: FitnessContext) -> float:
    """
    専攻医の重視要素スコアを計算

    要素例：
    - 年収: 病院の年収を正規化
    - 通勤時間: 通勤時間を逆正規化（短いほど高スコア）
    - 症例数: 病院の受入数を代理指標として使用（将来的に拡張可能）

    Args:
        staff_id: 専攻医ID
        hospital: 病院
        context: コンテキスト

    Returns:
        float: スコア（0.0-1.0）
    """
    weights = context.staff_weights.get(staff_id, {})

    if not weights:
        return 0.5  # デフォルト

    total_weighted_score = 0.0
    total_weight = sum(weights.values())

    if total_weight == 0:
        return 0.5

    for factor in context.staff_factors:
        factor_id = factor["id"]
        factor_name = factor["name"].lower()
        weight = weights.get(factor_id, 0)

        if weight == 0:
            continue

        # 要素名に基づいてスコアを計算
        factor_score = 0.5  # デフォルト

        if "年収" in factor_name or "給与" in factor_name or "salary" in factor_name:
            # 年収スコア（最大1000万を基準に正規化）
            salary = float(hospital.annual_salary or 0)
            factor_score = min(1.0, salary / 10000000) if salary > 0 else 0.5

        elif "通勤" in factor_name or "距離" in factor_name or "commute" in factor_name:
            # 通勤時間スコア（60分を基準に逆正規化）
            commute_time = context.commute_cache.get((staff_id, hospital.id), 60)
            factor_score = max(0.0, 1.0 - commute_time / 120) if commute_time > 0 else 0.5

        elif "症例" in factor_name or "外勤" in factor_name:
            # 外勤・症例数は病院の総受入数を代理指標として使用
            capacity = hospital.total_capacity
            factor_score = min(1.0, capacity / 20) if capacity > 0 else 0.5

        # 重みで加重
        normalized_weight = weight / total_weight
        total_weighted_score += factor_score * normalized_weight

    return total_weighted_score


def calculate_admin_score(staff_id: int, context: FitnessContext) -> float:
    """
    医局側評価スコアを計算

    Args:
        staff_id: 専攻医ID
        context: コンテキスト

    Returns:
        float: スコア（0.0-1.0）
    """
    evaluations = context.admin_evaluations.get(staff_id, {})

    if not evaluations:
        return 0.5  # デフォルト

    # 全評価の平均
    values = list(evaluations.values())
    return sum(values) / len(values) if values else 0.5
