"""
GA遺伝操作（交叉、突然変異）
"""
import random
from typing import List, Tuple, Dict
from ga.fitness import FitnessContext
from utils.logger import get_logger

logger = get_logger(__name__)


def crossover_two_point(ind1: List[int], ind2: List[int]) -> Tuple[List[int], List[int]]:
    """
    二点交叉

    Args:
        ind1: 親個体1
        ind2: 親個体2

    Returns:
        Tuple[List[int], List[int]]: 子個体のタプル
    """
    size = len(ind1)
    if size < 2:
        return ind1[:], ind2[:]

    cxpoint1 = random.randint(1, size - 1)
    cxpoint2 = random.randint(1, size - 1)

    if cxpoint2 < cxpoint1:
        cxpoint1, cxpoint2 = cxpoint2, cxpoint1

    child1 = ind1[:cxpoint1] + ind2[cxpoint1:cxpoint2] + ind1[cxpoint2:]
    child2 = ind2[:cxpoint1] + ind1[cxpoint1:cxpoint2] + ind2[cxpoint2:]

    return child1, child2


def crossover_uniform(ind1: List[int], ind2: List[int], indpb: float = 0.5) -> Tuple[List[int], List[int]]:
    """
    一様交叉

    Args:
        ind1: 親個体1
        ind2: 親個体2
        indpb: 各遺伝子の交換確率

    Returns:
        Tuple[List[int], List[int]]: 子個体のタプル
    """
    child1 = ind1[:]
    child2 = ind2[:]

    for i in range(len(ind1)):
        if random.random() < indpb:
            child1[i], child2[i] = child2[i], child1[i]

    return child1, child2


def mutate_random(individual: List[int], num_hospitals: int, indpb: float = 0.1) -> Tuple[List[int],]:
    """
    ランダム突然変異

    各遺伝子を一定確率でランダムな病院に変更

    Args:
        individual: 個体
        num_hospitals: 病院数
        indpb: 各遺伝子の変異確率

    Returns:
        Tuple[List[int],]: 変異後の個体（タプル形式）
    """
    for i in range(len(individual)):
        if random.random() < indpb:
            individual[i] = random.randint(0, num_hospitals - 1)

    return (individual,)


def mutate_swap(individual: List[int], indpb: float = 0.1) -> Tuple[List[int],]:
    """
    スワップ突然変異

    2つの遺伝子をランダムに交換

    Args:
        individual: 個体
        indpb: 変異確率

    Returns:
        Tuple[List[int],]: 変異後の個体（タプル形式）
    """
    size = len(individual)
    if size < 2:
        return (individual,)

    if random.random() < indpb:
        i, j = random.sample(range(size), 2)
        individual[i], individual[j] = individual[j], individual[i]

    return (individual,)


def mutate_capacity_aware(
    individual: List[int],
    context: FitnessContext,
    indpb: float = 0.1
) -> Tuple[List[int],]:
    """
    定員を考慮した突然変異

    定員超過している病院への割り当てを、空きのある病院に変更

    Args:
        individual: 個体
        context: フィットネスコンテキスト
        indpb: 変異確率

    Returns:
        Tuple[List[int],]: 変異後の個体（タプル形式）
    """
    if random.random() > indpb:
        return (individual,)

    # 病院ごとの割り当て数をカウント
    hospital_count: Dict[int, int] = {}
    for hospital_idx in individual:
        hospital_count[hospital_idx] = hospital_count.get(hospital_idx, 0) + 1

    # 定員超過している病院を特定
    overcapacity_hospitals = []
    undercapacity_hospitals = []

    for idx, hospital in enumerate(context.hospitals):
        current = hospital_count.get(idx, 0)
        capacity = context.hospital_capacities.get(hospital.id, 0)

        if current > capacity:
            overcapacity_hospitals.append(idx)
        elif current < capacity:
            undercapacity_hospitals.append(idx)

    if not overcapacity_hospitals or not undercapacity_hospitals:
        return (individual,)

    # 定員超過している病院に割り当てられている専攻医を見つけて、空きのある病院に移動
    for i, hospital_idx in enumerate(individual):
        if hospital_idx in overcapacity_hospitals and undercapacity_hospitals:
            # 空きのある病院にランダムに移動
            new_hospital_idx = random.choice(undercapacity_hospitals)
            individual[i] = new_hospital_idx

            # カウントを更新
            hospital_count[hospital_idx] -= 1
            hospital_count[new_hospital_idx] = hospital_count.get(new_hospital_idx, 0) + 1

            # リストを更新
            if hospital_count[hospital_idx] <= context.hospital_capacities.get(
                context.hospitals[hospital_idx].id, 0
            ):
                overcapacity_hospitals.remove(hospital_idx)

            if hospital_count[new_hospital_idx] >= context.hospital_capacities.get(
                context.hospitals[new_hospital_idx].id, 0
            ):
                undercapacity_hospitals.remove(new_hospital_idx)

            break  # 1回の変異で1つだけ移動

    return (individual,)


def mutate_hope_aware(
    individual: List[int],
    context: FitnessContext,
    indpb: float = 0.1
) -> Tuple[List[int],]:
    """
    希望を考慮した突然変異

    希望外の病院に割り当てられている専攻医を、希望病院に移動させる試み

    Args:
        individual: 個体
        context: フィットネスコンテキスト
        indpb: 変異確率

    Returns:
        Tuple[List[int],]: 変異後の個体（タプル形式）
    """
    if random.random() > indpb:
        return (individual,)

    for i, resident in enumerate(context.residents):
        current_hospital_idx = individual[i]
        current_hospital_id = context.hospitals[current_hospital_idx].id

        # 希望を取得
        choices = context.hospital_choices.get(resident.id, {})

        # 現在の割り当てが希望外かチェック
        is_in_hope = any(h_id == current_hospital_id for h_id in choices.values())

        if not is_in_hope and choices:
            # 希望病院のインデックスを取得
            hope_hospital_ids = list(choices.values())
            hope_hospital_idxs = [
                context.hospital_id_to_idx[h_id]
                for h_id in hope_hospital_ids
                if h_id in context.hospital_id_to_idx
            ]

            if hope_hospital_idxs:
                # ランダムに希望病院を選択
                individual[i] = random.choice(hope_hospital_idxs)
                break  # 1回の変異で1人だけ

    return (individual,)


def select_tournament(population: List, k: int, tournsize: int = 3) -> List:
    """
    トーナメント選択

    Args:
        population: 集団
        k: 選択する個体数
        tournsize: トーナメントサイズ

    Returns:
        List: 選択された個体のリスト
    """
    selected = []

    for _ in range(k):
        aspirants = random.sample(population, min(tournsize, len(population)))
        winner = max(aspirants, key=lambda ind: ind.fitness.values[0])
        selected.append(winner)

    return selected
